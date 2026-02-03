#!/bin/bash

# PlexMem - Console Mode
# All logs visible in terminal (no background processes)

set -e

echo "╔════════════════════════════════════════════╗"
echo "║    PlexMem - CONSOLE MODE (Full Output)   ║"
echo "╚════════════════════════════════════════════╝"
echo ""

cd /home/pavel/dev/plexmem

# Kill old - AGGRESSIVE
echo "🧹 Очистка старых процессов..."
pkill -9 -f "python.*run_api" 2>/dev/null || true
pkill -9 -f "python.*run_bot" 2>/dev/null || true
pkill -9 -f "uvicorn" 2>/dev/null || true
# Kill by port
if command -v fuser &> /dev/null; then
    fuser -k 8000/tcp 2>/dev/null || true
fi
sleep 2
echo "✅ Готово"
echo ""

# Activate
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ venv не найден!"
    exit 1
fi

# Cleanup
cleanup() {
    echo ""
    echo "🛑 Остановка всех процессов..."
    pkill -9 -f "uvicorn|run_api|run_bot" 2>/dev/null || true
    echo "✅ Остановлено"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Create named pipes for output
API_LOG=$(mktemp)
BOT_LOG=$(mktemp)

# Start API in background but pipe to console
echo "╔════════════════════════════════════════════╗"
echo "║         [1/2] Запуск API сервера           ║"
echo "╚════════════════════════════════════════════╝"
echo ""
venv/bin/python run_api.py > "$API_LOG" 2>&1 &
API_PID=$!

# Show API output
tail -f "$API_LOG" &
TAIL_API_PID=$!

sleep 5

echo ""
echo "╔════════════════════════════════════════════╗"
echo "║       [2/2] Запуск Telegram Bot            ║"
echo "╚════════════════════════════════════════════╝"
echo ""
venv/bin/python run_bot.py > "$BOT_LOG" 2>&1 &
BOT_PID=$!

# Show Bot output
tail -f "$BOT_LOG" &
TAIL_BOT_PID=$!

echo ""
echo "╔════════════════════════════════════════════╗"
echo "║           ✅ ВСЁ ЗАПУЩЕНО!                 ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "API:  http://localhost:8000 (PID $API_PID)"
echo "Bot:  Active (PID $BOT_PID)"
echo ""
echo "💡 Все логи видны в консоли"
echo "⚠️  Нажми Ctrl+C для остановки"
echo ""
echo "════════════════════════════════════════════════"
echo ""

# Enhanced cleanup
cleanup_all() {
    echo ""
    echo "🛑 Остановка..."
    kill $TAIL_API_PID $TAIL_BOT_PID $API_PID $BOT_PID 2>/dev/null || true
    pkill -9 -f "uvicorn|run_api|run_bot" 2>/dev/null || true
    rm -f "$API_LOG" "$BOT_LOG"
    echo "✅ Готово"
    exit 0
}

trap cleanup_all SIGINT SIGTERM

# Wait
wait -n $API_PID $BOT_PID
cleanup_all

