from db.connection import get_db

def create_tables():
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                phone_number TEXT PRIMARY KEY,
                yob INTEGER NOT NULL,
                name TEXT,
                chronic_history TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS visits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_phone TEXT NOT NULL,
                symptoms_raw TEXT NOT NULL,
                symptoms_list TEXT,
                risk_score REAL,
                risk_level TEXT,
                assigned_tier TEXT,
                status TEXT DEFAULT 'WAITING',
                ai_summary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                doctor_notes TEXT,
                FOREIGN KEY (patient_phone) REFERENCES patients(phone_number)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS doctors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                role_tier TEXT NOT NULL,
                pin_code TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()

def insert_sample_doctors():
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM doctors')
        if cursor.fetchone()[0] == 0:
            doctors = [
                ('Dr. Priya Sharma', 'SENIOR', '1234'),
                ('Dr. Amit Kumar', 'JUNIOR', '5678'),
                ('Dr. Sunita Patel', 'SENIOR', '9999')
            ]
            cursor.executemany(
                'INSERT INTO doctors (name, role_tier, pin_code) VALUES (?, ?, ?)',
                doctors
            )
            conn.commit()

def initialize_database():
    create_tables()
    insert_sample_doctors()
    print("[OK] Database initialized successfully!")
