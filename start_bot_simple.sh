#!/bin/bash
cd /home/pavel/dev/plexmem
source venv/bin/activate
nohup python run_bot.py > logs/bot_simple.log 2>&1 &
echo "Bot started. Check logs/bot_simple.log"

