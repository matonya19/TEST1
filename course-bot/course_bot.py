"""Бот курса: публикует посты дня и напоминания о встречах в ветку (тему) Telegram-группы.

Команды:
  python course_bot.py run        — отправить всё, что пора отправить (запускается по расписанию)
  python course_bot.py preview    — показать расписание и что уже отправлено
  python course_bot.py discover   — найти ID группы, ветки и file_id присланных боту видео
  python course_bot.py test       — проверочное сообщение в ветку группы
  python course_bot.py test 3     — прислать пост 3-го дня в тестовый чат COURSE_TEST_CHAT_ID

Переменные окружения: COURSE_BOT_TOKEN, COURSE_CHAT_ID, COURSE_THREAD_ID, COURSE_TEST_CHAT_ID.
"""
from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
import yaml

HERE = Path(__file__).parent
CONFIG = HERE / "course.yaml"
STATE = HERE / "data" / "sent.json"
CAPTION_LIMIT = 1024
TEXT_LIMIT = 4096
PLACEHOLDER = "ЗАМЕНИТЕ"
MEDIA_KINDS = ("video", "photo", "document", "animation")
MONTHS = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа",
          "сентября", "октября", "ноября", "декабря"]
WEEKDAYS = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]


# ---------- Telegram ----------

class Telegram:
    def __init__(self, token: str):
        self.base = f"https://api.telegram.org/bot{token}/"

    def call(self, method: str, data: dict, files: dict | None = None) -> dict:
        data = {k: v for k, v in data.items() if v is not None}
        r = requests.post(self.base + method, data=data, files=files, timeout=300)
        body = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
        if not body.get("ok"):
            # Если в тексте сломалась HTML-разметка — отправляем как обычный текст
            if "can't parse entities" in str(body.get("description", "")) and data.get("parse_mode"):
                print(f"  ! Ошибка разметки, отправляю без форматирования: {body['description']}")
                data.pop("parse_mode")
                return self.call(method, data, _reopen(files))
            new_id = (body.get("parameters") or {}).get("migrate_to_chat_id")
            hint = f" (группа стала супергруппой, новый ID: {new_id} — обновите COURSE_CHAT_ID)" if new_id else ""
            raise RuntimeError(f"Telegram {method}: {r.status_code} {body.get('description') or r.text[:300]}{hint}")
        return body["result"]

    def send_text(self, chat: str, thread: str | None, text: str, parse_mode: str | None) -> None:
        for part in split_text(text, TEXT_LIMIT):
            self.call("sendMessage", {"chat_id": chat, "message_thread_id": thread, "text": part,
                                      "parse_mode": parse_mode, "link_preview_options": '{"is_disabled": true}'})

    def send_media(self, chat: str, thread: str | None, kind: str, source: str, caption: str | None,
                   parse_mode: str | None) -> None:
        method = "send" + kind.capitalize()
        data = {"chat_id": chat, "message_thread_id": thread, "caption": caption,
                "parse_mode": parse_mode if caption else None}
        if kind == "video":
            data["supports_streaming"] = "true"
        files = None
        local = (HERE / source)
        if source.startswith(("http://", "https://")) or not local.is_file():
            data[kind] = source  # ссылка или file_id
        else:
            size_mb = local.stat().st_size / 1024 / 1024
            if size_mb > 50:
                raise RuntimeError(f"{source}: {size_mb:.0f} МБ, а бот может загрузить максимум 50 МБ. "
                                   "Пришлите видео боту в личку и используйте его file_id (см. README).")
            files = {kind: (local.name, local.open("rb"))}
        try:
            self.call(method, data, files)
        finally:
            for _, fh in (files or {}).values():
                fh.close()


def _reopen(files: dict | None) -> dict | None:
    if not files:
        return None
    return {k: (name, open(fh.name, "rb")) for k, (name, fh) in files.items()}


def split_text(text: str, limit: int) -> list[str]:
    parts, cur = [], ""
    for para in text.split("\n\n"):
        while len(para) > limit:
            cut = para.rfind("\n", 0, limit)
            cut = cut if cut > 0 else limit
            parts.append(para[:cut])
            para = para[cut:].lstrip("\n")
        if cur and len(cur) + len(para) + 2 > limit:
            parts.append(cur)
            cur = para
        else:
            cur = f"{cur}\n\n{para}" if cur else para
    if cur:
        parts.append(cur)
    return parts


# ---------- Расписание ----------

