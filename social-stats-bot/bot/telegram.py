from __future__ import annotations

import logging
import os

import requests

log = logging.getLogger(__name__)

LIMIT = 4000  # у Telegram лимит 4096 символов на сообщение


def _chunks(text: str) -> list[str]:
    out, cur = [], ""
    for block in text.split("\n\n"):
        # Режем по абзацам, чтобы не разорвать HTML-теги
        while len(block) > LIMIT:
            cut = block.rfind("\n", 0, LIMIT)
            cut = cut if cut > 0 else LIMIT
            out.append(block[:cut])
            block = block[cut:].lstrip("\n")
        if len(cur) + len(block) + 2 > LIMIT:
            out.append(cur)
            cur = block
        else:
            cur = f"{cur}\n\n{block}" if cur else block
    if cur:
        out.append(cur)
    return out


def _post(token: str, chat_id: str, part: str) -> requests.Response:
    return requests.post(f"https://api.telegram.org/bot{token}/sendMessage", timeout=30, json={
        "chat_id": chat_id, "text": part, "parse_mode": "HTML",
        "disable_web_page_preview": True,
    })


def send(token: str, chat_ids: str, text: str) -> None:
    """Отправляет отчёт во все чаты из списка (через запятую): личку, группы, каналы."""
    errors = []
    for chat_id in [c.strip() for c in chat_ids.split(",") if c.strip()]:
        for part in _chunks(text):
            r = _post(token, chat_id, part)
            # Группа превратилась в супергруппу (например, после назначения админа) — у неё новый ID
            new_id = (r.json().get("parameters") or {}).get("migrate_to_chat_id") if not r.ok else None
            if new_id:
                log.warning("Чат %s стал супергруппой с ID %s — обновите TELEGRAM_CHAT_ID", chat_id, new_id)
                chat_id = str(new_id)
                r = _post(token, chat_id, part)
            if not r.ok:
                errors.append(f"{chat_id}: {r.status_code} {r.text[:300]}")
                break
    if errors:
        raise RuntimeError("Telegram: " + "; ".join(errors))


def list_chats(token: str) -> list[dict]:
    """Чаты, в которых бот недавно получал сообщения или куда его добавили (за ~24 часа)."""
    r = requests.get(f"https://api.telegram.org/bot{token}/getUpdates", timeout=30,
                     params={"allowed_updates": '["message","my_chat_member","channel_post"]'})
    if not r.ok:
        raise RuntimeError(f"Telegram: {r.status_code} {r.text[:300]}")
    chats: dict[int, dict] = {}
    for upd in r.json().get("result", []):
        for key in ("message", "my_chat_member", "channel_post"):
            obj = upd.get(key)
            if not obj:
                continue
            chat = obj["chat"]
            chats[chat["id"]] = {"id": chat["id"], "type": chat["type"],
                                 "title": chat.get("title") or chat.get("first_name", "")}
            if obj.get("migrate_to_chat_id"):
                chats.pop(chat["id"], None)
                chats[obj["migrate_to_chat_id"]] = {"id": obj["migrate_to_chat_id"],
                                                    "type": "supergroup", "title": chat.get("title", "")}
    return list(chats.values())


if __name__ == "__main__":
    found = list_chats(os.environ["TELEGRAM_BOT_TOKEN"])
    if not found:
        print("Чатов не найдено. Напишите любое сообщение в группу (или упомяните бота) "
              "и запустите ещё раз.")
    kinds = {"private": "личный чат", "group": "группа", "supergroup": "группа", "channel": "канал"}
    for c in found:
        print(f"{kinds.get(c['type'], c['type']):10}  {c['title']!s:30}  ID: {c['id']}")
