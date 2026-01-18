#!/bin/bash
echo "=== Checking running processes ==="
ps aux | grep -E "run_bot|uvicorn" | grep -v grep
echo ""
echo "=== Bot log (last 10 lines) ==="
tail -10 /home/pavel/dev/plexmem/logs/bot_new.log
echo ""
echo "=== API status ==="
curl -s http://localhost:8000/ | head -1

