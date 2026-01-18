#!/usr/bin/env python3
"""
Script to clear the PlexMem database for testing.
Removes all data and recreates tables.
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.database.db_manager import DatabaseManager
from core.database.models import Base
from sqlalchemy import text


def clear_database():
    """Clear all data from database and recreate tables."""
    print("🗑️  Clearing PlexMem database...")
    
    db = DatabaseManager()
    
    # Drop all tables
    print("   Dropping all tables...")
    Base.metadata.drop_all(bind=db.engine)
    
    # Recreate all tables
    print("   Recreating tables...")
    Base.metadata.create_all(bind=db.engine)
    
    # Verify tables are empty
    with db.get_session() as session:
        users_count = session.execute(text("SELECT COUNT(*) FROM users")).scalar()
        sessions_count = session.execute(text("SELECT COUNT(*) FROM sessions")).scalar()
        quants_count = session.execute(text("SELECT COUNT(*) FROM quants")).scalar()
        turns_count = session.execute(text("SELECT COUNT(*) FROM turns")).scalar()
        
        print(f"\n✅ Database cleared successfully!")
        print(f"   Users: {users_count}")
        print(f"   Sessions: {sessions_count}")
        print(f"   Quants: {quants_count}")
        print(f"   Turns: {turns_count}")


def main():
    """Main function."""
    print("="*60)
    print("PlexMem Database Clear Tool")
    print("="*60)
    print()
    
    # Confirm action
    response = input("⚠️  This will DELETE ALL DATA in the database.\n   Continue? (yes/no): ")
    
    if response.lower() not in ['yes', 'y']:
        print("❌ Cancelled.")
        return
    
    print()
    clear_database()
    print()
    print("🎮 Ready for a fresh start!")
    print("   Run /start in Telegram bot to begin a new game.")
    print()


if __name__ == "__main__":
    main()

