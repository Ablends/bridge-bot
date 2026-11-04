#!/bin/bash
# setup-server.sh: run ONCE on the Google Cloud server to install and start Bridge Bot.
# Usage (inside the bridge-bot folder on the server):  bash deploy/setup-server.sh
set -e
cd "$(dirname "$0")/.."
BOT_DIR="$(pwd)"

echo "== 1/4 Installing Python tools =="
sudo apt-get update -y
sudo apt-get install -y python3 python3-venv git

echo "== 2/4 Installing the bot's add-ons =="
python3 -m venv .venv
.venv/bin/pip install --upgrade pip -q
.venv/bin/pip install -r requirements.txt -q

if [ ! -f .env ]; then
  echo "!! No .env file found. Upload your .env file into $BOT_DIR, then run this script again."
  exit 1
fi

echo "== 3/4 Setting the bot to run 24/7 and restart itself if it crashes =="
sudo tee /etc/systemd/system/bridge-bot.service > /dev/null <<SERVICE
[Unit]
Description=Bridge Bot (Slack helper)
After=network-online.target
Wants=network-online.target

[Service]
User=$USER
WorkingDirectory=$BOT_DIR
ExecStart=$BOT_DIR/.venv/bin/python -u bot.py
Restart=always
RestartSec=15

[Install]
WantedBy=multi-user.target
SERVICE

# Every morning at 6:45am Denver time, download the latest my-focus.txt (and code) from GitHub.
sudo tee /etc/systemd/system/bridge-bot-pull.service > /dev/null <<SERVICE
[Unit]
Description=Download latest Bridge Bot files from GitHub

[Service]
Type=oneshot
User=$USER
WorkingDirectory=$BOT_DIR
ExecStart=/usr/bin/git pull --ff-only
SERVICE

sudo tee /etc/systemd/system/bridge-bot-pull.timer > /dev/null <<SERVICE
[Unit]
Description=Daily GitHub download for Bridge Bot

[Timer]
OnCalendar=*-*-* 06:45:00 America/Denver
Persistent=true

[Install]
WantedBy=timers.target
SERVICE

echo "== 4/4 Starting the bot =="
sudo systemctl daemon-reload
sudo systemctl enable --now bridge-bot.service bridge-bot-pull.timer
sleep 5
sudo systemctl status bridge-bot.service --no-pager | head -n 12
echo
echo "Done! Check Slack for the 'Bridge Bot is online' DM."
