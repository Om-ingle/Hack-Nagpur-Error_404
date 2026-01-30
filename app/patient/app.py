import streamlit as st
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai.processing import transcribe_audio, extract_patient_data, extract_from_text
from ai.summary import generate_doctor_summary
from ml.model import predict_risk_score
import json
from datetime import datetime
from db.patient_repo import get_patient_by_phone, create_patient, verify_patient, update_patient_name
from db.visit_repo import create_visit, get_queue_position, get_previous_visits

# Page config
st.set_page_config(
    page_title="AarogyaQueue - Patient",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Premium Custom CSS with Medical Teal Theme
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
    
    /* Calm medical background */
    .stApp {
        background: #F4F7F8;
        min-height: 100vh;
    }
    
    /* Sticky Header */
    .sticky-header {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 70px;
        background: #FFFFFF;
        border-bottom: 1px solid #E5E7EB;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        z-index: 1000;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 2rem;
    }
    
    .header-brand {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .header-logo-icon {
        width: 42px;
        height: 42px;
        background: linear-gradient(135deg, #0E9F8A 0%, #0B7F6E 100%);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
    }
    
    .header-brand-text {
        font-size: 1.3rem;
        font-weight: 700;
        color: #1F2937;
    }
    
    .header-badge {
        background: #E8F1FF;
        color: #0E9F8A;
        padding: 0.5rem 1.25rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    /* Main Content Container */
    .main-content {
        margin-top: 90px;
        max-width: 1400px;
        margin-left: auto;
        margin-right: auto;
        padding: 2rem;
    }
    
    /* Login Container */
    .login-wrapper {
        max-width: 460px;
        margin: 3rem auto;
        text-align: center;
    }
    
    .logo-container {
        margin-bottom: 2rem;
    }
    
    .logo-icon {
        width: 90px;
        height: 90px;
        background: linear-gradient(135deg, #0E9F8A 0%, #0B7F6E 100%);
        border-radius: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 45px;
        margin: 0 auto 1rem;
        box-shadow: 0 8px 24px rgba(14, 159, 138, 0.3);
    }
    
    .brand-name {
        font-size: 1.6rem;
        font-weight: 700;
        color: #0B7F6E;
        letter-spacing: -0.5px;
    }
    
    .login-title {
        font-size: 2rem;
        font-weight: 800;
        color: #1F2937;
        margin: 1.5rem 0 0.5rem;
        letter-spacing: -1px;
    }
    
    .login-subtitle {
        color: #6B7280;
        font-size: 0.95rem;
        margin-bottom: 2rem;
        line-height: 1.6;
    }
    
    /* Card Styling */
    .glass-card {
        background: #FFFFFF;
        border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
        padding: 2.5rem;
        transition: all 0.3s ease;
        border: 1px solid #E5E7EB;
    }
    
    .glass-card:hover {
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
    }
    
    /* Voice Section Card */
    .voice-section {
        background: #FFFFFF;
        border-radius: 20px;
        padding: 2.5rem;
        text-align: center;
        border: 1px solid #E5E7EB;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
        height: 100%;
    }
    
    .voice-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #1F2937;
        margin-bottom: 0.5rem;
    }
    
    .voice-subtitle {
        color: #6B7280;
        font-size: 0.9rem;
        margin-bottom: 2rem;
    }
    
    /* Large Circular Mic Button */
    .mic-container {
        width: 180px;
        height: 180px;
        border-radius: 50%;
        background: linear-gradient(135deg, #E8F1FF 0%, #D1E9FF 100%);
        border: 5px solid #0E9F8A;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 2rem auto;
        position: relative;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 8px 24px rgba(14, 159, 138, 0.2);
    }
    
    .mic-container:hover {
        transform: scale(1.05);
        box-shadow: 0 12px 32px rgba(14, 159, 138, 0.3);
    }
    
    .mic-container::before {
        content: '';
        position: absolute;
        width: 100%;
        height: 100%;
        border-radius: 50%;
        border: 3px solid #0E9F8A;
        animation: pulse-ring 2s ease-out infinite;
    }
    
    @keyframes pulse-ring {
        0% { 
            transform: scale(1);
            opacity: 0.8;
        }
        70% { 
            transform: scale(1.3);
            opacity: 0;
        }
        100% { 
            transform: scale(1);
            opacity: 0;
        }
    }
    
    .mic-icon {
        font-size: 70px;
        filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
    }
    
    .mic-label {
        color: #0B7F6E;
        font-weight: 600;
        font-size: 1rem;
        margin-top: 1rem;
    }
    
    /* Form Card */
    .form-card {
        background: #FFFFFF;
        border-radius: 20px;
        padding: 2.5rem;
        border: 1px solid #E5E7EB;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
        height: 100%;
    }
    
    .form-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #1F2937;
        margin-bottom: 1.5rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid #E5E7EB;
    }
    
    /* Premium Input Styling */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: #FFFFFF !important;
        border: 2px solid #E5E7EB !important;
        border-radius: 12px !important;
        padding: 0.875rem 1.125rem !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
        color: #1F2937 !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #0E9F8A !important;
        box-shadow: 0 0 0 4px rgba(14, 159, 138, 0.1) !important;
        background: #FFFFFF !important;
    }
    
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: #9CA3AF !important;
        font-weight: 400 !important;
    }
    
    /* Premium Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #0E9F8A 0%, #0B7F6E 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.875rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        letter-spacing: 0.3px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(14, 159, 138, 0.3) !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #0B7F6E 0%, #096B5E 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(14, 159, 138, 0.4) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* Primary CTA Button */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #0E9F8A 0%, #0B7F6E 100%) !important;
        font-size: 1.05rem !important;
        padding: 1rem 2.5rem !important;
        box-shadow: 0 6px 20px rgba(14, 159, 138, 0.35) !important;
    }
    
    /* Token Success Screen - Redesigned */
    .token-success-container {
        background: #FFFFFF;
        border-radius: 24px;
        padding: 3rem 2.5rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
        border: 1px solid #E5E7EB;
        text-align: center;
    }
    
    /* Large Medical Green Checkmark */
    .success-checkmark {
        width: 120px;
        height: 120px;
        background: linear-gradient(135deg, #16A34A 0%, #15803D 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 1.5rem;
        box-shadow: 0 8px 32px rgba(22, 163, 74, 0.3);
        animation: success-pop 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    }
    
    @keyframes success-pop {
        0% { 
            transform: scale(0) rotate(-180deg);
            opacity: 0;
        }
        100% { 
            transform: scale(1) rotate(0deg);
            opacity: 1;
        }
    }
    
    .check-icon {
        font-size: 64px;
        color: white;
        font-weight: bold;
        line-height: 1;
    }
    
    /* Success Message */
    .success-message {
        font-size: 1.5rem;
        font-weight: 700;
        color: #16A34A;
        margin-bottom: 2rem;
        letter-spacing: -0.5px;
    }
    
    /* Token Display - Large and Centered */
    .token-display {
        background: linear-gradient(135deg, #F4F7F8 0%, #E8F1FF 100%);
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
        border: 2px solid #E5E7EB;
    }
    
    .token-label-new {
        color: #6B7280;
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 0.75rem;
    }
    
    .token-number-large {
        font-size: 5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #0E9F8A 0%, #0B7F6E 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.1;
        letter-spacing: -2px;
    }
    
    /* Information Cards */
    .info-card {
        background: #FFFFFF;
        border: 2px solid #E5E7EB;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .info-card:hover {
        border-color: #0E9F8A;
        box-shadow: 0 4px 16px rgba(14, 159, 138, 0.15);
        transform: translateY(-2px);
    }
    
    .info-card-highlight {
        background: linear-gradient(135deg, #E8F1FF 0%, #D1E9FF 100%);
        border: 2px solid #0E9F8A;
        grid-row: span 2;
    }
    
    .info-icon {
        font-size: 2.5rem;
        margin-bottom: 0.75rem;
        line-height: 1;
    }
    
    .info-label {
        color: #6B7280;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }
    
    .info-value {
        color: #1F2937;
        font-size: 1.3rem;
        font-weight: 700;
    }
    
    .info-value-large {
        color: #0E9F8A;
        font-size: 3rem;
        font-weight: 800;
        line-height: 1;
        margin: 0.5rem 0;
    }
    
    .info-unit {
        color: #6B7280;
        font-size: 0.9rem;
        font-weight: 500;
        margin-top: 0.25rem;
    }
    
    /* Old token success styles (kept for compatibility) */
    .token-success {
        text-align: center;
        padding: 3rem 2rem;
    }
    
    .success-icon {
        width: 110px;
        height: 110px;
        background: linear-gradient(135deg, #16A34A 0%, #15803D 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 1.5rem;
        font-size: 55px;
        box-shadow: 0 8px 30px rgba(22, 163, 74, 0.35);
        animation: scale-in 0.5s ease-out;
    }
    
    @keyframes scale-in {
        0% { transform: scale(0); opacity: 0; }
        100% { transform: scale(1); opacity: 1; }
    }
    
    .token-label {
        color: #6B7280;
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 0.5rem;
    }
    
    .token-number {
        font-size: 4.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #1F2937 0%, #374151 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.1;
        margin-bottom: 1rem;
    }
    
    .clinic-badge {
        display: inline-block;
        background: linear-gradient(135deg, #0E9F8A 0%, #0B7F6E 100%);
        color: white;
        padding: 0.75rem 2rem;
        border-radius: 50px;
        font-weight: 700;
        font-size: 1.1rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(14, 159, 138, 0.3);
    }
    
    .wait-info {
        background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
        border-radius: 16px;
        padding: 1.25rem 2rem;
        margin: 1.5rem auto;
        max-width: 350px;
        border: 1px solid #D97706;
    }
    
    .wait-label {
        color: #92400E;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .wait-time {
        color: #78350F;
        font-size: 2rem;
        font-weight: 800;
        margin-top: 0.25rem;
    }
    
    .queue-position {
        background: rgba(14, 159, 138, 0.1);
        border-radius: 12px;
        padding: 1rem;
        margin-top: 1.5rem;
        display: inline-block;
    }
    
    .queue-text {
        color: #0B7F6E;
        font-weight: 600;
        font-size: 1rem;
    }
    
    /* Divider */
    hr {
        border: none;
        height: 1px;
        background: #E5E7EB;
        margin: 1.5rem 0;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(14, 159, 138, 0.05) !important;
        border-radius: 10px !important;
        border: 1px solid #E5E7EB !important;
    }
    
    /* Audio input styling */
    .stAudioInput > div {
        border-radius: 12px !important;
        border: 2px solid #E5E7EB !important;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background-color: rgba(22, 163, 74, 0.1) !important;
        border-left: 4px solid #16A34A !important;
        border-radius: 8px !important;
        color: #15803D !important;
    }
    
    .stInfo {
        background-color: #E8F1FF !important;
        border-left: 4px solid #0E9F8A !important;
        border-radius: 8px !important;
        color: #0B7F6E !important;
    }
    
    .stWarning {
        background-color: rgba(217, 119, 6, 0.1) !important;
        border-left: 4px solid #D97706 !important;
        border-radius: 8px !important;
        color: #92400E !important;
    }
    
    .stError {
        background-color: rgba(220, 38, 38, 0.1) !important;
        border-left: 4px solid #DC2626 !important;
        border-radius: 8px !important;
        color: #991B1B !important;
    }
    
    /* Labels */
    .stTextInput > label, .stNumberInput > label, .stTextArea > label {
        font-weight: 600 !important;
        color: #1F2937 !important;
        font-size: 0.95rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Progress indicator */
    .processing-indicator {
        background: #E8F1FF;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        text-align: center;
        color: #0B7F6E;
        font-weight: 600;
        border: 2px dashed #0E9F8A;
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
if 'processing_audio' not in st.session_state:
    st.session_state.processing_audio = False
if 'extracted_symptoms_list' not in st.session_state:
    st.session_state.extracted_symptoms_list = []
if 'extracted_symptoms_text' not in st.session_state:
    st.session_state.extracted_symptoms_text = ''

def update_form_with_extracted_data(extracted):
    if not extracted:
        return
    
    if 'name' in extracted and extracted['name'] and extracted['name'] != 'Unknown':
        st.session_state.name_field_input = extracted['name']
    
    if 'age' in extracted and extracted['age']:
        st.session_state.age_field_input = int(extracted['age'])
    
    if 'symptoms' in extracted and extracted['symptoms']:
        # Store symptoms both as list and as text
        if isinstance(extracted['symptoms'], list):
            st.session_state.extracted_symptoms_list = extracted['symptoms']
            st.session_state.extracted_symptoms_text = ', '.join(extracted['symptoms'])
        else:
            st.session_state.extracted_symptoms_list = [str(extracted['symptoms'])]
            st.session_state.extracted_symptoms_text = str(extracted['symptoms'])
        # Update the field with the text version
        st.session_state.symptoms_field_input = st.session_state.extracted_symptoms_text

def render_sticky_header():
    """Render sticky header with branding"""
    st.markdown("""
        <div class="sticky-header">
            <div class="header-brand">
                <div class="header-logo-icon">🏥</div>
                <div class="header-brand-text">AarogyaQueue</div>
            </div>
            <div class="header-badge">Patient Portal</div>
        </div>
    """, unsafe_allow_html=True)

def show_login_screen():
    render_sticky_header()
    
    # Main content wrapper
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
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
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close main-content

def show_voice_input_screen():
    render_sticky_header()
    
    # Main content wrapper
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    if not st.session_state.token_generated:
        # Two-column layout: Voice Input (Left) | Patient Details (Right)
        col1, col2 = st.columns([1, 1.2], gap="large")
        
        with col1:
            st.markdown('<div class="voice-section">', unsafe_allow_html=True)
            
            # Voice section header
            st.markdown("""
                <div class="voice-title">🎤 Voice Input</div>
                <div class="voice-subtitle">Describe your symptoms by speaking clearly</div>
            """, unsafe_allow_html=True)
            
            # Large circular mic button
            st.markdown("""
                <div class="mic-container">
                    <span class="mic-icon">🎤</span>
                </div>
                <p class="mic-label">Tap below to start recording</p>
            """, unsafe_allow_html=True)
            
            # Audio input
            audio_bytes = st.audio_input("Record your symptoms", label_visibility="collapsed")
            
            # Simple mechanism to prevent re-processing the same audio
            current_audio_id = hash(audio_bytes) if audio_bytes else None
            
            if audio_bytes and st.session_state.get('last_processed_audio_id') != current_audio_id:
                st.session_state.processing_audio = True
                st.session_state.last_processed_audio_id = current_audio_id
                
                with st.spinner("🔄 Processing your voice..."):
                    transcript = transcribe_audio(audio_bytes)
                    if transcript:
                        st.info(f"📝 Heard: \"{transcript}\"")
                        extracted = extract_patient_data(transcript)
                        
                        if extracted and 'error' not in extracted:
                            st.session_state.extracted_data = extracted
                            update_form_with_extracted_data(extracted)
                            st.success("✅ Data extracted! Form updated.")
                            import time
                            time.sleep(1)
                
                st.session_state.processing_audio = False
                st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Text input option (collapsible)
            st.write("")
            with st.expander("💬 Or type your symptoms instead"):
                text_input = st.text_area("Type symptoms here", height=100, key="text_symptoms_input")
                if st.button("📤 Process Text", key="process_text_btn"):
                    if text_input:
                        extracted = extract_patient_data(text_input)
                        if extracted and 'error' not in extracted:
                            st.session_state.extracted_data = extracted
                            update_form_with_extracted_data(extracted)
                            st.success("✅ Data extracted!")
                            st.rerun()
        
        with col2:
            st.markdown('<div class="form-card">', unsafe_allow_html=True)
            st.markdown('<div class="form-title">📋 Patient Details</div>', unsafe_allow_html=True)
            
            # Initialize form fields in session state
            if 'name_field_input' not in st.session_state:
                st.session_state.name_field_input = ''
            if 'age_field_input' not in st.session_state:
                st.session_state.age_field_input = 30
            if 'symptoms_field_input' not in st.session_state:
                st.session_state.symptoms_field_input = ''
            
            # Form inputs
            name = st.text_input("Full Name", key="name_field_input", placeholder="Enter your full name")
            age = st.number_input("Age", min_value=1, max_value=120, key="age_field_input")
            symptoms = st.text_area(
                "Symptoms Description", 
                value=st.session_state.symptoms_field_input,
                height=150, 
                placeholder="Describe your symptoms in detail..."
            )
            
            st.write("")
            
            # Primary CTA Button
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
                    
                    # Get previous visits for context
                    previous_visits = get_previous_visits(st.session_state.patient_phone, limit=3)
                    
                    # Generate AI summary for doctor
                    ai_summary = generate_doctor_summary(
                        current_symptoms=symptoms,
                        patient_age=age,
                        risk_level=risk_level,
                        previous_visits=previous_visits
                    )
                    
                    # Create visit with AI summary
                    symptoms_list = [symptoms]
                    visit_id = create_visit(
                        st.session_state.patient_phone,
                        symptoms,
                        json.dumps(symptoms_list),
                        float(risk_score),
                        risk_level,
                        assigned_tier,
                        ai_summary
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
        # Token Success Screen - Redesigned
        token = st.session_state.token_data
        
        # Center column for success screen
        col1, col2, col3 = st.columns([0.5, 2, 0.5])
        
        with col2:
            st.markdown('<div class="token-success-container">', unsafe_allow_html=True)
            
            # Large success icon with medical green
            st.markdown('''
                <div class="success-checkmark">
                    <div class="check-icon">✓</div>
                </div>
            ''', unsafe_allow_html=True)
            
            # Success message
            st.markdown('''
                <div class="success-message">Token Generated Successfully!</div>
            ''', unsafe_allow_html=True)
            
            # Large token number - centered and prominent
            st.markdown(f'''
                <div class="token-display">
                    <div class="token-label-new">Your Token Number</div>
                    <div class="token-number-large">T-{token["token"]}</div>
                </div>
            ''', unsafe_allow_html=True)
            
            st.write("")
            
            # Information cards in a clean grid
            info_col1, info_col2 = st.columns(2, gap="medium")
            
            with info_col1:
                # Clinic assignment card
                clinic_name = "Senior Doctor" if token['tier'] == 'SENIOR' else "Junior Doctor"
                clinic_icon = "👨‍⚕️" if token['tier'] == 'SENIOR' else "🩺"
                st.markdown(f'''
                    <div class="info-card">
                        <div class="info-icon">{clinic_icon}</div>
                        <div class="info-label">Assigned To</div>
                        <div class="info-value">{clinic_name}</div>
                    </div>
                ''', unsafe_allow_html=True)
                
                # Queue position card
                st.markdown(f'''
                    <div class="info-card">
                        <div class="info-icon">📊</div>
                        <div class="info-label">Queue Position</div>
                        <div class="info-value">#{token.get("queue_position", 1)}</div>
                    </div>
                ''', unsafe_allow_html=True)
            
            with info_col2:
                # Wait time card - prominent
                st.markdown(f'''
                    <div class="info-card info-card-highlight">
                        <div class="info-icon">⏱️</div>
                        <div class="info-label">Estimated Wait</div>
                        <div class="info-value-large">{token["wait_time"]}</div>
                        <div class="info-unit">minutes</div>
                    </div>
                ''', unsafe_allow_html=True)
            
            st.write("")
            st.write("")
            
            # Single clear action button
            if st.button("🏠 Back to Home", use_container_width=True, key="back_home_btn"):
                st.session_state.authenticated = False
                st.session_state.token_generated = False
                st.session_state.name_field_input = ''
                st.session_state.age_field_input = 30
                st.session_state.symptoms_field_input = ''
                st.session_state.extracted_data = None
                st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close main-content

def main():
    if not st.session_state.authenticated:
        show_login_screen()
    else:
        show_voice_input_screen()

if __name__ == "__main__":
    main()
