"""История снимков: нужна, чтобы считать прирост за неделю."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .models import AccountStats

KEEP_RUNS = 26  # ~полгода еженедельных отчётов


def load(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8")).get("runs", [])


def last_snapshot(runs: list[dict], platform: str) -> dict | None:
    for run in reversed(runs):
        if platform in run.get("platforms", {}):
            return run["platforms"][platform]
    return None


def save(path: Path, runs: list[dict], accounts: list[AccountStats]) -> None:
    snap = {"date": datetime.now(timezone.utc).isoformat(timespec="seconds"), "platforms": {}}
    for a in accounts:
        if a.error:
            continue
        snap["platforms"][a.platform] = {
            "followers": a.followers,
            "total_views": a.total_views,
            "total_likes": a.total_likes,
            "videos": {v.id: v.views for v in a.videos},
        }
    runs = (runs + [snap])[-KEEP_RUNS:]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"runs": runs}, ensure_ascii=False, indent=1), encoding="utf-8")
