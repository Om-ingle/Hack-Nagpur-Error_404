#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from db.connection import get_db

print("Checking visits for AI summaries...")
print("=" * 70)

with get_db() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT id, patient_phone, ai_summary FROM visits ORDER BY id DESC LIMIT 5")
    visits = cursor.fetchall()
    
    if not visits:
        print("No visits found in database.")
    else:
        for visit in visits:
            visit_id = visit['id']
            phone = visit['patient_phone']
            summary = visit['ai_summary']
            
            print(f"\nVisit ID: {visit_id}")
            print(f"Phone: {phone}")
            if summary:
                print(f"AI Summary: {summary[:100]}...")
            else:
                print("AI Summary: ❌ NULL/EMPTY")
            print("-" * 70)
