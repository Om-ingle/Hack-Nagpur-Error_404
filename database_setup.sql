-- Telemedicine Queue Optimizer Database Setup
-- Run this SQL in your Supabase SQL Editor

-- Create patients table
CREATE TABLE IF NOT EXISTS patients (
    phone_number TEXT PRIMARY KEY,
    yob_pin INTEGER NOT NULL,
    full_name TEXT,
    chronic_history TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create doctors table
CREATE TABLE IF NOT EXISTS doctors (
    doctor_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    role_tier TEXT CHECK (role_tier IN ('JUNIOR', 'SENIOR')),
    pin_code TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create visits table
CREATE TABLE IF NOT EXISTS visits (
    visit_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_phone TEXT REFERENCES patients(phone_number),
    symptoms_raw TEXT NOT NULL,
    symptoms_extracted JSON,
    severity_score FLOAT CHECK (severity_score >= 0.0 AND severity_score <= 1.0),
    assigned_tier TEXT CHECK (assigned_tier IN ('JUNIOR', 'SENIOR')),
    status TEXT DEFAULT 'WAITING' CHECK (status IN ('WAITING', 'IN_PROGRESS', 'COMPLETED')),
    ai_summary TEXT,
    doctor_notes TEXT,
    prescription TEXT,
    doctor_id INTEGER REFERENCES doctors(doctor_id),
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- Insert sample doctors for testing
INSERT INTO doctors (name, role_tier, pin_code) VALUES 
('Dr. Priya Sharma', 'SENIOR', '1234'),
('Dr. Amit Kumar', 'JUNIOR', '5678'),
('Dr. Sunita Patel', 'SENIOR', '9999')
ON CONFLICT DO NOTHING;

-- Verify tables were created
SELECT 'Doctors table' as table_name, COUNT(*) as record_count FROM doctors
UNION ALL
SELECT 'Patients table' as table_name, COUNT(*) as record_count FROM patients
UNION ALL
SELECT 'Visits table' as table_name, COUNT(*) as record_count FROM visits;