#!/bin/bash
set -e

echo "🔧 Применение исправлений от 19 января..."

cd /home/pavel/dev/plexmem

# 1. Activate venv
echo "📦 Активация окружения..."
source venv/bin/activate

# 2. Apply DB migration
echo "🗄️  Применение миграции БД (synopsis column)..."
python3 fix_db_now.py

# 3. Stop services
echo "⏹️  Остановка сервисов..."
pkill -f "uvicorn core.api.main:app" 2>/dev/null || true
pkill -9 -f run_bot.py 2>/dev/null || true
sleep 2

# 4. Start services
echo "🚀 Запуск системы..."
bash start_plexmem.sh

echo ""
echo "✅ Готово!"
echo ""
echo "Исправлено:"
echo "  1. Ошибка 'no such column: synopsis'"
echo "  2. ГМ показывает проверки правильно"
echo "  3. /retry не телепортирует героя"
echo "  4. Формулы расчётов исправлены"
echo ""
echo "Проверь игру! 🎲"

