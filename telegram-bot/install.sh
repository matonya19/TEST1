#!/usr/bin/env bash
# Установка и обновление бота «ДНК-здоровье» на сервере Ubuntu.
# Запуск (от root):
#   curl -fsSL https://raw.githubusercontent.com/matonya19/TEST1/instagram-bot/telegram-bot/install.sh | bash
# Повторный запуск обновляет код и позволяет поменять настройки (Enter — оставить как есть).
set -euo pipefail

REPO="https://github.com/matonya19/TEST1.git"
BRANCH="instagram-bot"
APP_DIR="/opt/dna-bot"
BOT_DIR="$APP_DIR/telegram-bot"
ENV_FILE="$BOT_DIR/.env"
SERVICE="dna-bot"

if [ "$(id -u)" -ne 0 ]; then
  echo "Запустите от root." >&2
  exit 1
fi

echo "==> Устанавливаю системные пакеты"
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq git python3 python3-venv >/dev/null

id dnabot >/dev/null 2>&1 || useradd --system --home "$APP_DIR" --shell /usr/sbin/nologin dnabot

echo "==> Загружаю код бота"
if [ -d "$APP_DIR/.git" ]; then
  git -c safe.directory="$APP_DIR" -C "$APP_DIR" fetch -q origin "$BRANCH"
  git -c safe.directory="$APP_DIR" -C "$APP_DIR" reset -q --hard "origin/$BRANCH"
else
  git clone -q --branch "$BRANCH" --depth 1 "$REPO" "$APP_DIR"
fi

echo "==> Устанавливаю зависимости"
python3 -m venv "$BOT_DIR/venv"
# Библиотеки лежат в папке wheels рядом с ботом: pypi.org из России бывает недоступен.
if ! "$BOT_DIR/venv/bin/pip" install -q --no-index --find-links "$BOT_DIR/wheels" -r "$BOT_DIR/requirements.txt"; then
  echo "Не хватило библиотек в папке wheels — пробую скачать с pypi.org"
  "$BOT_DIR/venv/bin/pip" install -q --timeout 60 -r "$BOT_DIR/requirements.txt"
fi

# Текущие значения настроек (если бот уже ставился раньше).
current() { [ -f "$ENV_FILE" ] && grep -E "^$1=" "$ENV_FILE" | cut -d= -f2- || true; }
ask() {
  local name="$1" prompt="$2" value old
  old="$(current "$name")"
  if [ -n "$old" ]; then prompt="$prompt [Enter — оставить текущее]"; fi
  read -r -p "$prompt: " value </dev/tty
  echo "${value:-$old}"
}

echo
echo "==> Настройки"
TOKEN="$(ask TELEGRAM_BOT_TOKEN "Токен бота от @BotFather")"
CHAT_ID="$(ask ASSISTANT_CHAT_ID "ID чата ассистента (если ещё не знаете — просто Enter)")"
CONTACT="$(ask ASSISTANT_CONTACT "Контакт ассистента для клиентов, например @username или +7... (можно Enter)")"
CONSENT="$(current CONSENT_VERSION)"
COMPOSIO="$(ask COMPOSIO_API_KEY "Ключ Composio для Instagram-автоответчика (если не нужен — Enter)")"

if [ -z "$TOKEN" ]; then
  echo "Без токена бот не запустится. Запустите установку ещё раз и вставьте токен." >&2
  exit 1
fi

umask 077
cat >"$ENV_FILE" <<EOF
TELEGRAM_BOT_TOKEN=$TOKEN
ASSISTANT_CHAT_ID=$CHAT_ID
ASSISTANT_CONTACT=$CONTACT
CONSENT_VERSION=${CONSENT:-v1}
COMPOSIO_API_KEY=$COMPOSIO
EOF
chown -R dnabot:dnabot "$APP_DIR"
chmod 600 "$ENV_FILE"

cat >/etc/systemd/system/$SERVICE.service <<EOF
[Unit]
Description=Telegram bot DNK-zdorovie
After=network-online.target
Wants=network-online.target

[Service]
User=dnabot
WorkingDirectory=$BOT_DIR
ExecStart=$BOT_DIR/venv/bin/python bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

cat >/etc/systemd/system/$SERVICE-instagram.service <<EOF
[Unit]
Description=Instagram keyword autoresponder
After=network-online.target
Wants=network-online.target

[Service]
User=dnabot
WorkingDirectory=$BOT_DIR
ExecStart=$BOT_DIR/venv/bin/python igbot.py
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable -q "$SERVICE"
systemctl restart "$SERVICE"
sleep 5

if [ -n "$COMPOSIO" ]; then
  echo
  echo "==> Проверяю подключение к Instagram"
  if runuser -u dnabot -- "$BOT_DIR/venv/bin/python" "$BOT_DIR/igbot.py" --check; then
    systemctl enable -q "$SERVICE-instagram"
    systemctl restart "$SERVICE-instagram"
    echo "✅ Instagram-автоответчик запущен."
  else
    echo "❌ Instagram-автоответчик не запущен: проверьте ключ Composio."
  fi
else
  systemctl disable -q --now "$SERVICE-instagram" 2>/dev/null || true
fi

echo
if systemctl is-active -q "$SERVICE"; then
  echo "✅ Бот запущен и будет сам запускаться после перезагрузки сервера."
  if [ -z "$CHAT_ID" ]; then
    echo
    echo "Дальше: добавьте бота в группу ассистента, напишите там /chatid,"
    echo "затем запустите эту же команду установки ещё раз и вставьте полученный ID."
  fi
else
  echo "❌ Бот не запустился. Последние строки журнала:"
  journalctl -u "$SERVICE" -n 20 --no-pager
fi
