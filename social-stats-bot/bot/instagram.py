"""Instagram Graph API (профессиональный аккаунт: Business или Creator).

Работает с обоими вариантами:
  * Instagram API with Instagram Login  -> host graph.instagram.com, user_id = me
  * Instagram API with Facebook Login   -> host graph.facebook.com, user_id = числовой IG ID
"""
from __future__ import annotations

from datetime import datetime

import requests

from .models import AccountStats, Video

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


def fetch(token: str, user_id: str = "me", host: str = "graph.instagram.com",
          version: str = "v23.0", max_media: int = 30) -> AccountStats:
    c = Client(token, host, version)
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
