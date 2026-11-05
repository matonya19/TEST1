from __future__ import annotations

import requests

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


def send(token: str, chat_ids: str, text: str) -> None:
    for chat_id in [c.strip() for c in chat_ids.split(",") if c.strip()]:
        for part in _chunks(text):
            r = requests.post(f"https://api.telegram.org/bot{token}/sendMessage", timeout=30, json={
                "chat_id": chat_id, "text": part, "parse_mode": "HTML",
                "disable_web_page_preview": True,
            })
            if not r.ok:
                raise RuntimeError(f"Telegram: {r.status_code} {r.text[:300]}")
