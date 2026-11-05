"""TikTok Display API v2 (scopes: user.info.basic, user.info.stats, video.list)."""
from __future__ import annotations

import logging
from datetime import datetime, timezone

import requests

from .models import AccountStats, Video

API = "https://open.tiktokapis.com/v2"
log = logging.getLogger(__name__)


def refresh_access_token(client_key: str, client_secret: str, refresh_token: str) -> dict:
    r = requests.post(f"{API}/oauth/token/", timeout=30, data={
        "client_key": client_key,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }, headers={"Content-Type": "application/x-www-form-urlencoded"})
    data = r.json()
    if not r.ok or "access_token" not in data:
        raise RuntimeError(f"TikTok token refresh: {r.status_code} {str(data)[:300]}")
    if data.get("refresh_token") and data["refresh_token"] != refresh_token:
        log.warning("TikTok выдал новый refresh_token — обновите секрет TIKTOK_REFRESH_TOKEN "
                    "(старый ещё действует, но со временем истечёт).")
    return data


def _check(r: requests.Response, what: str) -> dict:
    data = r.json() if r.content else {}
    err = (data.get("error") or {}).get("code")
    if not r.ok or (err and err != "ok"):
        raise RuntimeError(f"TikTok {what}: {r.status_code} {str(data)[:300]}")
    return data.get("data", {})


def fetch(client_key: str, client_secret: str, refresh_token: str,
          max_videos: int = 40) -> AccountStats:
    token = refresh_access_token(client_key, client_secret, refresh_token)["access_token"]
    h = {"Authorization": f"Bearer {token}"}

    user = _check(requests.get(
        f"{API}/user/info/", headers=h, timeout=30,
        params={"fields": "open_id,display_name,username,follower_count,likes_count,video_count"},
    ), "user/info")["user"]

    fields = ("id,title,video_description,create_time,share_url,duration,"
              "view_count,like_count,comment_count,share_count")
    videos: list[Video] = []
    cursor = None
    while len(videos) < max_videos:
        body = {"max_count": 20}
        if cursor:
            body["cursor"] = cursor
        data = _check(requests.post(f"{API}/video/list/", headers=h, json=body,
                                    params={"fields": fields}, timeout=30), "video/list")
        for v in data.get("videos", []):
            videos.append(Video(
                platform="tiktok",
                id=v["id"],
                title=(v.get("title") or v.get("video_description") or "").strip()[:300],
                url=v.get("share_url", ""),
                published_at=datetime.fromtimestamp(v["create_time"], tz=timezone.utc),
                views=int(v.get("view_count", 0)),
                likes=int(v.get("like_count", 0)),
                comments=int(v.get("comment_count", 0)),
                shares=int(v.get("share_count", 0)),
                duration_sec=v.get("duration"),
                media_type="video",
            ))
        if not data.get("has_more"):
            break
        cursor = data.get("cursor")

    return AccountStats(
        platform="tiktok",
        name="@" + (user.get("username") or user.get("display_name", "")),
        followers=user.get("follower_count"),
        total_likes=user.get("likes_count"),
        media_count=user.get("video_count"),
        videos=videos[:max_videos],
    )
