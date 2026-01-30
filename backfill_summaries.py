#!/usr/bin/env python3
"""
Backfill AI summaries for existing visits that don't have them
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from db.connection import get_db
from db.patient_repo import get_patient_by_phone
from db.visit_repo import get_previous_visits
from ai.summary import generate_doctor_summary
from datetime import datetime

print("=" * 70)
print("BACKFILLING AI SUMMARIES FOR EXISTING VISITS")
print("=" * 70)

with get_db() as conn:
    cursor = conn.cursor()
    
    # Find visits without AI summary
    cursor.execute("""
        SELECT v.*, p.yob 
        FROM visits v
        JOIN patients p ON v.patient_phone = p.phone_number
        WHERE v.ai_summary IS NULL OR v.ai_summary = ''
        ORDER BY v.id
    """)
    visits_without_summary = cursor.fetchall()
    
    if not visits_without_summary:
        print("\n✅ All visits already have AI summaries!")
        print("=" * 70)
        sys.exit(0)
    
    print(f"\nFound {len(visits_without_summary)} visits without AI summaries")
    print("Generating summaries...\n")
    
    for visit in visits_without_summary:
        visit_dict = dict(visit)
        visit_id = visit_dict['id']
        patient_phone = visit_dict['patient_phone']
        symptoms = visit_dict['symptoms_raw']
        risk_level = visit_dict.get('risk_level', 'UNKNOWN')
        yob = visit_dict.get('yob')
        
        # Calculate age
        current_year = datetime.now().year
        age = current_year - yob if yob else 30
        
        print(f"Visit #{visit_id}: ", end="")
        
        try:
            # Get previous visits (excluding current one)
            cursor.execute("""
                SELECT * FROM visits 
                WHERE patient_phone = ? AND id < ? AND status = 'COMPLETED'
                ORDER BY created_at DESC LIMIT 3
            """, (patient_phone, visit_id))
            previous_visits = [dict(row) for row in cursor.fetchall()]
            
            # Generate summary
            summary = generate_doctor_summary(
                current_symptoms=symptoms,
                patient_age=age,
                risk_level=risk_level,
                previous_visits=previous_visits
            )
            
            # Update visit
            cursor.execute("""
                UPDATE visits SET ai_summary = ? WHERE id = ?
            """, (summary, visit_id))
            
            print(f"✅ Summary generated ({len(summary)} chars)")
            
        except Exception as e:
            print(f"❌ Failed: {e}")
    
    conn.commit()
    print("\n" + "=" * 70)
    print("BACKFILL COMPLETE!")
    print("=" * 70)
    print("\nRefresh the doctor dashboard to see AI summaries.")
