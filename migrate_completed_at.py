import sys
sys.path.insert(0, '.')
from db.connection import get_db

with get_db() as conn:
    cursor = conn.cursor()
    cursor.execute('PRAGMA table_info(visits)')
    cols = [row[1] for row in cursor.fetchall()]
    
    if 'completed_at' not in cols:
        cursor.execute('ALTER TABLE visits ADD COLUMN completed_at TIMESTAMP')
        conn.commit()
        print('✅ Added completed_at column')
    else:
        print('✅ completed_at column already exists')
