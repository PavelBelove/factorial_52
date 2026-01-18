#!/usr/bin/env python3
"""
Migration script: Add synopsis column to quants table.
Run this after updating the code with synopsis support.
"""

import sqlite3
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import settings

def migrate():
    """Add synopsis column to quants table if it doesn't exist."""
    db_path = settings.database_path
    
    print(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if synopsis column exists
        cursor.execute("PRAGMA table_info(quants)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'synopsis' in columns:
            print("✅ Column 'synopsis' already exists. No migration needed.")
            return
        
        # Add synopsis column
        print("Adding 'synopsis' column to quants table...")
        cursor.execute("""
            ALTER TABLE quants 
            ADD COLUMN synopsis VARCHAR(500)
        """)
        
        conn.commit()
        print("✅ Migration successful! Column 'synopsis' added to quants table.")
        
    except sqlite3.Error as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()

