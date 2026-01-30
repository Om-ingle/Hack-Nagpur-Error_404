#!/usr/bin/env python3
"""
Add completed_at column to existing visits table
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.connection import get_db

def migrate():
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check if column exists
        cursor.execute("PRAGMA table_info(visits)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'completed_at' not in columns:
            print("Adding completed_at column...")
            cursor.execute("ALTER TABLE visits ADD COLUMN completed_at TIMESTAMP")
            conn.commit()
            print("✅ Migration completed!")
        else:
            print("✅ completed_at column already exists.")

if __name__ == "__main__":
    migrate()