@dataclass
class Item:
    key: str           # уникальный ключ, по нему бот помнит, что уже отправил
    when: datetime     # когда отправить
    title: str         # для журнала
    text: str
    media: tuple[str, str] | None = None  # (тип, путь / ссылка / file_id)
    deadline: datetime | None = None      # после этого момента уже не отправлять


def parse_time(value, field: str) -> tuple[int, int]:
    if isinstance(value, int):  # YAML читает 10:00 без кавычек как число 600 (минуты)
        return value // 60, value % 60
    m = re.fullmatch(r"\s*(\d{1,2})[:.](\d{2})\s*", str(value))
    if not m:
        raise ValueError(f"{field}: не понимаю время {value!r}, нужно как \"10:00\"")
    return int(m[1]), int(m[2])


def parse_date(value, field: str) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value).strip())
    except ValueError:
        raise ValueError(f"{field}: не понимаю дату {value!r}, нужно как 2026-11-23") from None


def parse_datetime(value, field: str, tz: ZoneInfo) -> datetime:
    if isinstance(value, datetime):
        return value.replace(tzinfo=tz) if value.tzinfo is None else value.astimezone(tz)
    m = re.fullmatch(r"\s*(\d{4}-\d{2}-\d{2})[ T](\d{1,2}[:.]\d{2})(?::\d{2})?\s*", str(value))
    if not m:
        raise ValueError(f"{field}: не понимаю {value!r}, нужно как \"2026-11-25 19:00\"")
    d, (h, mi) = parse_date(m[1], field), parse_time(m[2], field)
    return datetime(d.year, d.month, d.day, h, mi, tzinfo=tz)


def parse_offset(value, field: str) -> timedelta:
    m = re.fullmatch(r"\s*(\d+)\s*([dhmдчм]?)\w*\s*", str(value).lower())
    if not m:
        raise ValueError(f"{field}: не понимаю {value!r}, нужно как 1d, 3h, 15m или 0")
    n, unit = int(m[1]), m[2] or "m"
    return {"d": timedelta(days=n), "д": timedelta(days=n), "h": timedelta(hours=n),
            "ч": timedelta(hours=n)}.get(unit, timedelta(minutes=n))


def human_dt(dt: datetime) -> str:
    return f"{dt.day} {MONTHS[dt.month - 1]} ({WEEKDAYS[dt.weekday()]}) в {dt:%H:%M}"


