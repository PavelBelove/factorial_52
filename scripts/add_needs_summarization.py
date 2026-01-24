"""
Add needs_summarization field to quants table.
"""
import sqlite3
from pathlib import Path

def run_migration():
    """Add needs_summarization column to quants table."""
    # Get database path
    db_path = Path(__file__).parent.parent / "data" / "plexmem.db"
    
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(quants)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'needs_summarization' in columns:
            print("✓ Column 'needs_summarization' already exists")
            return
        
        # Add the column
        cursor.execute("""
            ALTER TABLE quants 
            ADD COLUMN needs_summarization BOOLEAN DEFAULT 0
        """)
        
        conn.commit()
        print("✓ Added 'needs_summarization' column to quants table")
        
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()

