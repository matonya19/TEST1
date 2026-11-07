"""Instagram Graph API (профессиональный аккаунт: Business или Creator).

Работает с обоими типами токенов:
  * IGAA…  (Instagram Login)                -> graph.instagram.com, user_id = me
  * EAA…   (Facebook Login / системный пользователь, «Unified login»)
                                             -> graph.facebook.com, числовой IG ID
Хост и ID определяются автоматически, если не заданы явно.
"""
from __future__ import annotations

import logging
from datetime import datetime

import requests

from .models import AccountStats, Video

log = logging.getLogger(__name__)

# Пробуем наборы метрик по очереди: если API отклонит метрику (они меняются
# от версии к версии и зависят от типа публикации), откатываемся к более простому.
METRIC_SETS = {
    "REELS": ["views,reach,saved,shares,total_interactions,ig_reels_avg_watch_time",
              "views,reach,saved,shares", "reach,saved"],
    "VIDEO": ["views,reach,saved,shares,total_interactions", "reach,saved"],
    "FEED": ["views,reach,saved,shares,total_interactions", "reach,saved"],
}


class Client:
    def __init__(self, token: str, host: str, version: str):
        self.token = token
        self.base = f"https://{host}/{version}"

    def get(self, path: str, **params) -> dict:
        params["access_token"] = self.token
        r = requests.get(f"{self.base}/{path}", params=params, timeout=30)
        if not r.ok:
            raise RuntimeError(f"Instagram {path}: {r.status_code} {r.text[:300]}")
        return r.json()


def _insights(c: Client, media_id: str, product: str) -> dict:
    for metrics in METRIC_SETS.get(product, METRIC_SETS["FEED"]):
        try:
            data = c.get(f"{media_id}/insights", metric=metrics).get("data", [])
        except RuntimeError:
            continue
        out = {}
        for m in data:
            vals = m.get("values") or [{}]
            out[m["name"]] = m.get("total_value", {}).get("value", vals[0].get("value", 0))
        return out
    return {}


def detect_host(token: str) -> str:
    return "graph.instagram.com" if token.startswith("IG") else "graph.facebook.com"


def discover_user_id(c: Client) -> str:
    """Ищет ID Instagram-аккаунта, доступного токену Facebook/системного пользователя."""
    found: list[tuple[str, str]] = []
    attempts = [
        ("me/accounts", {"fields": "name,instagram_business_account{id,username}"}),
        ("me/businesses", {"fields": "name,owned_instagram_accounts{id,username},"
                                    "instagram_business_accounts{id,username}"}),
    ]
    for path, params in attempts:
        try:
            data = c.get(path, **params).get("data", [])
        except RuntimeError as e:
            log.info("Instagram: %s недоступно (%s)", path, str(e)[:120])
            continue
        for item in data:
            ig = item.get("instagram_business_account")
            if ig:
                found.append((ig["id"], ig.get("username", "")))
            for edge in ("owned_instagram_accounts", "instagram_business_accounts"):
                for ig in (item.get(edge) or {}).get("data", []):
                    found.append((ig["id"], ig.get("username", "")))
        if found:
            break
    if not found:
        raise RuntimeError("не удалось найти Instagram-аккаунт для этого токена — "
                           "задайте INSTAGRAM_USER_ID вручную")
    uniq = list(dict.fromkeys(found))
    log.info("Instagram: найдены аккаунты %s, используем первый",
             ", ".join(f"@{u} ({i})" for i, u in uniq))
    return uniq[0][0]


def fetch(token: str, user_id: str | None = None, host: str | None = None,
          version: str = "v23.0", max_media: int = 30) -> AccountStats:
    host = host or detect_host(token)
    c = Client(token, host, version)
    if not user_id or (user_id == "me" and host == "graph.facebook.com"):
        user_id = "me" if host == "graph.instagram.com" else discover_user_id(c)
    me = c.get(user_id, fields="username,followers_count,media_count")
    media = c.get(
        f"{user_id}/media", limit=max_media,
        fields="id,caption,media_type,media_product_type,timestamp,permalink,"
               "like_count,comments_count",
    ).get("data", [])

    videos: list[Video] = []
    for m in media:
        product = m.get("media_product_type", "FEED")
        ins = _insights(c, m["id"], product)
        avg_watch = ins.get("ig_reels_avg_watch_time")
        videos.append(Video(
            platform="instagram",
            id=m["id"],
            title=(m.get("caption") or "").strip()[:300],
            url=m.get("permalink", ""),
            published_at=datetime.fromisoformat(m["timestamp"].replace("+0000", "+00:00")),
            views=int(ins.get("views") or ins.get("reach") or 0),
            likes=int(m.get("like_count") or 0),
            comments=int(m.get("comments_count") or 0),
            shares=int(ins.get("shares") or 0),
            saves=int(ins.get("saved") or 0),
            media_type=f"{product.lower()}/{m.get('media_type', '').lower()}",
            extra={k: v for k, v in {
                "reach": ins.get("reach"),
                "avg_watch_time_sec": round(avg_watch / 1000, 1) if avg_watch else None,
            }.items() if v is not None},
        ))

    return AccountStats(
        platform="instagram",
        name="@" + me.get("username", ""),
        followers=me.get("followers_count"),
        media_count=me.get("media_count"),
        videos=videos,
    )
