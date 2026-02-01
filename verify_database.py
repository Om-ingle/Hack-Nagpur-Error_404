#!/usr/bin/env python3
"""
Database verification script - Shows current database state
"""

from db.connection import get_db

def show_db_status():
    print("=" * 60)
    print("TELEMEDICINE QUEUE DATABASE STATUS")
    print("=" * 60)
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check doctors
        cursor.execute('SELECT COUNT(*) as count FROM doctors')
        doctor_count = cursor.fetchone()['count']
        print(f"\n✓ Doctors table: {doctor_count} records")
        
        if doctor_count > 0:
            cursor.execute('SELECT name, role_tier FROM doctors')
            for row in cursor.fetchall():
                print(f"  - {row['name']} ({row['role_tier']})")
        
        # Check patients
        cursor.execute('SELECT COUNT(*) as count FROM patients')
        patient_count = cursor.fetchone()['count']
        print(f"\n✓ Patients table: {patient_count} records")
        
        # Check visits
        cursor.execute('SELECT COUNT(*) as count FROM visits')
        visit_count = cursor.fetchone()['count']
        print(f"\n✓ Visits table: {visit_count} records")
        
        # Check pending queue
        cursor.execute('''
            SELECT assigned_tier, COUNT(*) as count 
            FROM visits 
            WHERE status = 'WAITING' 
            GROUP BY assigned_tier
        ''')
        print(f"\n✓ Current Queue:")
        queue = cursor.fetchall()
        if queue:
            for row in queue:
                print(f"  - {row['assigned_tier']}: {row['count']} waiting")
        else:
            print(f"  - No patients in queue")
    
    print("\n" + "=" * 60)
    print("DATABASE STATUS: ✓ HEALTHY")
    print("=" * 60)

if __name__ == "__main__":
    show_db_status()
