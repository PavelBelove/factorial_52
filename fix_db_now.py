#!/usr/bin/env python3
import sqlite3

db_path = "/home/pavel/dev/plexmem/data/plexmem.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check if synopsis column exists
    cursor.execute("PRAGMA table_info(quants)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'synopsis' not in columns:
        print("Adding synopsis column...")
        cursor.execute("ALTER TABLE quants ADD COLUMN synopsis VARCHAR(500);")
        conn.commit()
        print("✅ Synopsis column added!")
    else:
        print("✅ Synopsis column already exists")
    
except Exception as e:
    print(f"❌ Error: {e}")
    conn.rollback()
finally:
    conn.close()

