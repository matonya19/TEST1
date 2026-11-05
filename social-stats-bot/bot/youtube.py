"""YouTube Data API v3: публичная статистика канала и последних роликов."""
from __future__ import annotations

import re
from datetime import datetime

import requests

from .models import AccountStats, Video

API = "https://www.googleapis.com/youtube/v3"


def _get(path: str, **params) -> dict:
    r = requests.get(f"{API}/{path}", params=params, timeout=30)
    if not r.ok:
        raise RuntimeError(f"YouTube {path}: {r.status_code} {r.text[:300]}")
    return r.json()


def _parse_duration(iso: str) -> int:
    m = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    if not m:
        return 0
    d, h, mi, s = (int(x or 0) for x in m.groups())
    return d * 86400 + h * 3600 + mi * 60 + s


def fetch(api_key: str, channel: str, max_videos: int = 30) -> AccountStats:
    params = {"part": "snippet,statistics,contentDetails", "key": api_key}
    if channel.startswith("@"):
        params["forHandle"] = channel
    else:
        params["id"] = channel
    items = _get("channels", **params).get("items") or []
    if not items:
        raise RuntimeError(f"YouTube: канал {channel!r} не найден")
    ch = items[0]
    st = ch["statistics"]
    uploads = ch["contentDetails"]["relatedPlaylists"]["uploads"]

    ids = [
        it["contentDetails"]["videoId"]
        for it in _get(
            "playlistItems", part="contentDetails", playlistId=uploads,
            maxResults=min(max_videos, 50), key=api_key,
        ).get("items", [])
    ]

    videos: list[Video] = []
    if ids:
        data = _get("videos", part="snippet,statistics,contentDetails",
                    id=",".join(ids), key=api_key)
        for v in data.get("items", []):
            s = v.get("statistics", {})
            dur = _parse_duration(v["contentDetails"].get("duration", ""))
            videos.append(Video(
                platform="youtube",
                id=v["id"],
                title=v["snippet"]["title"],
                url=(f"https://youtube.com/shorts/{v['id']}" if dur <= 180
                     else f"https://youtu.be/{v['id']}"),
                published_at=datetime.fromisoformat(v["snippet"]["publishedAt"].replace("Z", "+00:00")),
                views=int(s.get("viewCount", 0)),
                likes=int(s.get("likeCount", 0)),
                comments=int(s.get("commentCount", 0)),
                duration_sec=dur,
                media_type="short" if dur <= 180 else "video",
                extra={"tags": v["snippet"].get("tags", [])[:10],
                       "description": (v["snippet"].get("description") or "")[:300]},
            ))

    return AccountStats(
        platform="youtube",
        name=ch["snippet"].get("customUrl") or ch["snippet"]["title"],
        followers=None if st.get("hiddenSubscriberCount") else int(st.get("subscriberCount", 0)),
        total_views=int(st.get("viewCount", 0)),
        media_count=int(st.get("videoCount", 0)),
        videos=videos,
    )
