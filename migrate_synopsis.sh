#!/bin/bash
# Migration: Add synopsis column to quants table

cd /home/pavel/dev/plexmem
source venv/bin/activate

echo "Running migration: Add synopsis column..."
python3 << 'EOF'
import sqlite3

db_path = "data/plexmem.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check if synopsis column exists
    cursor.execute("PRAGMA table_info(quants)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'synopsis' in columns:
        print("✅ Column 'synopsis' already exists. No migration needed.")
    else:
        # Add synopsis column
        print("Adding 'synopsis' column to quants table...")
        cursor.execute("ALTER TABLE quants ADD COLUMN synopsis VARCHAR(500)")
        conn.commit()
        print("✅ Migration successful! Column 'synopsis' added.")
except Exception as e:
    print(f"❌ Migration failed: {e}")
    conn.rollback()
finally:
    conn.close()
EOF

echo ""
echo "Migration complete. Now starting PlexMem..."
sleep 2
bash start_plexmem.sh

