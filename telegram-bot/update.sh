#!/usr/bin/env bash
# Обновление ботов на сервере: bash /opt/dna-bot/telegram-bot/update.sh
set -e
git -c safe.directory='*' -C /opt/dna-bot pull -q
chown -R dnabot:dnabot /opt/dna-bot   # иначе боты не смогут писать в свои базы
systemctl restart dna-bot dna-bot-instagram
sleep 5
echo "Telegram-бот: $(systemctl is-active dna-bot)  Instagram-автоответчик: $(systemctl is-active dna-bot-instagram)"
