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

# ===== PAGE CONFIG =====
st.set_page_config(
    page_title="AarogyaQueue - Patient Portal",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ===== MINIMAL CSS - NO STREAMLIT OVERRIDES =====
st.markdown("""
<style>
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    .huge-number {
        font-size: 72px !important;
        font-weight: 800;
        color: #197CA7;
        text-align: center;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ===== SESSION STATE INIT =====
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'patient_phone' not in st.session_state:
    st.session_state.patient_phone = None
if 'patient_data' not in st.session_state:
    st.session_state.patient_data = None
if 'token_generated' not in st.session_state:
    st.session_state.token_generated = False
if 'current_screen' not in st.session_state:
    st.session_state.current_screen = 'login'
if 'health_tip_index' not in st.session_state:
    st.session_state.health_tip_index = 0

# ===== HEALTH TIPS =====
HEALTH_TIPS = [
    "💧 Drink 8-10 glasses of water daily for better health",
    "🥬 Include green vegetables in every meal",
    "🚶 Walk for 30 minutes daily to stay fit",
    "😴 Sleep 7-8 hours every night for good health",
    "🧼 Wash hands frequently to prevent infections",
    "🌞 Get morning sunlight for Vitamin D",
    "🧘 Practice deep breathing to reduce stress",
    "🍎 Eat fruits daily for essential vitamins",
]

def rotate_health_tip():
    st.session_state.health_tip_index = (st.session_state.health_tip_index + 1) % len(HEALTH_TIPS)

# ===== SCREEN 1: LOGIN =====
def show_login_screen():
    st.title("🏥 AarogyaQueue")
    st.subheader("Digital Healthcare Queue System")
    st.divider()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 📱 Patient Check-In")
        st.info("ℹ️ Enter your phone number and year of birth to continue")
        
        phone = st.text_input(
            "📞 Phone Number",
            placeholder="Enter 10-digit mobile number",
            max_chars=10,
            help="Your registered mobile number"
        )
        
        yob = st.text_input(
            "📅 Year of Birth",
            placeholder="Enter year (e.g., 1990)",
            max_chars=4,
            type="password",
            help="Your year of birth for verification"
        )
        
        st.markdown("")
        
        if st.button("🚀 **CHECK IN NOW**", use_container_width=True, type="primary"):
            if len(phone) == 10 and len(yob) == 4:
                try:
                    yob_int = int(yob)
                    patient = get_patient_by_phone(phone)
                    
                    if patient:
                        if patient['yob'] == yob_int:
                            st.session_state.authenticated = True
                            st.session_state.patient_phone = phone
                            st.session_state.patient_data = patient
                            st.session_state.current_screen = 'registration'
                            st.rerun()
                        else:
                            st.error("❌ Invalid year of birth. Please try again.")
                    else:
                        new_patient = create_patient(phone, yob_int)
                        st.session_state.authenticated = True
                        st.session_state.patient_phone = phone
                        st.session_state.patient_data = new_patient
                        st.session_state.current_screen = 'registration'
                        st.success("✅ New patient registered!")
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("⚠️ Please enter valid 10-digit phone and 4-digit year")
    
    st.divider()
    st.info(f"💡 **Health Tip:** {HEALTH_TIPS[st.session_state.health_tip_index]}")

# ===== SCREEN 2: REGISTRATION =====
def show_registration_screen():
    st.title("📋 Patient Registration")
    patient_name = st.session_state.patient_data.get('name', 'Patient')
    st.markdown(f"### Welcome, {patient_name}!")
    st.divider()
    
    col_form, col_voice = st.columns([3, 2], gap="large")
    
    with col_form:
        st.markdown("### 📝 Your Details")
        
        name = st.text_input(
            "👤 Full Name",
            value=st.session_state.patient_data.get('name', ''),
            placeholder="Enter your full name",
            help="Your complete name"
        )
        
        age = st.number_input(
            "🎂 Age",
            min_value=1,
            max_value=120,
            value=30,
            help="Your current age in years"
        )
        
        st.markdown("#### 🩺 Describe Your Health Issue")
        symptoms = st.text_area(
            "Symptoms",
            height=180,
            placeholder="Example: I have fever and headache since 2 days...",
            help="Describe your symptoms in simple words",
            label_visibility="collapsed"
        )
        
        st.markdown("")
        
        if st.button("✅ **SUBMIT & GET TOKEN**", use_container_width=True, type="primary"):
            if symptoms.strip():
                process_registration(name, age, symptoms)
            else:
                st.error("⚠️ Please describe your symptoms to continue")
    
    with col_voice:
        st.markdown("### 🎤 Voice Input (Optional)")
        st.info("📢 Speak your symptoms in your preferred language")
        
        audio_bytes = st.audio_input("Record symptoms")
        
        if audio_bytes:
            with st.spinner("🔄 Processing your voice..."):
                try:
                    transcript = transcribe_audio(audio_bytes)
                    if transcript:
                        st.success(f"✅ Recorded: \"{transcript}\"")
                except Exception as e:
                    st.error(f"❌ Error processing audio: {str(e)}")
        
        st.divider()
        
        st.markdown("### ⌨️ Or Type Symptoms")
        text_symptoms = st.text_area(
            "Type here",
            height=100,
            placeholder="Type your symptoms...",
            label_visibility="collapsed",
            key="text_symptoms_alt"
        )
        
        if st.button("📤 Use This Text", use_container_width=True):
            if text_symptoms.strip():
                st.session_state.temp_symptoms = text_symptoms
                st.rerun()
    
    st.divider()
    
    tip_col1, tip_col2 = st.columns([5, 1])
    with tip_col1:
        st.info(f"💡 **Health Tip:** {HEALTH_TIPS[st.session_state.health_tip_index]}")
    with tip_col2:
        if st.button("🔄"):
            rotate_health_tip()
            st.rerun()
    
    if st.button("⬅️ Back to Login"):
        st.session_state.authenticated = False
        st.session_state.current_screen = 'login'
        st.rerun()

def process_registration(name, age, symptoms):
    try:
        risk_score = predict_risk_score(symptoms, age)
        assigned_tier = 'SENIOR' if risk_score > 0.7 else 'JUNIOR'
        risk_level = 'HIGH' if risk_score > 0.7 else ('MEDIUM' if risk_score > 0.4 else 'LOW')
        
        if name and name != st.session_state.patient_data.get('name'):
            update_patient_name(st.session_state.patient_phone, name)
        
        previous_visits = get_previous_visits(st.session_state.patient_phone, limit=3)
        
        ai_summary = generate_doctor_summary(
            current_symptoms=symptoms,
            patient_age=age,
            risk_level=risk_level,
            previous_visits=previous_visits
        )
        
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
        
        queue_position = get_queue_position(assigned_tier)
        
        st.session_state.token_data = {
            'token': f"{visit_id:08d}",
            'tier': assigned_tier,
            'wait_time': queue_position * 8,
            'queue_position': queue_position,
            'risk_level': risk_level
        }
        st.session_state.token_generated = True
        st.session_state.current_screen = 'success'
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error creating visit: {str(e)}")

# ===== SCREEN 3: SUCCESS & QUEUE STATUS =====
def show_success_screen():
    token = st.session_state.token_data
    
    st.success("✅ **TOKEN GENERATED SUCCESSFULLY!**")
    st.divider()
    
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        st.markdown("#### Your Token Number")
        st.markdown(f'<p class="huge-number">T-{token["token"]}</p>', unsafe_allow_html=True)
        
        st.divider()
        
        clinic_name = "Senior Doctor 👨‍⚕️" if token['tier'] == 'SENIOR' else "Junior Doctor 🩺"
        st.info(f"**Assigned to:** {clinic_name}")
        st.markdown("")
    
    st.markdown("### 📊 Queue Status")
    
    status_col1, status_col2, status_col3 = st.columns(3, gap="medium")
    
    with status_col1:
        st.metric(
            label="⏱️ Estimated Wait Time",
            value=f"{token['wait_time']} min",
            delta="Approximate",
            help="Time may vary based on consultations"
        )
    
    with status_col2:
        st.metric(
            label="📍 Your Position",
            value=f"#{token.get('queue_position', 1)}",
            delta="in queue",
            help="Number of patients ahead of you"
        )
    
    with status_col3:
        priority = "High Priority" if token.get('risk_level') == 'HIGH' else "Normal"
        st.metric(
            label="🏥 Priority Level",
            value=priority,
            help="Based on symptom analysis"
        )
    
    st.divider()
    
    st.markdown("### 📢 What to Do Next")
    
    info_col1, info_col2 = st.columns(2, gap="medium")
    
    with info_col1:
        st.info("""
        **Please wait in the waiting area**
        
        ✓ Keep your token number visible  
        ✓ Listen for your token announcement  
        ✓ Have your ID ready for verification
        """)
    
    with info_col2:
        st.warning("""
        **Important Instructions**
        
        ⚠️ Do not leave the premises  
        ⚠️ Maintain social distancing  
        ⚠️ Wear your mask properly
        """)
    
    st.divider()
    
    st.markdown("### 💡 Health Tips While You Wait")
    
    tip_display_col, tip_button_col = st.columns([5, 1])
    
    with tip_display_col:
        st.success(HEALTH_TIPS[st.session_state.health_tip_index])
    
    with tip_button_col:
        if st.button("Next Tip ➡️"):
            rotate_health_tip()
            st.rerun()
    
    st.divider()
    
    action_col1, action_col2 = st.columns(2, gap="large")
    
    with action_col1:
        if st.button("🔄 **CHECK QUEUE STATUS**", use_container_width=True):
            updated_position = get_queue_position(token['tier'])
            st.session_state.token_data['queue_position'] = updated_position
            st.session_state.token_data['wait_time'] = updated_position * 8
            st.rerun()
    
    with action_col2:
        if st.button("🏠 **FINISH & GO HOME**", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.token_generated = False
            st.session_state.current_screen = 'login'
            st.rerun()

# ===== MAIN ROUTER =====
def main():
    if st.session_state.current_screen == 'login':
        show_login_screen()
    elif st.session_state.current_screen == 'registration':
        show_registration_screen()
    elif st.session_state.current_screen == 'success':
        show_success_screen()

if __name__ == "__main__":
    main()
