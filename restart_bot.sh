#!/bin/bash
pkill -9 -f "run_bot.py"
sleep 1
cd /home/pavel/dev/plexmem
source venv/bin/activate
nohup python run_bot.py > logs/bot_restart.log 2>&1 &
sleep 2
echo "Bot restarted!"
tail -5 logs/bot_restart.log

