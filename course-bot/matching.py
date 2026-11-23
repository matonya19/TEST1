"""Подбор пар участников для совместных эфиров.

Бот сохраняет сообщения участников из группы (в зашифрованном виде — репозиторий публичный),
а по расписанию или по команде /match просит Claude предложить пары. Черновик приходит
владельцу в личку, в группу он уходит только после команды /publish.
"""
from __future__ import annotations

import base64
import hashlib
import html
import json
from datetime import datetime
from zoneinfo import ZoneInfo

import course_bot as cb

CHAT_LOG = cb.HERE / "data" / "chat.enc"
DRAFT = cb.HERE / "data" / "match_draft.enc"
MODEL = "claude-opus-5-5"
PER_PERSON_CHARS = 6000  # сколько последних символов от каждого участника отдавать модели


# ---------- Шифрованное хранилище ----------

def _fernet():
    key = cb.env("COURSE_DATA_KEY", required=False)
    if not key:
        return None
    from cryptography.fernet import Fernet
    return Fernet(base64.urlsafe_b64encode(hashlib.sha256(key.encode()).digest()))


def load_secret(path, default):
    f = _fernet()
    if f is None or not path.exists():
        return default
    from cryptography.fernet import InvalidToken
    try:
        return json.loads(f.decrypt(path.read_bytes()))
    except InvalidToken:
        raise RuntimeError(f"{path.name}: не удалось расшифровать — секрет COURSE_DATA_KEY изменился?")


def save_secret(path, data) -> None:
    f = _fernet()
    if f is None:
        raise RuntimeError("не задан секрет COURSE_DATA_KEY")
    path.parent.mkdir(exist_ok=True)
    path.write_bytes(f.encrypt(json.dumps(data, ensure_ascii=False).encode()))


class ChatStore:
    """Сообщения участников группы: {"messages": [...]}"""

    def __init__(self):
        self.enabled = _fernet() is not None
        self.data = load_secret(CHAT_LOG, {"messages": []}) if self.enabled else {"messages": []}
        self.seen = {m["id"] for m in self.data["messages"]}
        self.added = self.skipped = 0

    def add(self, msg: dict) -> None:
        sender = msg.get("from") or {}
        text = (msg.get("text") or msg.get("caption") or "").strip()
        if sender.get("is_bot") or not text or text.startswith("/"):
            return
        if not self.enabled:
            self.skipped += 1
            return
        if msg["message_id"] in self.seen:
            return
        self.seen.add(msg["message_id"])
        self.data["messages"].append({
            "id": msg["message_id"], "date": msg.get("date"), "thread": msg.get("message_thread_id"),
            "uid": sender.get("id"), "username": sender.get("username"),
            "name": " ".join(filter(None, [sender.get("first_name"), sender.get("last_name")])) or "Участник",
            "text": text,
        })
        self.added += 1

    def save(self) -> None:
        if self.enabled and self.added:
            save_secret(CHAT_LOG, self.data)

    def people(self) -> dict[int, dict]:
        people: dict[int, dict] = {}
        for m in self.data["messages"]:
            p = people.setdefault(m["uid"], {"uid": m["uid"], "name": m["name"], "username": m["username"],
                                             "texts": []})
            p["name"], p["username"] = m["name"], m["username"] or p["username"]  # последнее имя актуальнее
            p["texts"].append(m["text"])
        return people


# ---------- Подбор пар через Claude ----------

SCHEMA = {
    "type": "object",
    "properties": {
        "matches": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "members": {"type": "array", "items": {"type": "integer"}},
                    "topic": {"type": "string"},
                    "why": {"type": "string"},
                },
                "required": ["members", "topic", "why"],
                "additionalProperties": False,
            },
        },
        "unmatched": {"type": "array", "items": {"type": "integer"}},
        "note_for_host": {"type": "string"},
    },
    "required": ["matches", "unmatched", "note_for_host"],
    "additionalProperties": False,
}

SYSTEM = """Ты помогаешь ведущей онлайн-курса «Текстура диалога» — курса о том, как брать и давать интервью.
Участники курса пишут в общий чат о себе, своей работе и выполняют задания. Твоя задача — предложить пары \
участников для совместного эфира или интервью друг с другом, где один берёт интервью у другого или они \
обсуждают общую тему.

Как подбирать:
- Ищи сочетания, где у людей есть о чём поговорить: смежные сферы, взаимный интерес, один может быть \
интересен аудитории другого, похожие задачи с разных сторон. Совсем одинаковые профили — не лучший выбор.
- Тема — конкретная и интересная зрителю, одной фразой (не «Поговорим о бизнесе»).
- «Почему» — одно-два предложения, опирайся на то, что люди сами о себе написали. Не выдумывай фактов.
- Каждый участник — не больше чем в одной паре. При нечётном числе можно одну тройку.
- Если о человеке слишком мало информации, не подбирай ему пару — укажи его в unmatched.
- В members указывай uid участников из входных данных.
- В note_for_host коротко (1–3 предложения) напиши ведущей, что стоит учесть, например кого стоит \
расспросить подробнее. Пиши по-русски."""


def build_prompt(people: dict[int, dict]) -> str:
    blocks = []
    for p in people.values():
        text = "\n---\n".join(p["texts"])[-PER_PERSON_CHARS:]
        blocks.append(f'<participant uid="{p["uid"]}" name="{html.escape(p["name"])}">\n{text}\n</participant>')
    return ("Сообщения участников из чата курса:\n\n" + "\n\n".join(blocks) +
            "\n\nПредложи пары для совместных эфиров.")


