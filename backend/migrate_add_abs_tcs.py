#!/usr/bin/env python3
"""
Migration script to add ABS and TCS columns to telemetrysample table.

Usage:
    python migrate_add_abs_tcs.py
"""
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from app.db import engine
from app.config import settings

def migrate():
    """Add abs and tcs columns to telemetrysample table."""
    print(f"Connecting to database: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")
    
    with engine.begin() as conn:
        # Check if columns already exist
        check_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'telemetrysample' 
            AND column_name IN ('abs', 'tcs')
        """)
        result = conn.execute(check_query)
        existing_columns = {row[0] for row in result}
        
        if 'abs' in existing_columns and 'tcs' in existing_columns:
            print("✓ Columns 'abs' and 'tcs' already exist. Migration not needed.")
            return
        
        # Add abs column if it doesn't exist
        if 'abs' not in existing_columns:
            print("Adding 'abs' column...")
            conn.execute(text("""
                ALTER TABLE telemetrysample 
                ADD COLUMN abs BOOLEAN NOT NULL DEFAULT FALSE
            """))
            print("✓ Added 'abs' column")
        else:
            print("✓ Column 'abs' already exists")
        
        # Add tcs column if it doesn't exist
        if 'tcs' not in existing_columns:
            print("Adding 'tcs' column...")
            conn.execute(text("""
                ALTER TABLE telemetrysample 
                ADD COLUMN tcs BOOLEAN NOT NULL DEFAULT FALSE
            """))
            print("✓ Added 'tcs' column")
        else:
            print("✓ Column 'tcs' already exists")
        
        print("\n✓ Migration completed successfully!")

if __name__ == "__main__":
    try:
        migrate()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

