#!/bin/bash

# PlexMem - Simple Startup (Console Output)
# Quick start with visible logs

echo "🚀 PlexMem Quick Start"
echo ""

cd /home/pavel/dev/plexmem

# Kill old - AGGRESSIVE
echo "🧹 Убиваем старые процессы..."
pkill -9 -f "python.*run_api" 2>/dev/null || true
pkill -9 -f "python.*run_bot" 2>/dev/null || true
pkill -9 -f "uvicorn" 2>/dev/null || true
if command -v fuser &> /dev/null; then
    fuser -k 8000/tcp 2>/dev/null || true
fi
sleep 2

# Activate
source venv/bin/activate

# Cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Остановка..."
    pkill -9 -f "uvicorn|run_api|run_bot" 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start
echo "▶️  Запуск API..."
python run_api.py &
API_PID=$!
sleep 5

echo "▶️  Запуск Bot..."
python run_bot.py &
BOT_PID=$!

echo ""
echo "✅ Работает! API: $API_PID, Bot: $BOT_PID"
echo "💡 Логи в logs/api.log и logs/bot.log"
echo "⚠️  Ctrl+C для остановки"
echo ""

wait -n $API_PID $BOT_PID
cleanup

