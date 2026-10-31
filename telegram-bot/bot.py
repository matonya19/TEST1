"""Telegram-бот «ДНК-здоровье» для Натальи Перепелицы.

Кнопочный бот по сценарию из screens.py. Заявки и вопросы клиентов уходят в чат ассистента;
ассистент отвечает клиенту, просто ответив (Reply) на уведомление бота.
"""

import html
import httpx
import logging
import os
import sqlite3
from contextlib import contextmanager
import time
from datetime import time as dtime
from zoneinfo import ZoneInfo
from pathlib import Path

from dotenv import load_dotenv
from telegram import (
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.constants import ParseMode
from telegram.error import Forbidden, TelegramError
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from screens import FOLLOWUPS, MENU, SCREENS

load_dotenv()

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
ASSISTANT_CHAT_ID = int(os.environ.get("ASSISTANT_CHAT_ID") or 0)
ASSISTANT_CONTACT = os.environ.get("ASSISTANT_CONTACT", "")
CONSENT_VERSION = os.environ.get("CONSENT_VERSION", "v1")
DB_PATH = Path(__file__).parent / "bot.db"
MEDIA_DIR = Path(__file__).parent / "media"
DAY = 24 * 3600

LEAD_TYPES = {"LEAD": "program", "LEAD_CHILD": "child", "LEAD_OWN": "existing_test"}
LEAD_TYPE_NAMES = {"program": "программа", "child": "ребёнок", "existing_test": "уже есть тест"}
TOPIC_NAMES = {
    "energy": "энергия, туман в голове",
    "weight": "вес и питание",
    "age": "молодость",
    "vitamins": "витамины",
    "risks": "риски и профилактика",
    "child": "ребёнок",
    "other": "другая тема",
    "edema": "отёки",
    "sport": "тренировки",
    "existing_test": "уже есть тест",
}

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger("dna-bot")


# ---------- база данных ----------

def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, source TEXT,
            topic TEXT, last_screen TEXT, awaiting TEXT, lead_type TEXT,
            price_seen INTEGER DEFAULT 0, followup_consent INTEGER DEFAULT 0, created REAL);
        CREATE TABLE IF NOT EXISTS leads (
            user_id INTEGER PRIMARY KEY, type TEXT, status TEXT, city TEXT, question TEXT,
            consent_at REAL, consent_version TEXT, consent_purpose TEXT, created REAL, updated REAL);
        CREATE TABLE IF NOT EXISTS followups (
            id INTEGER PRIMARY KEY, user_id INTEGER, screen TEXT, due REAL, done INTEGER DEFAULT 0);
        CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, user_id INTEGER, screen TEXT, ts REAL);
        CREATE TABLE IF NOT EXISTS relay (assistant_msg_id INTEGER PRIMARY KEY, user_id INTEGER);
        CREATE TABLE IF NOT EXISTS channel_posts (
            chat_id INTEGER, message_id INTEGER, username TEXT, title TEXT, media_group TEXT, ts REAL,
            PRIMARY KEY (chat_id, message_id));
        """
    )
    return conn


_schema_ready = False


@contextmanager
def db():
    """Соединение с базой, которое всегда закрывается: иначе за сутки копятся открытые файлы
    и SQLite начинает падать с «unable to open database file»."""
    global _schema_ready
    conn = _connect() if not _schema_ready else sqlite3.connect(DB_PATH)
    _schema_ready = True
    if True:
        conn.row_factory = sqlite3.Row
    try:
        with conn:
            yield conn
    finally:
        conn.close()


def get_user(tg_user, source: str | None = None) -> sqlite3.Row:
    with db() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO users (user_id, username, first_name, source, created) VALUES (?, ?, ?, ?, ?)",
            (tg_user.id, tg_user.username, tg_user.first_name, source or "telegram", time.time()),
        )
        conn.execute(
            "UPDATE users SET username = ?, first_name = ? WHERE user_id = ?",
            (tg_user.username, tg_user.first_name, tg_user.id),
        )
        if source:
            conn.execute("UPDATE users SET source = ? WHERE user_id = ?", (source, tg_user.id))
        return conn.execute("SELECT * FROM users WHERE user_id = ?", (tg_user.id,)).fetchone()


def update_user(user_id: int, **fields) -> None:
    cols = ", ".join(f"{k} = ?" for k in fields)
    with db() as conn:
        conn.execute(f"UPDATE users SET {cols} WHERE user_id = ?", (*fields.values(), user_id))


def get_lead(user_id: int) -> sqlite3.Row | None:
    with db() as conn:
        return conn.execute("SELECT * FROM leads WHERE user_id = ?", (user_id,)).fetchone()


def cancel_followups(user_id: int) -> None:
    with db() as conn:
        conn.execute("UPDATE followups SET done = 1 WHERE user_id = ? AND done = 0", (user_id,))


# ---------- уведомления ассистенту ----------

def client_card(user: sqlite3.Row, lead: sqlite3.Row | None) -> str:
    name = html.escape(user["first_name"] or "без имени")
    link = f'<a href="tg://user?id={user["user_id"]}">{name}</a>'
    if user["username"]:
        link += f" (@{html.escape(user['username'])})"
    lines = [
        f"Клиент: {link}",
        f"Источник: {html.escape(user['source'] or '—')}",
        f"Тема: {TOPIC_NAMES.get(user['topic'], '—')}",
        f"Смотрел цену: {'да' if user['price_seen'] else 'нет'}",
    ]
    if lead:
        lines.insert(0, f"Тип заявки: {LEAD_TYPE_NAMES.get(lead['type'], lead['type'])} · статус: {lead['status']}")
        if lead["city"]:
            lines.append(f"Город: {html.escape(lead['city'])}")
    return "\n".join(lines)


async def notify_assistant(context: ContextTypes.DEFAULT_TYPE, user_id: int, title: str, extra: str = "") -> bool:
    """Отправляет уведомление ассистенту. Возвращает False, если отправить не удалось."""
    if not ASSISTANT_CHAT_ID:
        log.error("ASSISTANT_CHAT_ID не задан — уведомление не отправлено")
        return False
    with db() as conn:
        user = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
    text = f"<b>{title}</b>\n{client_card(user, get_lead(user_id))}"
    if extra:
        text += f"\n\n{extra}"
    text += "\n\n<i>Ответьте на это сообщение (Reply) — бот перешлёт ответ клиенту.</i>"
    try:
        msg = await context.bot.send_message(ASSISTANT_CHAT_ID, text, parse_mode=ParseMode.HTML)
    except TelegramError as e:
        log.error("Не удалось уведомить ассистента: %s", e)
        return False
    with db() as conn:
        conn.execute("INSERT OR REPLACE INTO relay VALUES (?, ?)", (msg.message_id, user_id))
    return True


# ---------- экраны ----------

def keyboard(screen_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(label, callback_data=target)] for label, target in SCREENS[screen_id]["buttons"]]
    )


async def run_actions(context: ContextTypes.DEFAULT_TYPE, user_id: int, screen_id: str) -> str:
    """Выполняет действия, связанные с экраном. Может подменить экран (например, на экран ошибки)."""
    screen = SCREENS[screen_id]
    fields: dict = {"last_screen": screen_id, "awaiting": None}
    if "tag" in screen:
        fields["topic"] = screen["tag"]
    if screen_id == "PRICE":
        fields["price_seen"] = 1
    if screen_id in LEAD_TYPES:
        fields["lead_type"] = LEAD_TYPES[screen_id]
    if screen_id == "ASK_TEXT":
        fields["awaiting"] = "question"
    if screen_id == "CITY":
        fields["awaiting"] = "city"
    update_user(user_id, **fields)

    if screen_id == "LEAD_CONFIRM":
        return await create_lead(context, user_id)
    if screen_id == "FOLLOW_YES":
        now = time.time()
        with db() as conn:
            conn.execute("UPDATE users SET followup_consent = 1 WHERE user_id = ?", (user_id,))
            conn.execute("UPDATE followups SET done = 1 WHERE user_id = ? AND done = 0", (user_id,))
            conn.executemany(
                "INSERT INTO followups (user_id, screen, due) VALUES (?, ?, ?)",
                [(user_id, s, now + days * DAY) for s, days in FOLLOWUPS],
            )
    if screen_id == "STOP_FOLLOW":
        update_user(user_id, followup_consent=0)
        cancel_followups(user_id)
    return screen_id


async def create_lead(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> str:
    with db() as conn:
        user = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
        existing = conn.execute("SELECT * FROM leads WHERE user_id = ?", (user_id,)).fetchone()
        lead_type = user["lead_type"] or "program"
        now = time.time()
        if existing:
            conn.execute("UPDATE leads SET type = ?, updated = ? WHERE user_id = ?", (lead_type, now, user_id))
        else:
            conn.execute(
                "INSERT INTO leads (user_id, type, status, consent_at, consent_version, consent_purpose, created, updated)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (user_id, lead_type, "new", now, CONSENT_VERSION,
                 "передача Telegram-контакта ассистенту для связи по программе", now, now),
            )
    title = "🔁 Повторное нажатие «Хочу начать»" if existing else "🆕 Новая заявка"
    if not await notify_assistant(context, user_id, title):
        if not existing:
            with db() as conn:
                conn.execute("DELETE FROM leads WHERE user_id = ?", (user_id,))
        return "LEAD_FAIL"
    cancel_followups(user_id)  # после заявки серия напоминаний не нужна
    return "LEAD_CONFIRM"


DUPLICATE_WINDOW = 3  # секунды: повторный запрос того же экрана за это время — двойное нажатие
last_shown: dict[int, tuple[str, float]] = {}


async def show(update: Update, context: ContextTypes.DEFAULT_TYPE, screen_id: str, chat_id: int | None = None) -> None:
    user_id = update.effective_user.id
    prev_screen, prev_ts = last_shown.get(user_id, ("", 0.0))
    if prev_screen == screen_id and time.time() - prev_ts < DUPLICATE_WINDOW:
        log.info("update %s от %s → экран %s пропущен (повтор)", update.update_id, user_id, screen_id)
        return
    last_shown[user_id] = (screen_id, time.time())
    screen_id = await run_actions(context, user_id, screen_id)
    with db() as conn:
        conn.execute("INSERT INTO events (user_id, screen, ts) VALUES (?, ?, ?)", (user_id, screen_id, time.time()))
    log.info("update %s от %s → экран %s", update.update_id, user_id, screen_id)
    await send_screen(context, chat_id or update.effective_chat.id, screen_id)


PHOTO_CAPTION_LIMIT = 1024  # длиннее Telegram не принимает подпись к фото
photo_ids: dict[str, str] = {}  # после первой загрузки фото Telegram отдаёт id, дальше шлём по нему


async def send_screen(context: ContextTypes.DEFAULT_TYPE, chat_id: int, screen_id: str) -> None:
    screen = SCREENS[screen_id]
    text = screen["text"].format(contact=ASSISTANT_CONTACT or "контакт уточняется")
    photo = screen.get("photo")
    path = MEDIA_DIR / photo if photo else None
    if path and (photo in photo_ids or path.exists()):
        fits = len(text) <= PHOTO_CAPTION_LIMIT
        msg = await context.bot.send_photo(
            chat_id,
            photo_ids.get(photo) or path.read_bytes(),
            caption=text if fits else None,
            reply_markup=keyboard(screen_id) if fits else None,
        )
        photo_ids[photo] = msg.photo[-1].file_id
        if fits:
            return
    await context.bot.send_message(chat_id, text, reply_markup=keyboard(screen_id))


# ---------- обработчики клиента ----------

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Ссылка вида t.me/<бот>?start=instagram сохраняет источник перехода.
    source = context.args[0][:64] if context.args else None
    get_user(update.effective_user, source)
    prev_screen, prev_ts = last_shown.get(update.effective_user.id, ("", 0.0))
    if not (prev_screen == "START" and time.time() - prev_ts < DUPLICATE_WINDOW):
        menu = ReplyKeyboardMarkup([list(MENU)], resize_keyboard=True, is_persistent=True)
        await update.message.reply_text("Меню всегда внизу 👇", reply_markup=menu)
    await show(update, context, "START")


def command(screen_id: str):
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        get_user(update.effective_user)
        await show(update, context, screen_id)
    return handler


async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    get_user(update.effective_user)
    # Неизвестная кнопка — например, из старых сообщений прежнего бота: открываем главное меню.
    await show(update, context, query.data if query.data in SCREENS else "START")


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text.strip()
    user = get_user(update.effective_user)
    if text in MENU:
        await show(update, context, MENU[text])
        return

    if user["awaiting"] == "city":
        with db() as conn:
            conn.execute("UPDATE leads SET city = ?, updated = ? WHERE user_id = ?", (text[:100], time.time(), user["user_id"]))
        ok = await notify_assistant(context, user["user_id"], "📍 Клиент указал город")
        await show(update, context, "CITY_DONE" if ok else "ASK_FAIL")
        return

    # Вопрос: и после кнопки «Написать вопрос», и просто текст — ничего не теряется.
    with db() as conn:
        conn.execute("UPDATE leads SET question = ?, updated = ? WHERE user_id = ?", (text[:2000], time.time(), user["user_id"]))
    ok = await notify_assistant(context, user["user_id"], "✍️ Вопрос от клиента", f"«{html.escape(text[:3000])}»")
    await show(update, context, "ASK_DONE" if ok else "ASK_FAIL")


async def on_media(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Пожалуйста, не отправляйте сюда документы и фото — напишите вопрос текстом, и я передам его ассистенту."
    )


# ---------- обработчики ассистента ----------

async def assistant_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.message
    if not msg.reply_to_message:
        return
    with db() as conn:
        row = conn.execute(
            "SELECT user_id FROM relay WHERE assistant_msg_id = ?", (msg.reply_to_message.message_id,)
        ).fetchone()
    if not row:
        return
    try:
        sent = await context.bot.copy_message(row["user_id"], msg.chat_id, msg.message_id)
    except Forbidden:
        await msg.reply_text("❌ Клиент заблокировал бота — сообщение не доставлено.")
        return
    except TelegramError as e:
        await msg.reply_text(f"❌ Не удалось отправить: {e}")
        return
    with db() as conn:
        conn.execute("UPDATE leads SET status = 'contacted', updated = ? WHERE user_id = ? AND status = 'new'",
                     (time.time(), row["user_id"]))
        conn.execute("INSERT OR REPLACE INTO relay VALUES (?, ?)", (msg.message_id, row["user_id"]))
    await msg.reply_text("✅ Отправлено клиенту")


async def cmd_chatid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"ID этого чата: {update.effective_chat.id}")


async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    since = time.time() - 14 * DAY
    with db() as conn:
        def users_on(screen: str) -> int:
            return conn.execute(
                "SELECT COUNT(DISTINCT user_id) FROM events WHERE screen = ? AND ts > ?", (screen, since)
            ).fetchone()[0]
        started = users_on("START")
        price = users_on("PRICE")
        lead_screen = users_on("LEAD")
        leads = conn.execute("SELECT COUNT(*) FROM leads WHERE created > ?", (since,)).fetchone()[0]
        questions = users_on("ASK_DONE")
        sources = conn.execute(
            "SELECT COALESCE(source, '—'), COUNT(*) FROM users WHERE created > ? GROUP BY 1 ORDER BY 2 DESC", (since,)
        ).fetchall()
    await update.message.reply_text(
        "Статистика за 14 дней (уникальные люди):\n"
        f"Открыли бота: {started}\nСмотрели цену: {price}\nНажали «Хочу начать»: {lead_screen}\n"
        f"Оставили заявку: {leads}\nЗадали вопрос: {questions}\n\n"
        "Источники новых пользователей:\n" + ("\n".join(f"• {s}: {n}" for s, n in sources) or "—")
    )


# ---------- серия напоминаний ----------

async def send_followups(context: ContextTypes.DEFAULT_TYPE) -> None:
    with db() as conn:
        due = conn.execute(
            "SELECT f.id, f.user_id, f.screen, u.followup_consent, l.user_id AS has_lead FROM followups f"
            " JOIN users u ON u.user_id = f.user_id LEFT JOIN leads l ON l.user_id = f.user_id"
            " WHERE f.done = 0 AND f.due <= ?",
            (time.time(),),
        ).fetchall()
    for row in due:
        with db() as conn:
            conn.execute("UPDATE followups SET done = 1 WHERE id = ?", (row["id"],))
        if not row["followup_consent"] or row["has_lead"]:
            continue
        try:
            await send_screen(context, row["user_id"], row["screen"])
        except Forbidden:
            cancel_followups(row["user_id"])
        except TelegramError as e:
            log.error("Не удалось отправить %s пользователю %s: %s", row["screen"], row["user_id"], e)


async def post_init(app: Application) -> None:
    await app.bot.set_my_commands([
        BotCommand("start", "Начать сначала"),
        BotCommand("menu", "Главное меню"),
        BotCommand("price", "Стоимость"),
        BotCommand("help", "Частые вопросы"),
        BotCommand("stop", "Не присылать материалы"),
    ])


# ---------- баланс сервера Serverspace ----------

SERVERSPACE_API_KEY = os.environ.get("SERVERSPACE_API_KEY", "").strip()
SERVERSPACE_MIN_BALANCE = float(os.environ.get("SERVERSPACE_MIN_BALANCE", "300"))
SERVERSPACE_HOSTS = ("https://api.serverspace.ru", "https://api.serverspace.io")


async def serverspace_balance() -> tuple[float, str]:
    last_error = ""
    async with httpx.AsyncClient(timeout=30) as client:
        for host in SERVERSPACE_HOSTS:
            try:
                r = await client.get(f"{host}/api/v1/project", headers={"X-API-KEY": SERVERSPACE_API_KEY})
            except httpx.HTTPError as e:
                last_error = str(e)
                continue
            if r.status_code == 200:
                project = r.json().get("project", {})
                return float(project.get("balance", 0)), project.get("currency", "")
            last_error = f"{host}: HTTP {r.status_code}"
    raise RuntimeError(last_error)


async def check_server_balance(context: ContextTypes.DEFAULT_TYPE) -> None:
    if not (SERVERSPACE_API_KEY and ASSISTANT_CHAT_ID):
        return
    try:
        balance, currency = await serverspace_balance()
    except Exception as e:  # noqa: BLE001
        log.warning("Не удалось узнать баланс Serverspace: %s", e)
        return
    log.info("Баланс Serverspace: %s %s", balance, currency)
    if balance < SERVERSPACE_MIN_BALANCE:
        await context.bot.send_message(
            ASSISTANT_CHAT_ID,
            f"⚠️ На сервере Serverspace осталось {balance:.0f} {currency}. Пополните баланс, "
            "иначе сервер отключат и боты перестанут отвечать.",
        )


async def cmd_balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not SERVERSPACE_API_KEY:
        await update.message.reply_text("Ключ Serverspace не задан.")
        return
    try:
        balance, currency = await serverspace_balance()
        await update.message.reply_text(f"Баланс Serverspace: {balance:.2f} {currency}")
    except Exception as e:  # noqa: BLE001
        await update.message.reply_text(f"Не удалось узнать баланс: {e}")


# ---------- еженедельный дайджест канала ----------

DIGEST_TITLE_LIMIT = 90


def post_title(text: str | None) -> str:
    """Первая непустая строка поста, обрезанная до разумной длины."""
    for line in (text or "").splitlines():
        line = line.strip()
        if line:
            return line if len(line) <= DIGEST_TITLE_LIMIT else line[: DIGEST_TITLE_LIMIT - 1].rstrip() + "…"
    return ""


def post_link(chat_id: int, username: str | None, message_id: int) -> str:
    if username:
        return f"https://t.me/{username}/{message_id}"
    return f"https://t.me/c/{str(chat_id).removeprefix('-100')}/{message_id}"  # закрытый канал


async def on_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    post = update.channel_post
    title = post_title(post.text or post.caption)
    with db() as conn:
        if post.media_group_id:
            # Альбом приходит несколькими сообщениями — в дайджест попадает одно, с подписью.
            row = conn.execute(
                "SELECT message_id, title FROM channel_posts WHERE chat_id = ? AND media_group = ?",
                (post.chat.id, post.media_group_id),
            ).fetchone()
            if row:
                if title and not row["title"]:
                    conn.execute("UPDATE channel_posts SET title = ? WHERE chat_id = ? AND message_id = ?",
                                 (title, post.chat.id, row["message_id"]))
                return
        conn.execute(
            "INSERT OR IGNORE INTO channel_posts VALUES (?, ?, ?, ?, ?, ?)",
            (post.chat.id, post.message_id, post.chat.username, title, post.media_group_id, time.time()),
        )
    log.info("Пост в канале %s сохранён для дайджеста", post.chat.id)


def build_digest(chat_id: int) -> str | None:
    with db() as conn:
        rows = conn.execute(
            "SELECT message_id, username, title FROM channel_posts WHERE chat_id = ? AND ts > ? ORDER BY ts",
            (chat_id, time.time() - 7 * DAY),
        ).fetchall()
    if not rows:
        return None
    lines = ["📌 <b>Что было на канале за неделю</b>", ""]
    for r in rows:
        title = html.escape(r["title"] or "Пост с фото или видео")
        lines.append(f'• <a href="{post_link(chat_id, r["username"], r["message_id"])}">{title}</a>')
    lines += ["", "Сохраните, чтобы не потерять 💛"]
    return "\n".join(lines)


def digest_channels() -> list[int]:
    with db() as conn:
        rows = conn.execute("SELECT DISTINCT chat_id FROM channel_posts WHERE ts > ?", (time.time() - 7 * DAY,))
        return [r["chat_id"] for r in rows]


async def send_weekly_digest(context: ContextTypes.DEFAULT_TYPE) -> None:
    for chat_id in digest_channels():
        text = build_digest(chat_id)
        if not text:
            continue
        try:
            await context.bot.send_message(chat_id, text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
            log.info("Дайджест опубликован в канале %s", chat_id)
        except TelegramError as e:
            log.error("Не удалось опубликовать дайджест в канале %s: %s", chat_id, e)


async def cmd_digest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Предпросмотр дайджеста в группе ассистента — в канал ничего не уходит."""
    channels = digest_channels()
    if not channels:
        await update.message.reply_text("За последнюю неделю бот не видел постов в канале. "
                                        "Проверьте, что он добавлен в канал администратором.")
        return
    for chat_id in channels:
        await update.message.reply_text(build_digest(chat_id), parse_mode=ParseMode.HTML,
                                        disable_web_page_preview=True)


