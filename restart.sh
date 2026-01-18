#!/bin/bash
cd /home/pavel/dev/plexmem
pkill -f "uvicorn core.api.main:app"
pkill -9 -f run_bot.py
sleep 2
bash start_plexmem.sh

