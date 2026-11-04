#!/bin/bash
# update.sh: get the newest code from GitHub and restart the bot.
# Usage (on the server, inside the bridge-bot folder):  bash deploy/update.sh
set -e
cd "$(dirname "$0")/.."
git pull --ff-only
.venv/bin/pip install -r requirements.txt -q
sudo systemctl restart bridge-bot.service
sleep 5
sudo systemctl status bridge-bot.service --no-pager | head -n 8