# ---------- личка Натальи (Telegram для бизнеса) ----------

BUSINESS_KEYWORD = os.environ.get("BUSINESS_KEYWORD", "генетика")
BUSINESS_REPEAT_WINDOW = 10 * 60
BUSINESS_TEXT = (
    "Здравствуйте! Спасибо за интерес к генетике 🙂\n\n"
    "Всё о системе «ДНК-здоровье» — что показывает тест, как всё проходит и сколько стоит — я собрала в боте. "
    "Там же можно задать вопрос или оставить заявку, мой ассистент ответит лично."
)
business_replied: dict[int, float] = {}


def has_business_keyword(text: str | None) -> bool:
    norm = (text or "").lower().replace("ё", "е")
    return BUSINESS_KEYWORD.lower().replace("ё", "е")[:-1] in norm  # «генетик» ловит «генетика», «генетику»


async def on_business_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Сообщение в личку Натальи. Отвечаем только на кодовое слово и только собеседнику, не самой Наталье."""
    msg = update.business_message
    if not msg or not msg.from_user or msg.from_user.id != msg.chat.id:
        return  # это написала сама Наталья
    if not has_business_keyword(msg.text or msg.caption):
        return
    now = time.time()
    if now - business_replied.get(msg.chat.id, 0) < BUSINESS_REPEAT_WINDOW:
        return
    business_replied[msg.chat.id] = now
    link = f"https://t.me/{context.bot.username}?start=tg_dm"
    try:
        await context.bot.send_message(
            msg.chat.id,
            BUSINESS_TEXT,
            business_connection_id=msg.business_connection_id,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("👉 Узнать о программе", url=link)]]),
        )
    except TelegramError as e:
        log.error("Не удалось ответить в личке Натальи: %s", e)
        return
    name = html.escape(msg.from_user.full_name or "без имени")
    if msg.from_user.username:
        name += f" (@{html.escape(msg.from_user.username)})"
    if ASSISTANT_CHAT_ID:
        try:
            await context.bot.send_message(
                ASSISTANT_CHAT_ID,
                f"💬 Личка Натальи в Telegram: {name} написал(а) «{BUSINESS_KEYWORD}» — отправила ссылку на бота.",
                parse_mode=ParseMode.HTML,
            )
        except TelegramError as e:
            log.warning("Не удалось уведомить ассистента: %s", e)


def main() -> None:
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    assistant = filters.Chat(ASSISTANT_CHAT_ID) if ASSISTANT_CHAT_ID else filters.Chat(chat_id=[])

    app.add_handler(MessageHandler(filters.UpdateType.BUSINESS_MESSAGE, on_business_message))
    app.add_handler(CommandHandler("chatid", cmd_chatid))
    app.add_handler(CommandHandler("stats", cmd_stats, filters=assistant))
    app.add_handler(CommandHandler("balance", cmd_balance, filters=assistant))
    app.add_handler(CommandHandler("digest", cmd_digest, filters=assistant))
    app.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST, on_channel_post))
    app.add_handler(MessageHandler(filters.UpdateType.MESSAGE & assistant & filters.REPLY & ~filters.COMMAND,
                                   assistant_reply))

    # Только обычные сообщения боту: переписка из лички Натальи сюда попадать не должна.
    private = filters.UpdateType.MESSAGE & filters.ChatType.PRIVATE & ~assistant
    app.add_handler(CommandHandler("start", cmd_start, filters=private))
    app.add_handler(CommandHandler("menu", command("START"), filters=private))
    app.add_handler(CommandHandler("price", command("PRICE"), filters=private))
    app.add_handler(CommandHandler("help", command("FAQ"), filters=private))
    app.add_handler(CommandHandler("stop", command("STOP_FOLLOW"), filters=private))
    app.add_handler(CallbackQueryHandler(on_button))
    app.add_handler(MessageHandler(private & filters.TEXT & ~filters.COMMAND, on_text))
    app.add_handler(MessageHandler(private & ~filters.TEXT & ~filters.COMMAND, on_media))

    app.job_queue.run_repeating(send_followups, interval=600, first=30)
    app.job_queue.run_repeating(check_server_balance, interval=DAY, first=60)
    # Воскресенье, 19:00 по Москве (в python-telegram-bot 0 = воскресенье).
    app.job_queue.run_daily(send_weekly_digest, time=dtime(19, 0, tzinfo=ZoneInfo("Europe/Moscow")), days=(0,))
    log.info("Бот запущен")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
