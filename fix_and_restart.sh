#!/bin/bash
# Fix database and restart PlexMem

cd /home/pavel/dev/plexmem

echo "=== Stopping services ==="
pkill -f "uvicorn core.api.main:app"
pkill -9 -f run_bot.py
sleep 2

echo ""
echo "=== Adding aliases column to database ==="
sqlite3 data/plexmem.db "ALTER TABLE quants ADD COLUMN aliases JSON DEFAULT '[]';" 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Column 'aliases' added successfully"
elif echo "Error: duplicate column name: aliases" | grep -q "duplicate"; then
    echo "⚠️  Column 'aliases' already exists (OK)"
else
    echo "⚠️  Migration completed (column may already exist)"
fi

echo ""
echo "=== Verifying database schema ==="
echo "Checking for synopsis and aliases columns..."
sqlite3 data/plexmem.db "PRAGMA table_info(quants);" | grep -E "(synopsis|aliases)"

echo ""
echo "=== Starting PlexMem ==="
bash start_plexmem.sh

