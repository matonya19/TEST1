"""Instagram-бот, который отвечает клиентам Натальи Перепелицы в директ с помощью Claude."""

import hashlib
import hmac
import logging
import os
import sqlite3
import time
from pathlib import Path

import anthropic
import httpx
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse

load_dotenv()

VERIFY_TOKEN = os.environ["IG_VERIFY_TOKEN"]
APP_SECRET = os.environ["IG_APP_SECRET"]
ACCESS_TOKEN = os.environ["IG_ACCESS_TOKEN"]
GRAPH_URL = os.getenv("IG_GRAPH_URL", "https://graph.instagram.com/v21.0")
MODEL = os.getenv("CLAUDE_MODEL", "claude-opus-5-5")
HISTORY_LIMIT = 20  # сколько последних сообщений диалога передавать модели
HUMAN_PAUSE_SECONDS = int(os.getenv("HUMAN_PAUSE_HOURS", "12")) * 3600
IG_TEXT_LIMIT = 1000  # максимальная длина одного сообщения в Instagram

BASE_DIR = Path(__file__).parent
KNOWLEDGE = (BASE_DIR / "knowledge.md").read_text(encoding="utf-8")
DB_PATH = BASE_DIR / "conversations.db"

SYSTEM_PROMPT = f"""Ты — помощник Натальи Перепелицы и отвечаешь её клиентам в директе Instagram.

Как отвечать:
- Пиши тепло, вежливо и коротко — как в мессенджере: 1–4 предложения, без markdown, без списков со звёздочками.
- Отвечай на языке клиента (по умолчанию — на русском), обращайся на «вы».
- Опирайся только на сведения ниже. Не придумывай цены, даты, услуги, адреса и обещания, которых там нет.
- Если ответа в сведениях нет, вопрос личный, касается здоровья/денег/жалобы или клиент просит связаться с Натальей —
  скажи, что передашь вопрос Наталье и она ответит лично. Не пытайся решить такой вопрос сам.
- Если клиент хочет записаться или купить — помоги по шагам, описанным в сведениях.
- Не говори, что ты Наталья. Если спросят, кто отвечает, — честно скажи, что ты её виртуальный помощник.

Сведения о Наталье и её услугах:
<knowledge>
{KNOWLEDGE}
</knowledge>"""

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("ig-bot")

claude = anthropic.Anthropic()
app = FastAPI()


def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS messages ("
        "id INTEGER PRIMARY KEY, user_id TEXT, role TEXT, text TEXT, ts REAL)"
    )
    conn.execute("CREATE TABLE IF NOT EXISTS paused (user_id TEXT PRIMARY KEY, until REAL)")
    conn.execute("CREATE TABLE IF NOT EXISTS bot_sent (mid TEXT PRIMARY KEY)")
    return conn


def save_message(user_id: str, role: str, text: str) -> None:
    with db() as conn:
        conn.execute(
            "INSERT INTO messages (user_id, role, text, ts) VALUES (?, ?, ?, ?)",
            (user_id, role, text, time.time()),
        )


def load_history(user_id: str) -> list[dict]:
    with db() as conn:
        rows = conn.execute(
            "SELECT role, text FROM messages WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (user_id, HISTORY_LIMIT),
        ).fetchall()
    # Сливаем подряд идущие сообщения одной роли: API требует чередования user/assistant.
    history: list[dict] = []
    for role, text in reversed(rows):
        if history and history[-1]["role"] == role:
            history[-1]["content"] += "\n" + text
        else:
            history.append({"role": role, "content": text})
    while history and history[0]["role"] != "user":
        history.pop(0)
    return history


def is_paused(user_id: str) -> bool:
    with db() as conn:
        row = conn.execute("SELECT until FROM paused WHERE user_id = ?", (user_id,)).fetchone()
    return bool(row and row[0] > time.time())


def pause(user_id: str) -> None:
    with db() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO paused (user_id, until) VALUES (?, ?)",
            (user_id, time.time() + HUMAN_PAUSE_SECONDS),
        )


def remember_bot_message(mid: str) -> None:
    with db() as conn:
        conn.execute("INSERT OR IGNORE INTO bot_sent (mid) VALUES (?)", (mid,))


