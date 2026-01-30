from db.connection import get_db

def get_patient_by_phone(phone_number):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM patients WHERE phone_number = ?', (phone_number,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

def create_patient(phone_number, yob, name=None):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO patients (phone_number, yob, name) VALUES (?, ?, ?)',
            (phone_number, yob, name)
        )
        conn.commit()
        return get_patient_by_phone(phone_number)

def verify_patient(phone_number, yob):
    patient = get_patient_by_phone(phone_number)
    if patient and patient['yob'] == yob:
        return patient
    return None

def update_patient_name(phone_number, name):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE patients SET name = ? WHERE phone_number = ?',
            (name, phone_number)
        )
        conn.commit()

def get_all_patients():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM patients')
        return [dict(row) for row in cursor.fetchall()]