def ask_claude(people: dict[int, dict]) -> dict:
    import anthropic

    client = anthropic.Anthropic()  # ключ берётся из ANTHROPIC_API_KEY
    response = client.beta.messages.create(
        model=MODEL,
        max_tokens=16000,
        system=SYSTEM,
        messages=[{"role": "user", "content": build_prompt(people)}],
        output_config={"effort": "high", "format": {"type": "json_schema", "schema": SCHEMA}},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    )
    if response.stop_reason == "refusal":
        raise RuntimeError("модель отказалась отвечать на этот запрос")
    if response.stop_reason == "max_tokens":
        raise RuntimeError("ответ модели оборвался, попробуйте ещё раз")
    text = next(b.text for b in response.content if b.type == "text")
    return json.loads(text)


def mention(person: dict) -> str:
    return f'<a href="tg://user?id={person["uid"]}">{html.escape(person["name"])}</a>'


def render(result: dict, people: dict[int, dict]) -> tuple[str, list[str]]:
    """Текст поста для группы и список предупреждений для ведущей."""
    warnings, used, lines = [], set(), ["🤝 <b>Пары для совместных эфиров</b>", "",
                                        "Мы почитали, что вы пишете о себе, и подобрали собеседников, "
                                        "с которыми у вас точно найдётся о чём поговорить:"]
    for match in result["matches"]:
        members = [people[u] for u in match["members"] if u in people and u not in used]
        if len(members) < 2:
            warnings.append(f"пропущена пара с неизвестными или повторными участниками: {match['members']}")
            continue
        used.update(p["uid"] for p in members)
        lines += ["", " × ".join(mention(p) for p in members),
                  f"🎙 <b>Тема:</b> {html.escape(match['topic'])}",
                  f"💡 {html.escape(match['why'])}"]
    lines += ["", "Напишите друг другу в личку и договоритесь о времени. "
                  "Один берёт интервью, другой отвечает — а потом можно поменяться 🎤"]
    return "\n".join(lines), warnings


def make_draft(tg: cb.Telegram, owner: str, cfg: dict, store: ChatStore | None = None) -> None:
    store = store or ChatStore()
    if not store.enabled:
        tg.send_text(owner, None, "⚠️ Не могу подобрать пары: в GitHub не задан секрет COURSE_DATA_KEY.", None)
        return
    people = store.people()
    if len(people) < 2:
        tg.send_text(owner, None, f"Пока мало данных: написали {len(people)} участник(ов). "
                                  "Подбор пар имеет смысл, когда люди расскажут о себе.", None)
        return
    result = ask_claude(people)
    text, warnings = render(result, people)
    save_secret(DRAFT, {"text": text, "created": datetime.now().isoformat(timespec="minutes")})
    unmatched = [people[u]["name"] for u in result.get("unmatched", []) if u in people]
    note = ["📝 <b>Черновик пар для группы</b> — проверьте его. Ниже то, что увидят участники.",
            f"Учтено участников: {len(people)}, сообщений: {len(store.data['messages'])}."]
    if unmatched:
        note.append("Без пары (мало информации): " + html.escape(", ".join(unmatched)))
    if result.get("note_for_host"):
        note.append("💬 " + html.escape(result["note_for_host"]))
    if warnings:
        note.append("⚠️ " + html.escape("; ".join(warnings)))
    note.append("/publish — опубликовать в группе\n/match — подобрать заново")
    tg.send_text(owner, None, "\n\n".join(note), "HTML")
    tg.send_text(owner, None, text, "HTML")


def publish(tg: cb.Telegram, owner: str) -> None:
    draft = load_secret(DRAFT, None)
    if not draft:
        tg.send_text(owner, None, "Черновика пока нет. Отправьте /match, чтобы подобрать пары.", None)
        return
    chat, thread = cb.env("COURSE_CHAT_ID"), cb.env("COURSE_THREAD_ID", required=False)
    tg.send_text(chat, thread, draft["text"], "HTML")
    DRAFT.unlink()
    tg.send_text(owner, None, "✅ Пары опубликованы в группе.", None)


def handle_command(command: str, tg: cb.Telegram, owner: str, cfg: dict, store: ChatStore) -> None:
    if command == "/stats":
        people = store.people()
        tg.send_text(owner, None, f"Собрано сообщений: {len(store.data['messages'])}, "
                                  f"участников: {len(people)}.", None)
    elif command == "/match":
        tg.send_text(owner, None, "⏳ Подбираю пары, это займёт пару минут…", None)
        make_draft(tg, owner, cfg, store)
    elif command == "/publish":
        publish(tg, owner)


def run_scheduled(tg: cb.Telegram, owner: str | None, cfg: dict) -> None:
    """Черновик пар в заданное в course.yaml время (matching.drafts)."""
    tz = ZoneInfo(cfg.get("timezone", "Europe/Moscow"))
    now = datetime.now(tz)
    state = cb.load_state()
    for raw in (cfg.get("matching") or {}).get("drafts", []):
        when = cb.parse_datetime(raw, "matching.drafts", tz)
        key = f"match:{when:%Y-%m-%dT%H:%M}"
        if when > now or key in state or not owner:
            continue
        try:
            make_draft(tg, owner, cfg)
            state[key] = {"sent": now.isoformat(timespec="minutes")}
        except Exception as e:
            print(f"! Подбор пар: {e}")
            if (now - when).total_seconds() > 6 * 3600:  # не повторяем бесконечно
                state[key] = {"failed": str(e)[:200]}
        cb.save_state(state)
