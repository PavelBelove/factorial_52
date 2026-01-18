#!/bin/bash
# Simple shell script to clear database

echo "🗑️  Clearing PlexMem database..."
cd "$(dirname "$0")/.."

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run Python script
python scripts/clear_database.py

