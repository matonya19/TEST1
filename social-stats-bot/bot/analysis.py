"""Поиск «залетевших» роликов и разбор причин через Claude."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone
from statistics import median

import anthropic

from .models import AccountStats, Video
from .storage import last_snapshot

log = logging.getLogger(__name__)

WEEKDAYS = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"]


def _delta(new, old):
    return new - old if new is not None and old is not None else None


def compute(accounts: list[AccountStats], history: list[dict], *,
            multiplier: float, min_views: int, lookback_days: int) -> None:
    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)
    lookback = now - timedelta(days=lookback_days)

    for a in accounts:
        if a.error:
            continue
        prev = last_snapshot(history, a.platform) or {}
        a.followers_delta = _delta(a.followers, prev.get("followers"))
        a.total_views_delta = _delta(a.total_views, prev.get("total_views"))
        a.total_likes_delta = _delta(a.total_likes, prev.get("total_likes"))
        prev_views = prev.get("videos", {})

        for v in a.videos:
            if v.id in prev_views:
                v.views_gained_week = v.views - prev_views[v.id]
            elif v.published_at >= week_ago or prev:
                # Новый ролик (или его не было в прошлом снимке) — весь прирост за неделю
                v.views_gained_week = v.views

        # Медиану считаем по роликам старше 3 дней, чтобы свежие не занижали базу
        mature = [v for v in a.videos if v.published_at <= now - timedelta(days=3)] or a.videos
        a.median_views = median(v.views for v in mature) if mature else 0
        a.median_er = median(v.engagement_rate for v in mature) if mature else 0

        for v in a.videos:
            v.score = v.views / a.median_views if a.median_views else None
            v.is_viral = bool(
                v.published_at >= lookback
                and v.views >= min_views
                and v.score is not None and v.score >= multiplier
            )


def week_leader(a: AccountStats) -> Video | None:
    cands = [v for v in a.videos if v.views_gained_week]
    return max(cands, key=lambda v: v.views_gained_week, default=None)


def _video_row(v: Video) -> dict:
    row = {
        "title_or_caption": v.title,
        "url": v.url,
        "format": v.media_type,
        "published": f"{v.published_at:%Y-%m-%d %H:%M} UTC ({WEEKDAYS[v.published_at.weekday()]})",
        "duration_sec": v.duration_sec,
        "views": v.views,
        "views_gained_this_week": v.views_gained_week,
        "x_median": round(v.score, 2) if v.score else None,
        "likes": v.likes, "comments": v.comments, "shares": v.shares, "saves": v.saves,
        "engagement_rate_pct": round(v.engagement_rate * 100, 2),
        "viral": v.is_viral,
    }
    row.update(v.extra)
    return {k: val for k, val in row.items() if val not in (None, "", [])}


SYSTEM = """Ты — аналитик коротких видео для Instagram Reels, TikTok и YouTube.
Тебе дают еженедельную статистику автора. Твоя задача — объяснить, почему отдельные ролики
«залетели» (набрали в разы больше медианы аккаунта), и дать практичные выводы.

Как анализировать:
- Сравнивай залетевшие ролики с обычными роликами того же аккаунта: тема, формулировка
  заголовка/подписи (хук), длительность, формат, день и время публикации, соотношение
  лайков/комментариев/репостов/сохранений, среднее время просмотра (если есть).
- Высокие репосты и сохранения обычно означают полезный или «пересылаемый» контент,
  много комментариев — спорную или вовлекающую тему, высокий ER при малом охвате —
  ролик хорош, но его мало показали.
- Опирайся только на данные. Видео ты не смотришь — поэтому говори о гипотезах
  («скорее всего», «похоже»), а не о фактах. Не выдумывай содержание роликов.
- Если залетевших роликов нет — скажи, какой ролик недели был лучшим и чего не хватило.

Формат ответа: обычный текст на русском, без markdown-разметки (без *, #, таблиц),
можно эмодзи и короткие списки через «•». Структура:
1) По каждому залетевшему ролику: название (коротко) и 2–4 причины.
2) «Общие закономерности» — что объединяет удачные ролики.
3) «Что сделать на этой неделе» — 3 конкретных рекомендации.
Пиши ёмко, весь ответ — не больше 2500 символов."""


def explain_with_claude(accounts: list[AccountStats], model: str) -> str | None:
    payload = []
    for a in accounts:
        if a.error or not a.videos:
            continue
        top = sorted(a.videos, key=lambda v: v.views, reverse=True)[:12]
        payload.append({
            "platform": a.platform,
            "account": a.name,
            "followers": a.followers,
            "followers_change_week": a.followers_delta,
            "median_views_per_video": a.median_views,
            "median_engagement_rate_pct": round((a.median_er or 0) * 100, 2),
            "videos_top_by_views": [_video_row(v) for v in top],
        })
    if not payload:
        return None

    client = anthropic.Anthropic()
    try:
        resp = client.beta.messages.create(
            model=model,
            max_tokens=16000,
            system=SYSTEM,
            thinking={"type": "adaptive"},
            output_config={"effort": "medium"},
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            messages=[{"role": "user", "content":
                       "Статистика за неделю (JSON):\n"
                       + json.dumps(payload, ensure_ascii=False, indent=1)}],
        )
    except anthropic.APIError as e:
        log.error("Claude API error: %s", e)
        return None
    if resp.stop_reason == "refusal":
        log.warning("Claude отказался анализировать данные")
        return None
    return "\n".join(b.text for b in resp.content if b.type == "text").strip() or None
