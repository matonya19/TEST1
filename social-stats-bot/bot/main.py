"""Точка входа: python -m bot.main [--dry-run] [--demo] [--no-ai]"""
from __future__ import annotations

import argparse
import logging
import os
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv

from . import analysis, instagram, report, storage, telegram, tiktok, youtube
from .models import AccountStats, Video

ROOT = Path(__file__).resolve().parent.parent
HISTORY = ROOT / "data" / "history.json"
log = logging.getLogger("social-stats-bot")


def env(name: str, default: str | None = None) -> str | None:
    v = os.getenv(name)
    return v.strip() if v and v.strip() else default


def collect() -> list[AccountStats]:
    jobs = []
    if env("YOUTUBE_API_KEY") and env("YOUTUBE_CHANNEL"):
        jobs.append(("youtube", lambda: youtube.fetch(env("YOUTUBE_API_KEY"), env("YOUTUBE_CHANNEL"))))
    if env("INSTAGRAM_ACCESS_TOKEN"):
        jobs.append(("instagram", lambda: instagram.fetch(
            env("INSTAGRAM_ACCESS_TOKEN"), env("INSTAGRAM_USER_ID"),
            env("INSTAGRAM_API_HOST"), env("INSTAGRAM_API_VERSION", "v23.0"))))
    if env("TIKTOK_CLIENT_KEY") and env("TIKTOK_REFRESH_TOKEN"):
        jobs.append(("tiktok", lambda: tiktok.fetch(
            env("TIKTOK_CLIENT_KEY"), env("TIKTOK_CLIENT_SECRET", ""), env("TIKTOK_REFRESH_TOKEN"))))
    if not jobs:
        raise SystemExit("Не настроена ни одна платформа — заполните .env (см. .env.example)")

    accounts = []
    for platform, fn in jobs:
        try:
            accounts.append(fn())
            log.info("%s: ok (%d роликов)", platform, len(accounts[-1].videos))
        except Exception as e:  # одна упавшая платформа не должна ломать весь отчёт
            log.exception("%s: ошибка", platform)
            accounts.append(AccountStats(platform=platform, name="", error=str(e)))
    return accounts


def demo_accounts() -> list[AccountStats]:
    """Фейковые данные, чтобы посмотреть отчёт без ключей API."""
    rnd = random.Random(42)
    now = datetime.now(timezone.utc)
    topics = ["3 ошибки новичков в продажах", "Как я делегировал отдел за месяц",
              "День из жизни собственника", "Почему сотрудники увольняются",
              "Скрипт звонка, который работает", "Ответ хейтеру", "Мой утренний распорядок",
              "Сколько стоит открыть бизнес", "Разбор кейса подписчика", "Не нанимайте друзей"]
    accounts = []
    for platform, name, base in [("youtube", "@demo_channel", 3000),
                                 ("instagram", "@demo_insta", 5000),
                                 ("tiktok", "@demo_tt", 8000)]:
        vids = []
        for i in range(15):
            views = int(base * rnd.uniform(0.5, 1.6))
            if i in (1, 6):
                views *= rnd.randint(4, 9)
            vids.append(Video(
                platform=platform, id=f"{platform}{i}", title=topics[i % len(topics)],
                url=f"https://example.com/{platform}/{i}",
                published_at=now - timedelta(days=i * 2 + 1, hours=rnd.randint(0, 12)),
                views=views, likes=int(views * rnd.uniform(0.03, 0.09)),
                comments=int(views * rnd.uniform(0.002, 0.01)),
                shares=int(views * rnd.uniform(0.002, 0.03)) if platform != "youtube" else 0,
                saves=int(views * rnd.uniform(0.005, 0.03)) if platform == "instagram" else 0,
                duration_sec=rnd.randint(15, 60), media_type="reels/video",
            ))
        accounts.append(AccountStats(platform=platform, name=name,
                                     followers=base * 4 + rnd.randint(0, 999), videos=vids))
    return accounts


def main() -> None:
    p = argparse.ArgumentParser(description="Еженедельный отчёт по YouTube / Instagram / TikTok")
    p.add_argument("--dry-run", action="store_true", help="напечатать отчёт, не отправлять и не сохранять историю")
    p.add_argument("--demo", action="store_true", help="использовать фейковые данные")
    p.add_argument("--no-ai", action="store_true", help="без анализа Claude")
    args = p.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    load_dotenv(ROOT / ".env")

    history = [] if args.demo else storage.load(HISTORY)
    accounts = demo_accounts() if args.demo else collect()

    analysis.compute(
        accounts, history,
        multiplier=float(env("VIRAL_MULTIPLIER", "2.0")),
        min_views=int(env("VIRAL_MIN_VIEWS", "1000")),
        lookback_days=int(env("LOOKBACK_DAYS", "30")),
    )

    ai_text = None
    if not args.no_ai and env("ANTHROPIC_API_KEY"):
        ai_text = analysis.explain_with_claude(accounts, env("CLAUDE_MODEL", "claude-opus-5-5"))
    elif not args.no_ai:
        log.warning("ANTHROPIC_API_KEY не задан — отчёт без разбора причин")

    text = report.build(accounts, ai_text, datetime.now())

    if args.dry_run or args.demo:
        print(text)
        return
    telegram.send(env("TELEGRAM_BOT_TOKEN"), env("TELEGRAM_CHAT_ID"), text)
    storage.save(HISTORY, history, accounts)
    log.info("Отчёт отправлен")


if __name__ == "__main__":
    main()