def human_offset(off: timedelta) -> str:
    mins = int(off.total_seconds() // 60)
    if mins <= 0:
        return "Начинаем"
    if mins % 1440 == 0:
        days = mins // 1440
        return "Уже завтра" if days == 1 else f"Через {days} {plural(days, 'день', 'дня', 'дней')}"
    if mins % 60 == 0:
        h = mins // 60
        return f"Через {h} {plural(h, 'час', 'часа', 'часов')}"
    return f"Через {mins} {plural(mins, 'минуту', 'минуты', 'минут')}"


def plural(n: int, one: str, few: str, many: str) -> str:
    if n % 10 == 1 and n % 100 != 11:
        return one
    return few if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14 else many


def load_config() -> dict:
    try:
        with CONFIG.open(encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        sys.exit(f"Ошибка в course.yaml: {e}\n\nЧастая причина: двоеточие с пробелом внутри текста. "
                 "Возьмите такое значение в кавычки или используйте text: | с новой строки.")


def build_schedule(cfg: dict) -> list[Item]:
    tz = ZoneInfo(cfg.get("timezone", "Europe/Moscow"))
    start = parse_date(cfg["start_date"], "start_date")
    default_time = cfg.get("post_time", "10:00")
    catch_up = timedelta(hours=float(cfg.get("catch_up_hours", 12)))
    items: list[Item] = []
    seen: dict[str, int] = {}

    for i, post in enumerate(cfg.get("posts") or [], 1):
        where = f"posts[{i}]"
        if "date" in post:
            d = parse_date(post["date"], where + ".date")
        elif "day" in post:
            d = start + timedelta(days=int(post["day"]) - 1)
        else:
            raise ValueError(f"{where}: укажите day (номер дня курса) или date")
        h, m = parse_time(post.get("time", default_time), where + ".time")
        when = datetime(d.year, d.month, d.day, h, m, tzinfo=tz)
        media = [(k, str(post[k])) for k in MEDIA_KINDS if post.get(k)]
        if len(media) > 1:
            raise ValueError(f"{where}: в одном посте может быть только одно вложение")
        base = f"post:{when:%Y-%m-%dT%H:%M}"
        seen[base] = seen.get(base, 0) + 1
        label = f"День {post['day']}" if "day" in post else f"Пост {d}"
        items.append(Item(key=f"{base}#{seen[base]}", when=when, title=label,
                          text=str(post.get("text") or "").strip(), media=media[0] if media else None,
                          deadline=when + catch_up))

    default_reminders = cfg.get("default_reminders", ["1d", "1h"])
    for i, ev in enumerate(cfg.get("events") or [], 1):
        where = f"events[{i}]"
        start_at = parse_datetime(ev["datetime"], where + ".datetime", tz)
        title = str(ev.get("title", "Встреча"))
        for off_raw in ev.get("reminders", default_reminders):
            off = parse_offset(off_raw, where + ".reminders")
            when = start_at - off
            # Если напоминание сильно опоздало (бот не работал), оно уже не нужно
            deadline = min(when + timedelta(hours=1), start_at + timedelta(minutes=15))
            items.append(Item(key=f"event:{start_at:%Y-%m-%dT%H:%M}:{title}:{int(off.total_seconds() // 60)}m",
                              when=when, title=f"{title} — напоминание «{human_offset(off)}»",
                              text=event_text(ev, title, start_at, off), deadline=deadline))
    return sorted(items, key=lambda it: it.when)


def event_text(ev: dict, title: str, start_at: datetime, off: timedelta) -> str:
    icon = "🔴" if str(ev.get("kind", "")).lower() in ("эфир", "online", "онлайн", "live") else "📍"
    lines = [f"🔔 <b>{human_offset(off)} — {title}</b>", "", f"🗓 {human_dt(start_at)}"]
    if ev.get("place"):
        lines.append(f"{icon} {ev['place']}")
    if ev.get("link"):
        lines.append(f"🔗 {ev['link']}")
    if ev.get("text"):
        lines += ["", str(ev["text"]).strip()]
    return "\n".join(lines)


# ---------- Отправка ----------

def deliver(tg: Telegram, chat: str, thread: str | None, item: Item, parse_mode: str | None) -> None:
    if not item.media:
        tg.send_text(chat, thread, item.text, parse_mode)
        return
    kind, source = item.media
    if len(item.text) <= CAPTION_LIMIT:
        tg.send_media(chat, thread, kind, source, item.text or None, parse_mode)
    else:  # подпись длиннее 1024 символов — сначала вложение, потом текст отдельным сообщением
        tg.send_media(chat, thread, kind, source, None, None)
        tg.send_text(chat, thread, item.text, parse_mode)


def load_state() -> dict:
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_state(state: dict) -> None:
    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def env(name: str, required: bool = True) -> str | None:
    value = (os.environ.get(name) or "").strip()
    if required and not value:
        sys.exit(f"Не задана переменная {name} (см. README, раздел «Что нужно от вас»)")
    return value or None


def cmd_run(cfg: dict) -> None:
    if not cfg.get("enabled"):
        print("Бот выключен: в course.yaml стоит enabled: false. Ничего не отправляю.")
        return
    tg = Telegram(env("COURSE_BOT_TOKEN"))
    chat, thread = env("COURSE_CHAT_ID"), env("COURSE_THREAD_ID", required=False)
    parse_mode = cfg.get("parse_mode", "HTML") or None
    now = datetime.now(ZoneInfo(cfg.get("timezone", "Europe/Moscow")))
    state, errors = load_state(), []

    for item in build_schedule(cfg):
        if item.key in state or item.when > now:
            continue
        if item.deadline and now > item.deadline:
            print(f"- Пропускаю (опоздание): {item.title}, {item.when:%d.%m %H:%M}")
            state[item.key] = {"skipped": True, "at": now.isoformat(timespec="minutes")}
            continue
        if PLACEHOLDER in item.text:
            print(f"! Не отправляю {item.title}: в тексте остался шаблон «{PLACEHOLDER}»")
            errors.append(f"{item.title}: не заполнен текст")
            continue
        try:
            deliver(tg, chat, thread, item, parse_mode)
        except Exception as e:  # одна ошибка не должна блокировать остальные публикации
            print(f"! Ошибка при отправке «{item.title}»: {e}")
            errors.append(f"{item.title}: {e}")
            continue
        print(f"+ Отправлено: {item.title}")
        state[item.key] = {"sent": now.isoformat(timespec="minutes")}
        save_state(state)  # сохраняем сразу, чтобы при сбое не отправить дважды
    save_state(state)
    if errors:
        sys.exit("Были ошибки:\n" + "\n".join(errors))


def cmd_preview(cfg: dict) -> None:
    state = load_state()
    print(f"Бот {'ВКЛЮЧЁН' if cfg.get('enabled') else 'выключен (enabled: false)'}, "
          f"старт курса {cfg['start_date']}, часовой пояс {cfg.get('timezone', 'Europe/Moscow')}\n")
    for it in build_schedule(cfg):
        mark = "✅" if "sent" in state.get(it.key, {}) else "⏭" if it.key in state else "⏳"
        warn = "  ⚠️ шаблонный текст" if PLACEHOLDER in it.text else ""
        media = f"  [{it.media[0]}]" if it.media else ""
        print(f"{mark} {WEEKDAYS[it.when.weekday()][:2]} {it.when:%d.%m %H:%M}  {it.title}{media}{warn}")


def cmd_test(cfg: dict, day: str | None) -> None:
    tg = Telegram(env("COURSE_BOT_TOKEN"))
    parse_mode = cfg.get("parse_mode", "HTML") or None
    if not day:
        chat, thread = env("COURSE_CHAT_ID"), env("COURSE_THREAD_ID", required=False)
        tg.send_text(chat, thread, "✅ Бот курса подключён. Здесь будут посты и напоминания.", None)
        print(f"Проверочное сообщение отправлено в чат {chat}, ветку {thread or '— (общий чат)'}")
        return
    chat = env("COURSE_TEST_CHAT_ID")
    items = [it for it in build_schedule(cfg) if it.title in (f"День {day}", f"Пост {day}")]
    if not items:
        sys.exit(f"В course.yaml нет поста для дня {day}")
    for it in items:
        deliver(tg, chat, None, it, parse_mode)
        print(f"Пост «{it.title}» отправлен в тестовый чат {chat}")


def cmd_discover() -> None:
    token = env("COURSE_BOT_TOKEN")
    r = requests.get(f"https://api.telegram.org/bot{token}/getUpdates", timeout=30, params={
        "allowed_updates": json.dumps(["message", "my_chat_member", "channel_post"])})
    if not r.ok:
        sys.exit(f"Telegram: {r.status_code} {r.text[:300]}")
    chats, topics, files = {}, {}, []
    for upd in r.json().get("result", []):
        for key in ("message", "my_chat_member", "channel_post"):
            msg = upd.get(key)
            if not msg:
                continue
            chat = msg["chat"]
            chat_id = msg.get("migrate_to_chat_id") or chat["id"]
            chats[chat_id] = chat.get("title") or chat.get("first_name", "")
            if msg.get("is_topic_message") or msg.get("message_thread_id"):
                created = msg.get("forum_topic_created") or \
                    (msg.get("reply_to_message") or {}).get("forum_topic_created") or {}
                tid = msg["message_thread_id"]
                topics[(chat_id, tid)] = created.get("name") or topics.get((chat_id, tid)) or "?"
            for kind in MEDIA_KINDS:
                media = msg.get(kind)
                if media:
                    media = media[-1] if isinstance(media, list) else media  # у фото — самый большой размер
                    name = media.get("file_name") or msg.get("caption", "")[:40]
                    files.append((kind, name, media["file_id"]))

    if not (chats or files):
        print("Ничего не найдено. Напишите в нужной ветке группы /id@имя_вашего_бота "
              "(или пришлите боту видео в личку) и запустите ещё раз в течение суток.")
    print("ЧАТЫ (COURSE_CHAT_ID):")
    for cid, title in chats.items():
        print(f"  {cid:>16}  {title}")
    print("\nВЕТКИ / ТЕМЫ (COURSE_THREAD_ID):")
    for (cid, tid), name in topics.items():
        print(f"  чат {cid}  ветка {tid:>6}  «{name}»")
    if not topics:
        print("  не найдено — напишите /id@имя_бота именно в нужной ветке")
    print("\nФАЙЛЫ (вставьте file_id в course.yaml в поле video/photo/document):")
    for kind, name, fid in files:
        print(f"  {kind:9} {name!s:40} {fid}")


def main() -> None:
    args = sys.argv[1:] or ["run"]
    cmd = args[0]
    if cmd == "discover":
        return cmd_discover()
    cfg = load_config()
    {"run": lambda: cmd_run(cfg),
     "preview": lambda: cmd_preview(cfg),
     "test": lambda: cmd_test(cfg, args[1] if len(args) > 1 and args[1] else None),
     }.get(cmd, lambda: sys.exit(__doc__))()


if __name__ == "__main__":
    main()
