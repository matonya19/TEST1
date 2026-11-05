"""Однократное получение refresh_token для TikTok.

1. python get_tiktok_token.py           -> откройте ссылку, разрешите доступ
2. Скопируйте из адресной строки redirect-страницы параметр code=...
3. python get_tiktok_token.py <code>    -> получите refresh_token (живёт 365 дней)

Нужны TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET и TIKTOK_REDIRECT_URI в .env
(redirect URI должен совпадать с указанным в настройках приложения на developers.tiktok.com).
"""
import os
import secrets
import sys
from pathlib import Path
from urllib.parse import unquote, urlencode

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")
KEY, SECRET = os.environ["TIKTOK_CLIENT_KEY"], os.environ["TIKTOK_CLIENT_SECRET"]
REDIRECT = os.environ["TIKTOK_REDIRECT_URI"]

if len(sys.argv) < 2:
    print("Откройте ссылку и разрешите доступ:\n")
    print("https://www.tiktok.com/v2/auth/authorize/?" + urlencode({
        "client_key": KEY, "response_type": "code", "redirect_uri": REDIRECT,
        "scope": "user.info.basic,user.info.profile,user.info.stats,video.list",
        "state": secrets.token_urlsafe(8),
    }))
    sys.exit()

r = requests.post("https://open.tiktokapis.com/v2/oauth/token/", timeout=30, data={
    "client_key": KEY, "client_secret": SECRET, "code": unquote(sys.argv[1]),
    "grant_type": "authorization_code", "redirect_uri": REDIRECT,
})
data = r.json()
if "refresh_token" not in data:
    sys.exit(f"Ошибка: {data}")
print("TIKTOK_REFRESH_TOKEN=" + data["refresh_token"])
print(f"(действует {data.get('refresh_expires_in', 0) // 86400} дн., scopes: {data.get('scope')})")
