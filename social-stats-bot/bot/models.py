from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Video:
    platform: str
    id: str
    title: str
    url: str
    published_at: datetime
    views: int
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    duration_sec: int | None = None
    media_type: str = ""
    # Доп. метрики платформы (reach, среднее время просмотра и т.п.)
    extra: dict = field(default_factory=dict)

    # Заполняется в analysis.py
    views_gained_week: int | None = None
    score: float | None = None  # во сколько раз больше медианы
    is_viral: bool = False

    @property
    def interactions(self) -> int:
        return self.likes + self.comments + self.shares + self.saves

    @property
    def engagement_rate(self) -> float:
        return self.interactions / self.views if self.views else 0.0


@dataclass
class AccountStats:
    platform: str
    name: str
    followers: int | None = None
    # Суммарные показатели аккаунта, если платформа их отдаёт
    total_views: int | None = None
    total_likes: int | None = None
    media_count: int | None = None
    videos: list[Video] = field(default_factory=list)
    error: str | None = None

    # Заполняется в analysis.py
    followers_delta: int | None = None
    total_views_delta: int | None = None
    total_likes_delta: int | None = None
    median_views: float | None = None
    median_er: float | None = None
