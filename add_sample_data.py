#!/usr/bin/env python3
"""
Add sample patients and visits for demo purposes
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.patient_repo import create_patient
from db.visit_repo import create_visit
from db.connection import get_db
import json

print("=" * 70)
print("ADDING SAMPLE PATIENTS AND VISITS FOR DEMO")
print("=" * 70)

# Sample patients with visits
sample_data = [
    {
        "phone": "9876543210",
        "yob": 1978,
        "name": "Rajesh Kumar",
        "symptoms": "severe chest pain radiating to left arm, sweating",
        "risk_score": 0.85,
        "risk_level": "HIGH",
        "tier": "SENIOR",
        "status": "WAITING",
        "ai_summary": "46-year-old male presenting with severe chest pain radiating to left arm and sweating.\nNo previous visit history on record.\nRisk assessment indicates high urgency level.\nImmediate medical evaluation strongly recommended."
    },
    {
        "phone": "9876543211",
        "yob": 1992,
        "name": "Priya Sharma",
        "symptoms": "persistent headache for 3 days, dizziness, blurred vision",
        "risk_score": 0.72,
        "risk_level": "HIGH",
        "tier": "SENIOR",
        "status": "WAITING",
        "ai_summary": "32-year-old female presenting with persistent headache for 3 days, dizziness, and blurred vision.\nNo previous visit history on record.\nRisk assessment indicates high urgency level.\nPrompt medical evaluation recommended."
    },
    {
        "phone": "9876543212",
        "yob": 1985,
        "name": "Amit Patel",
        "symptoms": "high fever 102°F, severe body ache, cough",
        "risk_score": 0.55,
        "risk_level": "MEDIUM",
        "tier": "SENIOR",
        "status": "COMPLETED",
        "ai_summary": "39-year-old male presenting with high fever, severe body ache, and cough.\nNo previous visit history on record.\nRisk assessment indicates moderate urgency level.\nPrompt medical evaluation recommended.",
        "doctor_notes": "Viral fever. Prescribed paracetamol 500mg TDS, rest for 3 days. Follow up if fever persists beyond 3 days."
    },
    {
        "phone": "9876543213",
        "yob": 1995,
        "name": "Sneha Reddy",
        "symptoms": "stomach pain, nausea, vomiting",
        "risk_score": 0.48,
        "risk_level": "MEDIUM",
        "tier": "SENIOR",
        "status": "COMPLETED",
        "ai_summary": "29-year-old female presenting with stomach pain, nausea, and vomiting.\nNo previous visit history on record.\nRisk assessment indicates moderate urgency level.\nPrompt medical evaluation recommended.",
        "doctor_notes": "Gastroenteritis. Prescribed ORS, domperidone 10mg TDS, avoid spicy food. Review in 2 days if symptoms worsen."
    },
    {
        "phone": "9876543214",
        "yob": 1960,
        "name": "Suresh Iyer",
        "symptoms": "difficulty breathing, wheezing, chest tightness",
        "risk_score": 0.78,
        "risk_level": "HIGH",
        "tier": "SENIOR",
        "status": "COMPLETED",
        "ai_summary": "64-year-old patient presenting with difficulty breathing, wheezing, and chest tightness.\nNo previous visit history on record.\nRisk assessment indicates high urgency level.\nImmediate medical evaluation strongly recommended.",
        "doctor_notes": "Acute asthma exacerbation. Nebulization given, prescribed salbutamol inhaler, prednisolone 40mg OD for 5 days. Emergency review if breathing worsens."
    }
]

created_count = 0
for data in sample_data:
    try:
        # Create or get patient
        from db.patient_repo import get_patient_by_phone
        patient = get_patient_by_phone(data["phone"])
        
        if not patient:
            create_patient(data["phone"], data["yob"], data["name"])
            print(f"✅ Created patient: {data['name']} ({data['phone']})")
        else:
            print(f"ℹ️  Patient exists: {data['name']} ({data['phone']})")
        
        # Create visit
        visit_id = create_visit(
            patient_phone=data["phone"],
            symptoms_raw=data["symptoms"],
            symptoms_list=json.dumps([data["symptoms"]]),
            risk_score=data["risk_score"],
            risk_level=data["risk_level"],
            assigned_tier=data["tier"],
            ai_summary=data["ai_summary"]
        )
        
        # If completed, mark it as completed
        if data["status"] == "COMPLETED":
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE visits 
                    SET status = 'COMPLETED', 
                        doctor_notes = ?,
                        completed_at = datetime('now', '-' || (? || ' hours'))
                    WHERE id = ?
                """, (data["doctor_notes"], created_count, visit_id))
                conn.commit()
            print(f"   📋 Visit #{visit_id} - COMPLETED")
        else:
            print(f"   ⏳ Visit #{visit_id} - WAITING")
        
        created_count += 1
        
    except Exception as e:
        print(f"❌ Error creating {data['name']}: {e}")

print("\n" + "=" * 70)
print(f"SAMPLE DATA CREATION COMPLETE!")
print("=" * 70)
print(f"\n✅ Created {created_count} patients with visits")
print("\nYou can now:")
print("- Login as SENIOR doctor (PIN: 1234)")
print("- See 2 patients in WAITING queue")
print("- See 3 patients in HISTORY")
print("\nDoctor Portal: http://localhost:8502")
print("=" * 70)