def sent_by_bot(mid: str, user_id: str, text: str) -> bool:
    # Эхо может прийти раньше, чем бот сохранит id отправленного сообщения,
    # поэтому дополнительно сверяем текст с последним ответом бота этому клиенту.
    with db() as conn:
        if conn.execute("SELECT 1 FROM bot_sent WHERE mid = ?", (mid,)).fetchone():
            return True
        row = conn.execute(
            "SELECT text FROM messages WHERE user_id = ? AND role = 'assistant' ORDER BY id DESC LIMIT 1",
            (user_id,),
        ).fetchone()
    return bool(row and text and text in row[0])


def generate_reply(user_id: str) -> str | None:
    history = load_history(user_id)
    if not history:
        return None
    try:
        response = claude.beta.messages.create(
            model=MODEL,
            max_tokens=2000,
            system=SYSTEM_PROMPT,
            messages=history,
            output_config={"effort": "low"},
            betas=["server-side-fallback-2026-07-01"],
            extra_body={"fallbacks": "default"},
        )
    except anthropic.RateLimitError:
        log.warning("Claude: превышен лимит запросов")
        return None
    except anthropic.APIStatusError as e:
        log.error("Claude: ошибка API %s: %s", e.status_code, e.message)
        return None
    except anthropic.APIConnectionError:
        log.error("Claude: нет соединения")
        return None

    if response.stop_reason == "refusal":
        return "Спасибо за сообщение! Я передам ваш вопрос Наталье, она ответит вам лично."
    text = "".join(block.text for block in response.content if block.type == "text").strip()
    return text or None


def send_instagram_message(recipient_id: str, text: str) -> None:
    chunks = [text[i : i + IG_TEXT_LIMIT] for i in range(0, len(text), IG_TEXT_LIMIT)]
    for chunk in chunks:
        r = httpx.post(
            f"{GRAPH_URL}/me/messages",
            headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
            json={"recipient": {"id": recipient_id}, "message": {"text": chunk}},
            timeout=30,
        )
        if r.status_code != 200:
            log.error("Instagram: ошибка отправки %s: %s", r.status_code, r.text)
            return
        mid = r.json().get("message_id")
        if mid:
            remember_bot_message(mid)


def handle_incoming(user_id: str, text: str) -> None:
    save_message(user_id, "user", text)
    if is_paused(user_id):
        log.info("Диалог с %s на паузе — отвечает Наталья", user_id)
        return
    reply = generate_reply(user_id)
    if reply:
        save_message(user_id, "assistant", reply)
        send_instagram_message(user_id, reply)


def verify_signature(body: bytes, signature: str | None) -> bool:
    if not signature or not signature.startswith("sha256="):
        return False
    expected = hmac.new(APP_SECRET.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature.removeprefix("sha256="))


@app.get("/webhook")
def verify_webhook(request: Request):
    p = request.query_params
    if p.get("hub.mode") == "subscribe" and p.get("hub.verify_token") == VERIFY_TOKEN:
        return PlainTextResponse(p.get("hub.challenge", ""))
    raise HTTPException(status_code=403)


@app.post("/webhook")
async def receive_webhook(request: Request, background: BackgroundTasks):
    body = await request.body()
    if not verify_signature(body, request.headers.get("X-Hub-Signature-256")):
        raise HTTPException(status_code=403)

    payload = await request.json()
    for entry in payload.get("entry", []):
        for event in entry.get("messaging", []):
            message = event.get("message")
            if not message or message.get("is_deleted"):
                continue
            if message.get("is_echo"):
                # Сообщение ушло с аккаунта Натальи. Если его написала она сама, а не бот,
                # бот замолкает в этом диалоге, чтобы не перебивать её.
                client_id = event["recipient"]["id"]
                if not sent_by_bot(message.get("mid", ""), client_id, message.get("text", "")):
                    pause(client_id)
                continue
            text = message.get("text")
            if text:
                background.add_task(handle_incoming, event["sender"]["id"], text)
            elif message.get("attachments"):
                background.add_task(
                    handle_incoming, event["sender"]["id"], "[клиент прислал фото, видео или голосовое]"
                )
    # Instagram ждёт быстрый ответ 200, иначе будет повторять доставку.
    return {"ok": True}


@app.get("/")
def health():
    return {"status": "ok"}
