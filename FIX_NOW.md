# Быстрое исправление БД

## Проблема
Отсутствует столбец `aliases` в таблице `quants`.

## Решение

Выполни эти команды:

```bash
# 1. Останови систему
pkill -f "uvicorn core.api.main:app"
pkill -9 -f run_bot.py
sleep 2

# 2. Добавь столбец aliases
cd /home/pavel/dev/plexmem
sqlite3 data/plexmem.db "ALTER TABLE quants ADD COLUMN aliases JSON DEFAULT '[]';"

# 3. Проверь что оба столбца на месте
sqlite3 data/plexmem.db "PRAGMA table_info(quants);" | grep -E "(synopsis|aliases)"

# 4. Перезапусти систему
bash start_plexmem.sh
```

## Альтернатива (одной командой)

```bash
cd /home/pavel/dev/plexmem && \
pkill -f "uvicorn core.api.main:app" && pkill -9 -f run_bot.py && sleep 2 && \
sqlite3 data/plexmem.db "ALTER TABLE quants ADD COLUMN aliases JSON DEFAULT '[]';" && \
bash start_plexmem.sh
```

Система должна заработать после этого!

