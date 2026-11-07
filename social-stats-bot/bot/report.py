"""Сборка текста отчёта (Telegram HTML)."""
from __future__ import annotations

from datetime import datetime
from html import escape

from .analysis import week_leader
from .models import AccountStats, Video

TITLES = {"youtube": "▶️ YouTube", "instagram": "📸 Instagram", "tiktok": "🎵 TikTok"}
MONTHS = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля",
          "августа", "сентября", "октября", "ноября", "декабря"]


def n(x: float | int | None) -> str:
    if x is None:
        return "—"
    x = int(round(x))
    if abs(x) >= 1_000_000:
        return f"{x / 1_000_000:.1f}".rstrip("0").rstrip(".").replace(".", ",") + " млн"
    if abs(x) >= 10_000:
        return f"{x / 1000:.1f}".rstrip("0").rstrip(".").replace(".", ",") + " тыс"
    return f"{x:,}".replace(",", " ")


def delta(x: int | None) -> str:
    if x is None:
        return ""
    sign = "+" if x > 0 else "−" if x < 0 else "±"
    return f" ({sign}{n(abs(x))} за неделю)"


def _short(title: str, limit: int = 70) -> str:
    t = " ".join(title.split()) or "без подписи"
    return t if len(t) <= limit else t[: limit - 1] + "…"


def _video_line(v: Video) -> str:
    bits = [f"{n(v.views)} просм."]
    if v.score:
        bits.append(f"×{v.score:.1f} к медиане")
    bits.append(f"ER {v.engagement_rate * 100:.1f}%")
    if v.shares:
        bits.append(f"{n(v.shares)} репостов")
    if v.saves:
        bits.append(f"{n(v.saves)} сохр.")
    return f'<a href="{escape(v.url, quote=True)}">{escape(_short(v.title))}</a> — ' + ", ".join(bits)


def account_block(a: AccountStats) -> str:
    head = f"<b>{TITLES.get(a.platform, a.platform)}</b> · {escape(a.name)}"
    if a.error:
        return f"{head}\n⚠️ Не удалось получить данные: {escape(a.error[:200])}"

    lines = [head]
    if a.followers is not None:
        lines.append(f"👥 Подписчики: {n(a.followers)}{delta(a.followers_delta)}")
    if a.total_views_delta is not None:
        lines.append(f"👁 Просмотры канала за неделю: +{n(a.total_views_delta)}")
    else:
        gained = sum(v.views_gained_week or 0 for v in a.videos)
        if gained:
            lines.append(f"👁 Просмотры роликов за неделю: ≈ +{n(gained)}")
    if a.total_likes_delta is not None:
        lines.append(f"❤️ Лайков за неделю: +{n(a.total_likes_delta)}")

    week_new = [v for v in a.videos if (datetime.now(v.published_at.tzinfo) - v.published_at).days < 7]
    lines.append(f"🆕 Новых роликов за неделю: {len(week_new)}")
    lines.append(f"📏 Медиана: {n(a.median_views)} просм., ER {(a.median_er or 0) * 100:.1f}%")

    viral = sorted((v for v in a.videos if v.is_viral), key=lambda v: v.views, reverse=True)
    if viral:
        lines.append("🔥 <b>Залетело:</b>")
        lines += [f"• {_video_line(v)}" for v in viral[:5]]
    leader = week_leader(a)
    if leader and leader not in viral[:5]:
        lines.append(f"🏆 Лидер недели: {_video_line(leader)} (+{n(leader.views_gained_week)} за неделю)")
    if not viral and not leader:
        lines.append("Залетевших роликов нет.")
    return "\n".join(lines)


def build(accounts: list[AccountStats], ai_text: str | None, today: datetime) -> str:
    parts = [f"📊 <b>Отчёт по соцсетям · {today.day} {MONTHS[today.month - 1]} {today.year}</b>"]
    parts += [account_block(a) for a in accounts]
    if ai_text:
        parts.append("🧠 <b>Почему залетело</b>\n" + escape(ai_text))
    return "\n\n".join(parts)
