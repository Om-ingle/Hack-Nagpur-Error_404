import streamlit as st
import os
from ai_processing import transcribe_audio, extract_patient_data, extract_from_text
from predict_risk import predict_risk_score
import json
from datetime import datetime
from db.patient_repo import get_patient_by_phone, create_patient, verify_patient, update_patient_name
from db.visit_repo import create_visit, get_queue_position

# Page config
st.set_page_config(
    page_title="AarogyaQueue - Patient",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Premium Custom CSS
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Reset & Base */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Hide Streamlit defaults */
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Beautiful gradient background */
    .stApp {
        background: linear-gradient(135deg, #e0f7fa 0%, #e8f5e9 50%, #f3e5f5 100%);
        min-height: 100vh;
    }
    
    /* Glassmorphism card base */
    .glass-card {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.5);
        border-radius: 24px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
        padding: 2.5rem;
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
        transform: translateY(-2px);
    }
    
    /* Login Container */
    .login-wrapper {
        max-width: 420px;
        margin: 3rem auto;
        text-align: center;
    }
    
    .logo-container {
        margin-bottom: 2rem;
    }
    
    .logo-icon {
        width: 80px;
        height: 80px;
        background: linear-gradient(135deg, #00897b 0%, #4db6ac 100%);
        border-radius: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 40px;
        margin: 0 auto 1rem;
        box-shadow: 0 8px 24px rgba(0, 137, 123, 0.3);
    }
    
    .brand-name {
        font-size: 1.5rem;
        font-weight: 700;
        color: #00695c;
        letter-spacing: -0.5px;
    }
    
    .login-title {
        font-size: 2rem;
        font-weight: 800;
        color: #1a1a2e;
        margin: 1.5rem 0 0.5rem;
        letter-spacing: -1px;
    }
    
    .login-subtitle {
        color: #64748b;
        font-size: 0.95rem;
        margin-bottom: 2rem;
        line-height: 1.5;
    }
    
    /* Premium Input Styling */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.9) !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 14px !important;
        padding: 1rem 1.25rem !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
        color: #1e293b !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #00897b !important;
        box-shadow: 0 0 0 4px rgba(0, 137, 123, 0.15) !important;
        background: white !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #94a3b8 !important;
        font-weight: 400 !important;
    }
    
    /* Premium Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #00897b 0%, #00695c 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 0.875rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        letter-spacing: 0.3px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0, 137, 123, 0.35) !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #00695c 0%, #004d40 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(0, 137, 123, 0.45) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* Voice Input Screen */
    .voice-section {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 2rem;
        text-align: center;
        border: 1px solid rgba(0, 137, 123, 0.1);
    }
    
    .mic-container {
        width: 160px;
        height: 160px;
        border-radius: 50%;
        background: linear-gradient(135deg, #e0f2f1 0%, #b2dfdb 100%);
        border: 4px solid #80cbc4;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 1.5rem auto;
        position: relative;
        animation: pulse-ring 2s ease-out infinite;
    }
    
    @keyframes pulse-ring {
        0% { box-shadow: 0 0 0 0 rgba(0, 137, 123, 0.4); }
        70% { box-shadow: 0 0 0 15px rgba(0, 137, 123, 0); }
        100% { box-shadow: 0 0 0 0 rgba(0, 137, 123, 0); }
    }
    
    .mic-icon {
        font-size: 60px;
    }
    
    .mic-label {
        color: #00695c;
        font-weight: 600;
        font-size: 1rem;
        margin-top: 0.5rem;
    }
    
    /* Form Card */
    .form-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
    }
    
    .form-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 1.5rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid #e2e8f0;
    }
    
    /* Token Success Screen */
    .token-success {
        text-align: center;
        padding: 3rem 2rem;
    }
    
    .success-icon {
        width: 100px;
        height: 100px;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 1.5rem;
        font-size: 50px;
        box-shadow: 0 8px 30px rgba(16, 185, 129, 0.35);
        animation: scale-in 0.5s ease-out;
    }
    
    @keyframes scale-in {
        0% { transform: scale(0); opacity: 0; }
        100% { transform: scale(1); opacity: 1; }
    }
    
    .token-label {
        color: #64748b;
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 0.5rem;
    }
    
    .token-number {
        font-size: 4.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.1;
        margin-bottom: 1rem;
    }
    
    .clinic-badge {
        display: inline-block;
        background: linear-gradient(135deg, #00897b 0%, #00695c 100%);
        color: white;
        padding: 0.75rem 2rem;
        border-radius: 50px;
        font-weight: 700;
        font-size: 1.1rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0, 137, 123, 0.3);
    }
    
    .wait-info {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-radius: 16px;
        padding: 1.25rem 2rem;
        margin: 1.5rem auto;
        max-width: 350px;
        border: 1px solid #fbbf24;
    }
    
    .wait-label {
        color: #92400e;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .wait-time {
        color: #78350f;
        font-size: 2rem;
        font-weight: 800;
        margin-top: 0.25rem;
    }
    
    .queue-position {
        background: rgba(0, 137, 123, 0.1);
        border-radius: 12px;
        padding: 1rem;
        margin-top: 1.5rem;
        display: inline-block;
    }
    
    .queue-text {
        color: #00695c;
        font-weight: 600;
        font-size: 1rem;
    }
    
    /* Header styling */
    .app-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 2rem;
        padding: 1rem 0;
    }
    
    .header-logo {
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, #00897b 0%, #4db6ac 100%);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        box-shadow: 0 4px 12px rgba(0, 137, 123, 0.25);
    }
    
    .header-text {
        font-weight: 700;
        font-size: 1.25rem;
        color: #00695c;
    }
    
    /* Divider */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
        margin: 1.5rem 0;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(0, 137, 123, 0.05) !important;
        border-radius: 10px !important;
    }
    
    /* Audio input styling */
    .stAudioInput > div {
        border-radius: 14px !important;
    }
    
    /* Success/Error messages */
    .stSuccess, .stInfo, .stWarning, .stError {
        border-radius: 12px !important;
    }
    
    /* Labels */
    .stTextInput > label, .stNumberInput > label, .stTextArea > label {
        font-weight: 600 !important;
        color: #374151 !important;
        font-size: 0.95rem !important;
        margin-bottom: 0.5rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'patient_phone' not in st.session_state:
    st.session_state.patient_phone = None
if 'patient_data' not in st.session_state:
    st.session_state.patient_data = None
if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = None
if 'token_generated' not in st.session_state:
    st.session_state.token_generated = False
if 'form_name' not in st.session_state:
    st.session_state.form_name = ''
if 'form_age' not in st.session_state:
    st.session_state.form_age = 30
if 'form_symptoms' not in st.session_state:
    st.session_state.form_symptoms = ''
if 'processing_audio' not in st.session_state:
    st.session_state.processing_audio = False

def update_form_with_extracted_data(extracted):
    """Helper to update session state with extracted data - updates widget keys directly"""
    if not extracted:
        return
    
    # Update the widget keys directly - this is how Streamlit autofill works
    if 'name' in extracted and extracted['name'] and extracted['name'] != 'Unknown':
        st.session_state.name_field_input = extracted['name']
        st.session_state.form_name = extracted['name']
    
    if 'age' in extracted and extracted['age']:
        st.session_state.age_field_input = int(extracted['age'])
        st.session_state.form_age = int(extracted['age'])
    
    if 'symptoms' in extracted and extracted['symptoms']:
        symptoms_text = ', '.join(extracted['symptoms']) if isinstance(extracted['symptoms'], list) else str(extracted['symptoms'])
        st.session_state.symptoms_field_input = symptoms_text
        st.session_state.form_symptoms = symptoms_text

def header():
    st.markdown("""
        <div class="app-header">
            <div class="header-logo">🏥</div>
            <div class="header-text">AarogyaQueue</div>
        </div>
    """, unsafe_allow_html=True)

def show_login_screen():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
        
        # Logo and branding
        st.markdown("""
            <div class="logo-container">
                <div class="logo-icon">🏥</div>
                <div class="brand-name">AarogyaQueue</div>
            </div>
            <div class="login-title">Patient Check-In</div>
            <div class="login-subtitle">Enter your details to join the queue and get your token</div>
        """, unsafe_allow_html=True)
        
        # Form inputs
        phone = st.text_input("Phone Number", placeholder="Enter 10-digit phone number", max_chars=10, key="phone_input", label_visibility="collapsed")
        st.write("")
        yob = st.text_input("Year of Birth", placeholder="Enter year (e.g., 1990)", max_chars=4, type="password", key="yob_input", label_visibility="collapsed")
        
        st.write("")
        st.write("")
        
        if st.button("🚀 Check In", use_container_width=True):
            if len(phone) == 10 and len(yob) == 4:
                try:
                    yob_int = int(yob)
                    patient = get_patient_by_phone(phone)
                    
                    if patient:
                        if patient['yob'] == yob_int:
                            st.session_state.authenticated = True
                            st.session_state.patient_phone = phone
                            st.session_state.patient_data = patient
                            st.rerun()
                        else:
                            st.error("❌ Invalid credentials. Please check your details.")
                    else:
                        # New patient registration
                        new_patient = create_patient(phone, yob_int)
                        st.session_state.authenticated = True
                        st.session_state.patient_phone = phone
                        st.session_state.patient_data = new_patient
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("⚠️ Please enter valid phone number and year of birth")
        
        st.markdown('</div>', unsafe_allow_html=True)

def show_voice_input_screen():
    header()
    
    if not st.session_state.token_generated:
        col1, col2 = st.columns([1, 1.3], gap="large")
        
        with col1:
            st.markdown('<div class="voice-section">', unsafe_allow_html=True)
            
            st.markdown("""
                <div style="margin-bottom: 1rem;">
                    <h3 style="color: #1e293b; font-weight: 700; margin-bottom: 0.5rem;">Voice Input</h3>
                    <p style="color: #64748b; font-size: 0.9rem;">Describe your symptoms by speaking</p>
                </div>
                <div class="mic-container">
                    <span class="mic-icon">🎤</span>
                </div>
                <p class="mic-label">Tap below to start recording</p>
            """, unsafe_allow_html=True)
            
            audio_bytes = st.audio_input("Record your symptoms", label_visibility="collapsed")
            
            # Simple mechanism to prevent re-processing the same audio
            # We use the size of bytes as a proxy for "same audio" in this session context, or just check object identity if stable
            current_audio_id = hash(audio_bytes) if audio_bytes else None
            
            if audio_bytes and st.session_state.get('last_processed_audio_id') != current_audio_id:
                st.session_state.processing_audio = True
                st.session_state.last_processed_audio_id = current_audio_id
                
                with st.spinner("🔄 Processing your voice..."):
                    transcript = transcribe_audio(audio_bytes)
                    if transcript:
                        st.info(f"📝 Heard: \"{transcript}\"")
                        extracted = extract_patient_data(transcript)
                        
                        # Debug output to help diagnose autofill issues
                        st.write("Debug - Extracted Data:", extracted)
                        
                        if extracted and 'error' not in extracted:
                            st.session_state.extracted_data = extracted
                            update_form_with_extracted_data(extracted)
                            st.success("✅ Data extracted! Form updated.")
                            # Force a sleep briefly to let user see success before rerun
                            import time
                            time.sleep(1)
                
                st.session_state.processing_audio = False
                st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Text input option (collapsible)
            with st.expander("💬 Or type your symptoms instead"):
                text_input = st.text_area("Type symptoms here", height=100, key="text_symptoms_input")
                if st.button("📤 Process Text", key="process_text_btn"):
                    if text_input:
                        extracted = extract_patient_data(text_input)
                        st.write("Debug - Extracted Data:", extracted)
                        if extracted and 'error' not in extracted:
                            st.session_state.extracted_data = extracted
                            update_form_with_extracted_data(extracted)
                            st.success("✅ Data extracted!")
                            st.rerun()
        
        with col2:
            st.markdown('<div class="form-card">', unsafe_allow_html=True)
            st.markdown('<div class="form-title">📋 Patient Details</div>', unsafe_allow_html=True)
            
            # Form fields - use session state keys for autofill to work
            # Initialize widget keys if not present
            if 'name_field_input' not in st.session_state:
                st.session_state.name_field_input = st.session_state.form_name
            if 'age_field_input' not in st.session_state:
                st.session_state.age_field_input = st.session_state.form_age
            if 'symptoms_field_input' not in st.session_state:
                st.session_state.symptoms_field_input = st.session_state.form_symptoms
            
            name = st.text_input("Full Name", key="name_field_input", placeholder="Enter your full name")
            age = st.number_input("Age", min_value=1, max_value=120, key="age_field_input")
            symptoms = st.text_area("Symptoms Description", height=150, key="symptoms_field_input", placeholder="Describe your symptoms in detail...")
            
            st.write("")
            
            if st.button("✅ Submit & Get Token", use_container_width=True, type="primary"):
                if symptoms:
                    extracted_data = {
                        'name': name if name else 'Unknown',
                        'age': age,
                        'symptoms': [symptoms],
                        'emergency_detected': any(w in symptoms.lower() for w in ['heart attack', 'stroke', 'bleeding', 'unconscious', 'chest pain'])
                    }
                    
                    risk_score = predict_risk_score(symptoms, age)
                    assigned_tier = 'SENIOR' if risk_score > 0.7 else 'JUNIOR'
                    risk_level = 'HIGH' if risk_score > 0.7 else ('MEDIUM' if risk_score > 0.4 else 'LOW')
                    
                    # Update patient name
                    if name and name != st.session_state.patient_data.get('name'):
                        update_patient_name(st.session_state.patient_phone, name)
                    
                    # Create visit
                    symptoms_list = [symptoms]
                    visit_id = create_visit(
                        st.session_state.patient_phone,
                        symptoms,
                        json.dumps(symptoms_list),
                        float(risk_score),
                        risk_level,
                        assigned_tier
                    )
                    
                    # Calculate queue position
                    queue_position = get_queue_position(assigned_tier)
                    
                    st.session_state.token_data = {
                        'token': f"{visit_id:08d}",
                        'tier': assigned_tier,
                        'wait_time': queue_position * 8,
                        'queue_position': queue_position
                    }
                    st.session_state.token_generated = True
                    st.rerun()
                else:
                    st.error("⚠️ Please enter your symptoms to continue")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        # Token Success Screen
        token = st.session_state.token_data
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown('<div class="token-success">', unsafe_allow_html=True)
            
            # Success icon
            st.markdown('<div class="success-icon">✓</div>', unsafe_allow_html=True)
            
            # Token number
            st.markdown('<div class="token-label">Your Token Number</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="token-number">T-{token["token"][:4]}</div>', unsafe_allow_html=True)
            
            # Clinic assignment
            clinic_name = "Senior Doctor Clinic" if token['tier'] == 'SENIOR' else "Junior Doctor Clinic"
            st.markdown(f'<div class="clinic-badge">{clinic_name}</div>', unsafe_allow_html=True)
            
            # Wait time
            st.markdown(f'''
                <div class="wait-info">
                    <div class="wait-label">Estimated Wait Time</div>
                    <div class="wait-time">{token["wait_time"]} Minutes</div>
                </div>
            ''', unsafe_allow_html=True)
            
            # Queue position
            st.markdown(f'''
                <div class="queue-position">
                    <span class="queue-text">📊 Position in Queue: #{token.get("queue_position", 1)}</span>
                </div>
            ''', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.write("")
            st.write("")
            
            if st.button("🏠 Back to Home", use_container_width=True):
                # Reset session state
                st.session_state.authenticated = False
                st.session_state.token_generated = False
                st.session_state.form_name = ''
                st.session_state.form_age = 30
                st.session_state.form_symptoms = ''
                st.session_state.extracted_data = None
                st.rerun()

def main():
    if not st.session_state.authenticated:
        show_login_screen()
    else:
        show_voice_input_screen()

if __name__ == "__main__":
    main()
