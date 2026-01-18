#!/bin/bash
# Migration: Add aliases column to quants table

cd /home/pavel/dev/plexmem

echo "Running migration: Add aliases column..."
sqlite3 data/plexmem.db "ALTER TABLE quants ADD COLUMN aliases JSON DEFAULT '[]';"

if [ $? -eq 0 ]; then
    echo "✅ Migration successful! Column 'aliases' added."
else
    echo "⚠️  Column may already exist or migration failed."
fi

