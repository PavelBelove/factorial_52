#!/usr/bin/env python3
"""
Migration script to add characters table to the database.
Run this after adding CharacterDB model.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from core.database.models import Base, CharacterDB
from core.config import settings

def add_characters_table():
    """Add characters table to database"""
    engine = create_engine(settings.database_url, echo=True)
    
    print("Creating characters table...")
    CharacterDB.__table__.create(engine, checkfirst=True)
    print("✅ Characters table created successfully!")

if __name__ == "__main__":
    add_characters_table()

