import streamlit as st
import pandas as pd
from datetime import datetime
import json
from db.visit_repo import verify_doctor, get_next_visit_for_tier, mark_visit_completed, get_visit_by_id
from db.patient_repo import get_patient_by_phone

# Page config
st.set_page_config(
    page_title="AarogyaQueue - Doctor Portal",
    page_icon="👨‍⚕️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Premium Custom CSS for Doctor Portal
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Reset */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Hide Streamlit defaults */
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* App background */
    .stApp {
        background: linear-gradient(135deg, #f0f4f8 0%, #e2e8f0 100%);
    }
    
    /* Doctor Header */
    .doctor-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 10px 30px rgba(30, 58, 95, 0.25);
    }
    
    .doctor-name {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }
    
    .doctor-role {
        opacity: 0.85;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    .live-badge {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        padding: 0.5rem 1.25rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 0.9rem;
        border: 1px solid rgba(255, 255, 255, 0.3);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    /* Patient Card */
    .patient-card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border-left: 5px solid #3b82f6;
        margin-bottom: 1rem;
    }
    
    .patient-name {
        font-size: 1.4rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }
    
    .token-badge {
        display: inline-block;
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    /* Queue Item */
    .queue-item {
        background: white;
        border-radius: 16px;
        padding: 1.25rem;
        margin-bottom: 0.75rem;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .queue-item:hover {
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
    }
    
    .risk-high {
        border-left: 4px solid #ef4444;
    }
    
    .risk-medium {
        border-left: 4px solid #f59e0b;
    }
    
    .risk-low {
        border-left: 4px solid #10b981;
    }
    
    .queue-token {
        font-weight: 700;
        font-size: 1.1rem;
        color: #1e293b;
    }
    
    .queue-score {
        font-size: 0.85rem;
        color: #64748b;
        margin-top: 0.25rem;
    }
    
    /* Section Title */
    .section-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1e293b;
        margin: 1.5rem 0 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e2e8f0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* AI Summary Box */
    .ai-summary {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        border-radius: 12px;
        padding: 1.25rem;
        border-left: 4px solid #3b82f6;
        margin: 1rem 0;
    }
    
    /* Emergency Alert */
    .emergency-alert {
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
        border: 2px solid #ef4444;
        border-radius: 12px;
        padding: 1rem;
        color: #991b1b;
        font-weight: 600;
        text-align: center;
        animation: flash 1s infinite;
    }
    
    @keyframes flash {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }
    
    /* Button Styling */
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 0.75rem 1.5rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.35) !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.45) !important;
    }
    
    /* Input Styling */
    .stTextArea textarea, .stTextInput input {
        border-radius: 12px !important;
        border: 2px solid #e2e8f0 !important;
        padding: 0.75rem 1rem !important;
    }
    
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15) !important;
    }
    
    /* Select Box */
    .stSelectbox > div > div {
        border-radius: 12px !important;
    }
    
    /* Empty State */
    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
        color: #94a3b8;
    }
    
    .empty-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }
    
    /* Login Card */
    .login-card {
        background: white;
        border-radius: 24px;
        padding: 3rem;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
        max-width: 400px;
        margin: 2rem auto;
    }
    
    .login-title {
        font-size: 1.75rem;
        font-weight: 800;
        color: #1e293b;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .login-subtitle {
        color: #64748b;
        text-align: center;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Session State
if 'doctor_auth' not in st.session_state:
    st.session_state.doctor_auth = False
if 'doctor_info' not in st.session_state:
    st.session_state.doctor_info = None

def login_page():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown("""
            <div style="text-align: center; margin-bottom: 2rem;">
                <div style="font-size: 3rem; margin-bottom: 0.5rem;">👨‍⚕️</div>
                <div class="login-title">Doctor Portal</div>
                <div class="login-subtitle">Enter your credentials to access the queue</div>
            </div>
        """, unsafe_allow_html=True)
        
        role = st.selectbox("Select Your Role", ["JUNIOR", "SENIOR"])
        st.write("")
        pin = st.text_input("Access PIN", type="password", placeholder="Enter your 4-digit PIN")
        
        st.write("")
        st.write("")
        
        if st.button("🔓 Login", type="primary", use_container_width=True):
            try:
                doctor = verify_doctor(role, pin)
                
                if doctor:
                    st.session_state.doctor_auth = True
                    st.session_state.doctor_info = doctor
                    st.success(f"Welcome, Dr. {doctor['name']}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials. Please try again.")
            except Exception as e:
                st.error(f"❌ Login failed: {str(e)}")
        
        st.markdown('</div>', unsafe_allow_html=True)

def get_queue(tier):
    try:
        from db.connection import get_db
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
    except Exception as e:
        st.error(f"Error fetching queue: {e}")
        return []

def complete_visit(visit_id, diagnosis, prescription):
    try:
        mark_visit_completed(visit_id, diagnosis)
        return True
    except Exception as e:
        st.error(f"Error completing visit: {e}")
        return False

def dashboard():
    doc = st.session_state.doctor_info
    
    # Header
    st.markdown(f"""
    <div class="doctor-header">
        <div>
            <div class="doctor-name">Dr. {doc['name']}</div>
            <div class="doctor-role">{doc['role_tier']} Resident</div>
        </div>
        <div class="live-badge">🟢 Live Queue</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Refresh button
    col_refresh, col_spacer = st.columns([1, 5])
    with col_refresh:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    # Main Content
    queue = get_queue(doc['role_tier'])
    
    col1, col2 = st.columns([1, 2], gap="large")
    
    with col1:
        st.markdown(f"""
            <div class="section-title">
                📋 Waiting Queue ({len(queue)} patients)
            </div>
        """, unsafe_allow_html=True)
        
        if not queue:
            st.markdown("""
                <div class="empty-state">
                    <div class="empty-icon">🎉</div>
                    <div>No patients in queue!</div>
                </div>
            """, unsafe_allow_html=True)
        
        for i, patient in enumerate(queue):
            visit_id = patient['id']
            score = patient['risk_score']
            
            # Determine risk level
            if score > 0.7:
                risk_class = "risk-high"
                risk_text = "High Risk"
            elif score > 0.4:
                risk_class = "risk-medium"
                risk_text = "Medium Risk"
            else:
                risk_class = "risk-low"
                risk_text = "Low Risk"
            
            with st.container():
                st.markdown(f"""
                    <div class="queue-item {risk_class}">
                        <div class="queue-token">🎫 Token #{visit_id:08d}</div>
                        <div class="queue-score">{risk_text} • Score: {score:.2f}</div>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Select Patient", key=f"btn_{visit_id}", use_container_width=True):
                    st.session_state.current_patient = patient
                    st.rerun()
    
    with col2:
        if 'current_patient' in st.session_state and st.session_state.current_patient:
            p = st.session_state.current_patient
            
            st.markdown('<div class="section-title">🏥 Current Consultation</div>', unsafe_allow_html=True)
            
            # Patient Card
            st.markdown(f"""
                <div class="patient-card">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <div class="patient-name">{p.get('patient_name') or 'Unknown Patient'}</div>
                            <div style="color: #64748b; margin-top: 0.25rem;">YOB: {p.get('patient_yob', 'N/A')}</div>
                        </div>
                        <div class="token-badge">Token: {p['id']:08d}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # AI Summary
            st.markdown('<div class="section-title">🤖 AI Analysis</div>', unsafe_allow_html=True)
            st.markdown(f"""
                <div class="ai-summary">
                    Risk Score: {p.get('risk_score', 0):.2f} | Risk Level: {p.get('risk_level', 'UNKNOWN')}
                </div>
            """, unsafe_allow_html=True)
            
            # Emergency Check
            if p.get('symptoms_list'):
                try:
                    symptoms_text = p.get('symptoms_raw', '')
                    if any(w in symptoms_text.lower() for w in ['heart attack', 'stroke', 'bleeding', 'unconscious', 'chest pain']):
                        st.markdown("""
                            <div class="emergency-alert">
                                🚨 EMERGENCY KEYWORDS DETECTED - PRIORITIZE THIS PATIENT
                            </div>
                        """, unsafe_allow_html=True)
                except:
                    pass
            
            # Symptoms
            st.markdown('<div class="section-title">🗣️ Reported Symptoms</div>', unsafe_allow_html=True)
            st.info(p.get('symptoms_raw', 'No symptoms recorded'))
            
            st.divider()
            
            # Doctor Actions
            st.markdown('<div class="section-title">📝 Diagnosis & Treatment</div>', unsafe_allow_html=True)
            
            diagnosis = st.text_area("Doctor's Notes / Diagnosis", height=100, placeholder="Enter your diagnosis...")
            prescription = st.text_area("Prescription", height=100, placeholder="Medication name, dosage, frequency...")
            
            st.write("")
            
            col_complete, col_skip = st.columns(2)
            
            with col_complete:
                if st.button("✅ Complete Visit", type="primary", use_container_width=True):
                    if diagnosis:
                        if complete_visit(p['id'], diagnosis, prescription):
                            st.success("✅ Visit completed successfully!")
                            del st.session_state.current_patient
                            st.rerun()
                    else:
                        st.warning("⚠️ Please enter a diagnosis before completing.")
            
            with col_skip:
                if st.button("⏭️ Skip / Release", use_container_width=True):
                    del st.session_state.current_patient
                    st.rerun()
        
        else:
            st.markdown("""
                <div class="empty-state">
                    <div class="empty-icon">🩺</div>
                    <div style="font-size: 1.1rem;">Select a patient from the queue</div>
                    <div style="margin-top: 0.5rem; font-size: 0.9rem;">to start consultation</div>
                </div>
            """, unsafe_allow_html=True)
    
    # Logout in sidebar
    with st.sidebar:
        st.write("")
        st.write("")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.doctor_auth = False
            st.session_state.doctor_info = None
            if 'current_patient' in st.session_state:
                del st.session_state.current_patient
            st.rerun()

def main():
    if not st.session_state.doctor_auth:
        login_page()
    else:
        dashboard()

if __name__ == "__main__":
    main()
