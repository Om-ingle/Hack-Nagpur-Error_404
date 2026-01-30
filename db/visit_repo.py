import json
from db.connection import get_db

def create_visit(patient_phone, symptoms_raw, symptoms_list, risk_score, risk_level, assigned_tier, ai_summary=None):
    with get_db() as conn:
        cursor = conn.cursor()
        symptoms_json = json.dumps(symptoms_list) if isinstance(symptoms_list, list) else symptoms_list
        cursor.execute('''
            INSERT INTO visits (patient_phone, symptoms_raw, symptoms_list, risk_score, risk_level, assigned_tier, status, ai_summary)
            VALUES (?, ?, ?, ?, ?, ?, 'WAITING', ?)
        ''', (patient_phone, symptoms_raw, symptoms_json, risk_score, risk_level, assigned_tier, ai_summary))
        conn.commit()
        return cursor.lastrowid

def get_next_visit_for_tier(tier):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM visits 
            WHERE assigned_tier = ? AND status = 'WAITING'
            ORDER BY risk_score DESC, created_at ASC
            LIMIT 1
        ''', (tier,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

def mark_visit_completed(visit_id, doctor_notes):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE visits 
            SET status = 'COMPLETED', doctor_notes = ?, completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (doctor_notes, visit_id))
        conn.commit()

def get_queue_position(assigned_tier):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) as position FROM visits 
            WHERE assigned_tier = ? AND status = 'WAITING'
        ''', (assigned_tier,))
        result = cursor.fetchone()
        return result['position'] if result else 0

def verify_doctor(role_tier, pin_code):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM doctors 
            WHERE role_tier = ? AND pin_code = ?
        ''', (role_tier, pin_code))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

def get_visit_by_id(visit_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM visits WHERE id = ?', (visit_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

def get_previous_visits(patient_phone, limit=5):
    """Get previous completed visits for a patient"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM visits 
            WHERE patient_phone = ? AND status = 'COMPLETED'
            ORDER BY created_at DESC
            LIMIT ?
        ''', (patient_phone, limit))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_waiting_visits(tier):
    """Get all waiting visits for a specific tier (for live queue)"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT v.*, p.name as patient_name, p.yob as patient_yob
            FROM visits v
            JOIN patients p ON v.patient_phone = p.phone_number
            WHERE v.assigned_tier = ? AND v.status = 'WAITING'
            ORDER BY v.risk_score DESC, v.created_at ASC
        ''', (tier,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_completed_visits(tier=None, limit=20):
    """Get recently completed visits (consultation history)"""
    with get_db() as conn:
        cursor = conn.cursor()
        if tier:
            cursor.execute('''
                SELECT v.*, p.name as patient_name, p.yob as patient_yob
                FROM visits v
                JOIN patients p ON v.patient_phone = p.phone_number
                WHERE v.assigned_tier = ? AND v.status = 'COMPLETED'
                ORDER BY v.completed_at DESC, v.id DESC
                LIMIT ?
            ''', (tier, limit))
        else:
            cursor.execute('''
                SELECT v.*, p.name as patient_name, p.yob as patient_yob
                FROM visits v
                JOIN patients p ON v.patient_phone = p.phone_number
                WHERE v.status = 'COMPLETED'
                ORDER BY v.completed_at DESC, v.id DESC
                LIMIT ?
            ''', (limit,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
