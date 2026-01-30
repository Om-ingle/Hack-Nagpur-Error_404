#!/usr/bin/env python3
"""
Database migration script to add ai_summary column to existing visits table
"""
import sqlite3
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.connection import get_db

def migrate_database():
    """Add ai_summary column if it doesn't exist"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Check if column exists
            cursor.execute("PRAGMA table_info(visits)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'ai_summary' not in columns:
                print("Adding ai_summary column to visits table...")
                cursor.execute("ALTER TABLE visits ADD COLUMN ai_summary TEXT")
                conn.commit()
                print("✅ Migration completed successfully!")
            else:
                print("✅ ai_summary column already exists. No migration needed.")
                
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise

if __name__ == "__main__":
    migrate_database()
