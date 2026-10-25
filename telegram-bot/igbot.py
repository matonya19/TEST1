"""Instagram-автоответчик по кодовому слову (через Composio).

Каждые несколько минут проверяет новые комментарии под свежими публикациями и новые сообщения в директе.
Если в тексте есть кодовое слово (по умолчанию «генетика»):
  • комментарий → пробует отправить человеку сообщение в директ («ответ в личку на комментарий»)
    и отвечает под комментарием;
  • сообщение в директ → отвечает в директ ссылкой на Telegram-бота.
Каждому человеку отвечает не чаще раза в сутки. Старые комментарии и сообщения (до первого запуска) не трогает.

Запуск: python igbot.py          — работать постоянно
        python igbot.py --check  — проверить ключ и найти аккаунт, ничего не отправляя
"""

import logging
import os
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("COMPOSIO_API_KEY", "").strip().strip("\"'").removeprefix("COMPOSIO_API_KEY=")
IG_USERNAME = os.environ.get("IG_USERNAME", "doc.perepelitsa").lstrip("@").lower()
KEYWORD = os.environ.get("IG_KEYWORD", "генетика")
TG_BOT_USERNAME = os.environ.get("TG_BOT_USERNAME", "dnk_system_perepelitca_bot").lstrip("@")
POLL_SECONDS = int(os.environ.get("IG_POLL_SECONDS", "240"))
MEDIA_DAYS = int(os.environ.get("IG_MEDIA_DAYS", "14"))  # комментарии смотрим только под публикациями за N дней
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
ASSISTANT_CHAT_ID = os.environ.get("ASSISTANT_CHAT_ID", "")

BASE = "https://backend.composio.dev/api/v3"
GRAPH_VERSION = "v21.0"
DB_PATH = Path(__file__).parent / "igbot.db"
DAY = 24 * 3600

LINK = f"https://t.me/{TG_BOT_USERNAME}?start=instagram"
DM_TEXT = (
    "Здравствуйте! Это Наталья 🙂 Спасибо за интерес к генетике!\n\n"
    "Всё о программе «ДНК-здоровье» — что показывает тест, как он проходит и сколько стоит — "
    f"я собрала в Telegram-боте 👉 {LINK}\n\n"
    "Там же можно задать вопрос или оставить заявку — мой ассистент ответит лично."
)
COMMENT_REPLY_SENT = "Отправила вам подробности в директ 💌"
COMMENT_REPLY_ASK_DM = f"Напишите мне в директ слово «{KEYWORD}» — пришлю подробности 💌"

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger("igbot")


# ---------- Composio ----------

class Composio:
    def __init__(self, api_key: str):
        self.http = httpx.Client(headers={"x-api-key": api_key}, timeout=60)
        self.account_id = ""

    def execute(self, slug: str, arguments: dict) -> dict:
        r = self.http.post(
            f"{BASE}/tools/execute/{slug}",
            json={"connected_account_id": self.account_id, "arguments": arguments},
        )
        payload = r.json() if r.content else {}
        if r.status_code >= 400 or not payload.get("successful", False):
            raise RuntimeError(f"{slug}: HTTP {r.status_code} {payload.get('error') or payload}")
        data = payload.get("data") or {}
        # Ответы Instagram часто завёрнуты дважды: {"data": {"data": [...], "paging": ...}}
        return data

    def proxy(self, method: str, endpoint: str, body: dict) -> tuple[int, dict]:
        r = self.http.post(
            f"{BASE}/tools/execute/proxy",
            json={"endpoint": endpoint, "method": method, "connected_account_id": self.account_id, "body": body},
        )
        payload = r.json() if r.content else {}
        status = payload.get("status") or r.status_code
        return int(status), payload

    def instagram_accounts(self) -> list[dict]:
        r = self.http.get(f"{BASE}/connected_accounts", params={"toolkit_slugs": "instagram", "limit": 50})
        r.raise_for_status()
        return [a for a in r.json().get("items", []) if str(a.get("status", "")).upper() == "ACTIVE"]

    def find_account(self, username: str) -> dict:
        """Находит подключённый аккаунт Instagram с нужным именем. Возвращает данные профиля."""
        for acc in self.instagram_accounts():
            self.account_id = acc["id"]
            try:
                info = self.execute("INSTAGRAM_GET_USER_INFO", {"ig_user_id": "me", "fields": "id,user_id,username"})
            except Exception as e:  # noqa: BLE001 — один сломанный аккаунт не должен мешать искать остальные
                log.warning("Аккаунт %s не отвечает: %s", acc["id"], e)
                continue
            log.info("Найден подключённый аккаунт: @%s", info.get("username"))
            if str(info.get("username", "")).lower() == username:
                return info
        raise RuntimeError(f"В Composio нет активного подключения Instagram @{username}")


