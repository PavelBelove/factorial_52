#!/usr/bin/env python3
"""
Migration: Add translator and cost tracking fields to turns table
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from core.config import settings

def migrate():
    """Add new fields to turns table."""
    engine = create_engine(settings.database_url)
    
    with engine.connect() as conn:
        # Check if columns exist
        result = conn.execute(text("PRAGMA table_info(turns)"))
        columns = [row[1] for row in result.fetchall()]
        
        # Add translated_json if not exists
        if "translated_json" not in columns:
            print("Adding translated_json column...")
            conn.execute(text("ALTER TABLE turns ADD COLUMN translated_json TEXT"))
            conn.commit()
            print("✅ translated_json added")
        else:
            print("✅ translated_json already exists")
        
        # Add cost fields if not exist
        cost_fields = [
            "cost_gm",
            "cost_quantizer",
            "cost_summarizer",
            "cost_translator",
            "cost_total"
        ]
        
        for field in cost_fields:
            if field not in columns:
                print(f"Adding {field} column...")
                conn.execute(text(f"ALTER TABLE turns ADD COLUMN {field} REAL DEFAULT 0.0"))
                conn.commit()
                print(f"✅ {field} added")
            else:
                print(f"✅ {field} already exists")
    
    print("\n✅ Migration complete!")

if __name__ == "__main__":
    migrate()