def items(data: dict) -> list:
    inner = data.get("data", data)
    return inner if isinstance(inner, list) else []


# ---------- состояние ----------

def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);
        CREATE TABLE IF NOT EXISTS handled (id TEXT PRIMARY KEY, ts REAL);
        CREATE TABLE IF NOT EXISTS replied_users (user_id TEXT PRIMARY KEY, ts REAL);
        CREATE TABLE IF NOT EXISTS media_counts (media_id TEXT PRIMARY KEY, comments INTEGER);
        """
    )
    return conn


def started_at() -> float:
    with db() as conn:
        row = conn.execute("SELECT value FROM meta WHERE key = 'started'").fetchone()
        if row:
            return float(row[0])
        now = time.time()
        conn.execute("INSERT INTO meta VALUES ('started', ?)", (str(now),))
        return now


def is_handled(item_id: str) -> bool:
    with db() as conn:
        return conn.execute("SELECT 1 FROM handled WHERE id = ?", (item_id,)).fetchone() is not None


def mark_handled(item_id: str) -> None:
    with db() as conn:
        conn.execute("INSERT OR IGNORE INTO handled VALUES (?, ?)", (item_id, time.time()))


def recently_replied(user_id: str) -> bool:
    with db() as conn:
        row = conn.execute("SELECT ts FROM replied_users WHERE user_id = ?", (user_id,)).fetchone()
    return bool(row and time.time() - row[0] < DAY)


def mark_replied(user_id: str) -> None:
    with db() as conn:
        conn.execute("INSERT OR REPLACE INTO replied_users VALUES (?, ?)", (user_id, time.time()))


# ---------- логика ----------

def has_keyword(text: str | None) -> bool:
    norm = (text or "").lower().replace("ё", "е")
    return KEYWORD.lower().replace("ё", "е")[:-1] in norm  # «генетик» ловит и «генетика», и «генетику»


def ts(value: str) -> float:
    return datetime.fromisoformat(value.replace("+0000", "+00:00")).timestamp()


def notify_assistant(text: str) -> None:
    if not (TELEGRAM_BOT_TOKEN and ASSISTANT_CHAT_ID):
        return
    try:
        httpx.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": ASSISTANT_CHAT_ID, "text": text},
            timeout=20,
        )
    except httpx.HTTPError as e:
        log.warning("Не удалось уведомить ассистента: %s", e)


def handle_comment(api: Composio, comment: dict) -> None:
    author = (comment.get("from") or {}).get("id", "")
    username = (comment.get("from") or {}).get("username") or comment.get("username") or "?"
    dm_sent = False
    if not recently_replied(author):
        status, payload = api.proxy(
            "POST",
            f"/{GRAPH_VERSION}/me/messages",
            {"recipient": {"comment_id": comment["id"]}, "message": {"text": DM_TEXT}},
        )
        dm_sent = 200 <= status < 300 and "error" not in str(payload.get("data", ""))[:200]
        if not dm_sent:
            log.warning("Ответ в личку на комментарий не ушёл (%s): %s", status, str(payload)[:300])
    else:
        dm_sent = True  # уже писали этому человеку сегодня
    reply = COMMENT_REPLY_SENT if dm_sent else COMMENT_REPLY_ASK_DM
    try:
        api.execute("INSTAGRAM_POST_IG_COMMENT_REPLIES", {"ig_comment_id": comment["id"], "message": reply})
    except Exception as e:  # noqa: BLE001
        log.error("Не удалось ответить под комментарием %s: %s", comment["id"], e)
    if dm_sent and author:
        mark_replied(author)
    log.info("Комментарий @%s: директ %s", username, "отправлен" if dm_sent else "не отправлен, попросили написать")
    notify_assistant(
        f"📸 Instagram: @{username} написал(а) «{KEYWORD}» в комментарии — "
        + ("отправила ссылку на бота в директ." if dm_sent else "попросила написать в директ.")
    )


def check_comments(api: Composio, own_id: str, since: float) -> None:
    media = items(api.execute("INSTAGRAM_GET_IG_USER_MEDIA", {
        "ig_user_id": "me", "limit": 15, "fields": "id,timestamp,comments_count",
    }))
    for m in media:
        if time.time() - ts(m["timestamp"]) > MEDIA_DAYS * DAY:
            continue
        count = int(m.get("comments_count") or 0)
        with db() as conn:
            row = conn.execute("SELECT comments FROM media_counts WHERE media_id = ?", (m["id"],)).fetchone()
            conn.execute("INSERT OR REPLACE INTO media_counts VALUES (?, ?)", (m["id"], count))
        if row is not None and row[0] == count:
            continue  # новых комментариев нет — не тратим запрос
        comments = items(api.execute("INSTAGRAM_GET_IG_MEDIA_COMMENTS", {
            "ig_media_id": m["id"], "limit": 50, "fields": "id,text,timestamp,from,username",
        }))
        for c in comments:
            if is_handled(c["id"]):
                continue
            mark_handled(c["id"])
            author = (c.get("from") or {}).get("id")
            if ts(c["timestamp"]) < since or author == own_id or not has_keyword(c.get("text")):
                continue
            handle_comment(api, c)


def check_direct(api: Composio, own_id: str, since: float) -> None:
    convs = items(api.execute("INSTAGRAM_LIST_ALL_CONVERSATIONS", {
        "limit": 20, "fields": "id,updated_time,messages.limit(3){id,message,from,created_time}",
    }))
    for conv in convs:
        if ts(conv["updated_time"]) < since:
            continue
        for msg in (conv.get("messages") or {}).get("data", []):
            sender = (msg.get("from") or {})
            if sender.get("id") == own_id:
                break  # дальше идут сообщения старше нашего ответа
            if is_handled(msg["id"]):
                break
            mark_handled(msg["id"])
            if ts(msg["created_time"]) < since or not has_keyword(msg.get("message")):
                continue
            if recently_replied(sender["id"]):
                break
            try:
                api.execute("INSTAGRAM_SEND_TEXT_MESSAGE", {"recipient_id": sender["id"], "text": DM_TEXT})
                mark_replied(sender["id"])
                log.info("Директ @%s: ответ отправлен", sender.get("username"))
                notify_assistant(f"📸 Instagram: @{sender.get('username')} написал(а) «{KEYWORD}» в директ — "
                                 "отправила ссылку на бота.")
            except Exception as e:  # noqa: BLE001
                log.error("Не удалось ответить в директ @%s: %s", sender.get("username"), e)
            break


def main() -> None:
    if not API_KEY:
        sys.exit("COMPOSIO_API_KEY не задан — Instagram-автоответчик не запущен.")
    api = Composio(API_KEY)
    info = api.find_account(IG_USERNAME)
    own_id = str(info.get("user_id") or info.get("id"))
    if "--check" in sys.argv:
        print(f"OK: найден @{info.get('username')}, автоответчик готов к работе.")
        return
    try:
        # Без этой подписки Instagram не даёт приложению отвечать в директ («outside of allowed window»).
        api.execute("INSTAGRAM_ENABLE_WEBHOOK_SUBSCRIPTIONS", {"subscribed_fields": ["messages", "comments"]})
    except Exception as e:  # noqa: BLE001
        log.warning("Не удалось включить подписку на сообщения: %s", e)
    since = started_at()
    log.info("Автоответчик запущен для @%s, слово «%s», проверка каждые %s с", IG_USERNAME, KEYWORD, POLL_SECONDS)
    while True:
        for step in (check_comments, check_direct):
            try:
                step(api, own_id, since)
            except Exception as e:  # noqa: BLE001 — сбой одной проверки не должен останавливать автоответчик
                log.error("%s: %s", step.__name__, e)
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
