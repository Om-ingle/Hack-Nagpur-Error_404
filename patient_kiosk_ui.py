import streamlit as st
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai.processing import transcribe_audio, extract_patient_data, extract_from_text
from ai.summary import generate_doctor_summary
from ml.model import predict_risk_score
import json
from datetime import datetime
from db.patient_repo import get_patient_by_phone, create_patient, verify_patient, update_patient_name
from db.visit_repo import create_visit, get_queue_position, get_previous_visits
import time

# --- CONFIGURATION ---
KIOSK_MODE = True  # Global toggle for Kiosk / Booth Mode

# Page config
st.set_page_config(
    page_title="AarogyaQueue - Patient Kiosk",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- PWA KIOSK CONFIGURATION (INJECTED) ---
# Purpose: Enable full-screen "Add to Home Screen" capability without external server
import base64

def inject_pwa():
    # 1. Manifest JSON
    manifest = {
        "name": "AarogyaQueue Patient Kiosk",
        "short_name": "Aarogya Kiosk",
        "start_url": "./",
        "display": "standalone",
        "background_color": "#FFFFFF",
        "theme_color": "#0E9F8A",
        "orientation": "portrait",
        "icons": [
            {
                "src": "https://img.icons8.com/color/192/hospital-2.png",
                "sizes": "192x192",
                "type": "image/png"
            },
            {
                "src": "https://img.icons8.com/color/512/hospital-2.png",
                "sizes": "512x512",
                "type": "image/png"
            }
        ]
    }
    manifest_json = json.dumps(manifest)
    b64_manifest = base64.b64encode(manifest_json.encode()).decode()
    
    pwa_javascript = f"""
        <script>
            // A. Inject Manifest
            const link = document.createElement('link');
            link.rel = 'manifest';
            link.href = 'data:application/manifest+json;base64,{b64_manifest}';
            document.head.appendChild(link);

            // B. Inject Meta Tags for iOS/Android Fullscreen
            const metaTags = [
                {{name: 'mobile-web-app-capable', content: 'yes'}},
                {{name: 'apple-mobile-web-app-capable', content: 'yes'}},
                {{name: 'apple-mobile-web-app-status-bar-style', content: 'black-translucent'}},
                {{name: 'theme-color', content: '#0E9F8A'}},
                {{name: 'viewport', content: 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no'}}
            ];

            metaTags.forEach(tag => {{
                const meta = document.createElement('meta');
                meta.name = tag.name;
                meta.content = tag.content;
                document.head.appendChild(meta);
            }});

            // C. Register Minimal Service Worker (for PWA criteria)
            if ('serviceWorker' in navigator) {{
                const swCode = `
                    self.addEventListener('install', (e) => {{
                        e.waitUntil(self.skipWaiting());
                    }});
                    self.addEventListener('fetch', (e) => {{
                        // No-op transparent proxy
                    }});
                `;
                const blob = new Blob([swCode], {{type: 'application/javascript'}});
                const swUrl = URL.createObjectURL(blob);
                
                navigator.serviceWorker.register(swUrl)
                    .then(reg => console.log('Kiosk SW Registered'))
                    .catch(err => console.log('SW Error:', err));
            }}
        </script>
        
        <style>
            /* Extra safety for touch selection */
            body {{
                user-select: none;
                -webkit-user-select: none;
                overscroll-behavior-y: none; /* Disables pull-to-refresh */
            }}
            
            /* Fullscreen Button Style */
            #fullscreen-btn {{
                position: fixed;
                bottom: 20px;
                left: 20px;
                z-index: 99999;
                background: rgba(0, 0, 0, 0.5);
                color: white;
                border: none;
                width: 50px;
                height: 50px;
                border-radius: 50%;
                font-size: 24px;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                transition: opacity 0.3s;
            }}
            #fullscreen-btn:active {{ transform: scale(0.95); }}
            @media all and (display-mode: standalone) {{
                #fullscreen-btn {{ display: none; }}
            }}
        </style>
        
        <script>
            // Robust Fullscreen Toggle
            function createFullscreenBtn() {{
                const existing = document.getElementById('fullscreen-btn');
                if (existing) existing.remove();

                const btn = document.createElement('button');
                btn.id = 'fullscreen-btn';
                btn.innerHTML = '⛶';
                btn.title = 'Enter Fullscreen';
                
                btn.onclick = function() {{
                    const doc = window.document;
                    const docEl = doc.documentElement;

                    const requestFullScreen = docEl.requestFullscreen || docEl.mozRequestFullScreen || docEl.webkitRequestFullScreen || docEl.msRequestFullscreen;
                    const cancelFullScreen = doc.exitFullscreen || doc.mozCancelFullScreen || doc.webkitExitFullscreen || doc.msExitFullscreen;

                    if(!doc.fullscreenElement && !doc.mozFullScreenElement && !doc.webkitFullscreenElement && !doc.msFullscreenElement) {{
                        requestFullScreen.call(docEl);
                    }} else {{
                        cancelFullScreen.call(doc);
                    }}
                }};
                
                document.body.appendChild(btn);
            }}

            createFullscreenBtn();
            setTimeout(createFullscreenBtn, 1000);
        </script>
    """
    
    st.markdown(pwa_javascript, unsafe_allow_html=True)
    
inject_pwa()

# Premium Custom CSS - Kiosk Theme
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Reset & Base */
    html, body, .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background: #FFFFFF !important;
    }
    
    .stApp {
        background: #FFFFFF !important;
        min-height: 100vh;
    }
    
    div[data-testid="stAppViewContainer"],
    div[data-testid="stHeader"],
    section[data-testid="stSidebar"] {
        background: #FFFFFF !important;
    }
    
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display: none;}
    
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
        background: #FFFFFF;
        color: #0E9F8A;
        padding: 0.5rem 1.25rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 0.9rem;
        border: 2px solid #0E9F8A;
    }
    
    /* Main Content Container */
    .main-content {
        margin-top: 90px;
        max-width: 1400px;
        margin-left: auto;
        margin-right: auto;
        padding: 2rem;
    }
    
    /* KIOSK MODE SPECIFIC STYLES */
    .kiosk-btn {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 100%;
        height: 140px;
        background: #FFFFFF;
        border: 2px solid #0E9F8A;
        border-radius: 16px;
        cursor: pointer;
        transition: all 0.2s;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .kiosk-btn:hover {
        background: #F0FDFA;
        transform: translateY(-4px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    .kiosk-btn-icon {
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    .kiosk-btn-text {
        font-size: 1.25rem;
        font-weight: 700;
        color: #0F766E;
    }
    .kiosk-attractor {
        height: 80vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #0F766E 0%, #115E59 100%);
        color: white;
        border-radius: 20px;
        text-align: center;
        cursor: pointer;
        animation: pulse-light 3s infinite;
    }
    @keyframes pulse-light {
        0%, 100% { box-shadow: 0 0 20px rgba(15, 118, 110, 0.5); }
        50% { box-shadow: 0 0 40px rgba(15, 118, 110, 0.8); }
    }
    
    /* Numeric Keypad */
    .keypad-title {
        font-size: 0.9rem;
        font-weight: 600;
        color: #6B7280;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    /* Button Styling */
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
</style>
""", unsafe_allow_html=True)

# KIOSK STATE MANAGEMENT
if 'kiosk_step' not in st.session_state:
    st.session_state.kiosk_step = 'HOME'
if 'kiosk_last_interaction' not in st.session_state:
    st.session_state.kiosk_last_interaction = time.time()
if 'keypad_phone_value' not in st.session_state:
    st.session_state.keypad_phone_value = ''
if 'keypad_yob_value' not in st.session_state:
    st.session_state.keypad_yob_value = ''

def reset_kiosk_state():
    """Reset all session state for new user safety"""
    keys_to_reset = [
        'authenticated', 'patient_phone', 'patient_data', 'extracted_data', 
        'token_generated', 'processing_audio', 'extracted_symptoms_list', 
        'extracted_symptoms_text', 'name_field_input', 'age_field_input', 
        'symptoms_field_input', 'token_data', 'keypad_phone_value', 'keypad_yob_value'
    ]
    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]
    
    st.session_state.kiosk_step = 'HOME'
    st.session_state.keypad_phone_value = ''
    st.session_state.keypad_yob_value = ''

# --- KIOSK RENDER FUNCTIONS ---
def render_kiosk_home():
    """Screen 1: Attractor / Home"""
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    if st.button("START_KIOSK", key="kiosk_start_btn", use_container_width=True):
         st.session_state.kiosk_step = 'ACTION'
         st.rerun()
    
    st.markdown("""
        <div class="kiosk-attractor">
            <div style="font-size: 5rem; margin-bottom: 1rem;">🏥</div>
            <div style="font-size: 3rem; font-weight: 800; margin-bottom: 0.5rem;">AarogyaQueue</div>
            <div style="font-size: 1.5rem; opacity: 0.9;">Rural Telemedicine Booth</div>
            <br><br>
            <div style="background: white; color: #0F766E; padding: 1rem 3rem; border-radius: 50px; font-weight: 700; font-size: 2rem;">
                Tap to Start Health Check
            </div>
            <br>
            <div style="font-size: 1.2rem;">👆 टच करके शुरू करें</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_kiosk_action_selection():
    """Screen 2: Action Selection"""
    render_sticky_header()
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    st.markdown("<h1 style='text-align: center; color: #1F2937; margin-bottom: 2rem;'>What do you want to do?<br><span style='font-size: 1.2rem; color: #6B7280;'>आप क्या करना चाहते हैं?</span></h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("""
            <div class="kiosk-btn">
                <div class="kiosk-btn-icon">🎤</div>
                <div class="kiosk-btn-text">Check-in Yourself</div>
                <div style="font-size: 0.9rem; color: #6B7280;">खुद चेक-इन करें</div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Select Check-in", key="btn_checkin", use_container_width=True):
            st.session_state.kiosk_step = 'CHECKIN_LOGIN'
            st.rerun()
            
    with col2:
        st.markdown("""
            <div class="kiosk-btn">
                <div class="kiosk-btn-icon">📞</div>
                <div class="kiosk-btn-text">Call Helpline</div>
                <div style="font-size: 0.9rem; color: #6B7280;">हेल्पलाइन पर कॉल करें</div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Select Helpline", key="btn_helpline", use_container_width=True):
            st.info("Dialing 1075... (Demo)")
            
    st.write("")
    st.write("")
    if st.button("⬅️ Back / पीछे जाएं", key="back_home", use_container_width=True):
        reset_kiosk_state()
        st.rerun()
        
    st.markdown('</div>', unsafe_allow_html=True)

def render_kiosk_phone_input():
    """Screen 3a: Big Phone Input"""
    render_sticky_header()
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    st.markdown("<h2 style='text-align: center; color: #1F2937;'>Enter Phone Number<br><span style='font-size: 1rem; color: #6B7280;'>फोन नंबर दर्ज करें</span></h2>", unsafe_allow_html=True)
    
    st.session_state.active_input = 'phone'
    
    curr_val = st.session_state.get('keypad_phone_value', '')
    display_val = curr_val if curr_val else "__________"
    st.markdown(f"<div style='font-size: 3rem; font-weight: 800; text-align: center; color: #0E9F8A; margin: 1rem 0; letter-spacing: 4px;'>{display_val}</div>", unsafe_allow_html=True)
    
    render_numeric_keypad()
    
    st.write("")
    col1, col2 = st.columns(2)
    with col1:
         if st.button("⬅️ Back", use_container_width=True, key="back_phone"):
             st.session_state.kiosk_step = 'ACTION'
             st.rerun()
    with col2:
         disabled = len(curr_val) != 10
         if st.button("Next ➡️", use_container_width=True, type="primary", disabled=disabled, key="next_phone"):
             st.session_state.patient_phone = curr_val
             st.session_state.kiosk_step = 'KIOSK_YOB'
             st.rerun()
             
    st.markdown('</div>', unsafe_allow_html=True)

def render_kiosk_yob_input():
    """Screen 3b: Big YOB Input"""
    render_sticky_header()
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    st.markdown("<h2 style='text-align: center; color: #1F2937;'>Enter Year of Birth<br><span style='font-size: 1rem; color: #6B7280;'>जन्म का वर्ष दर्ज करें (e.g. 1980)</span></h2>", unsafe_allow_html=True)
    
    st.session_state.active_input = 'yob'
    
    curr_val = st.session_state.get('keypad_yob_value', '')
    display_val = curr_val if curr_val else "YYYY"
    st.markdown(f"<div style='font-size: 3rem; font-weight: 800; text-align: center; color: #0E9F8A; margin: 1rem 0; letter-spacing: 4px;'>{display_val}</div>", unsafe_allow_html=True)
    
    render_numeric_keypad()
    
    st.write("")
    col1, col2 = st.columns(2)
    with col1:
         if st.button("⬅️ Back", use_container_width=True, key="back_yob"):
             st.session_state.kiosk_step = 'KIOSK_PHONE'
             st.rerun()
    with col2:
         disabled = len(curr_val) != 4
         if st.button("Start Check-in 🚀", use_container_width=True, type="primary", disabled=disabled, key="next_yob"):
             phone = st.session_state.patient_phone
             try:
                 yob_int = int(curr_val)
                 patient = get_patient_by_phone(phone)
                 
                 if patient:
                     if patient['yob'] == yob_int:
                         st.session_state.authenticated = True
                         st.session_state.patient_data = patient
                         st.session_state.kiosk_step = 'KIOSK_VOICE'
                         st.rerun()
                     else:
                         st.error("Invalid login details.")
                 else:
                     new_patient = create_patient(phone, yob_int)
                     st.session_state.authenticated = True
                     st.session_state.patient_data = new_patient
                     st.session_state.kiosk_step = 'KIOSK_VOICE'
                     st.rerun()
             except Exception as e:
                 st.error(f"Error: {e}")
             
    st.markdown('</div>', unsafe_allow_html=True)

def render_kiosk_voice_input():
    """Screen 3c: Voice Input & Review"""
    render_sticky_header()
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    st.markdown("<h2 style='text-align: center; color: #1F2937;'>Describe Symptoms<br><span style='font-size: 1rem; color: #6B7280;'>अपनी समस्या बताएं</span></h2>", unsafe_allow_html=True)

    st.markdown("""
        <div class="mic-container" style="width: 150px; height: 150px; margin: 1rem auto;">
            <span class="mic-icon" style="font-size: 60px;">🎤</span>
        </div>
    """, unsafe_allow_html=True)
    
    audio_bytes = st.audio_input("Record", label_visibility="collapsed")
    
    current_audio_id = hash(audio_bytes) if audio_bytes else None
    if audio_bytes and st.session_state.get('last_processed_audio_id') != current_audio_id:
        st.session_state.last_processed_audio_id = current_audio_id
        with st.spinner("Processing..."):
            transcript = transcribe_audio(audio_bytes)
            if transcript:
                st.info(f"Heard: {transcript}")
                extracted = extract_patient_data(transcript)
                if extracted:
                    update_form_with_extracted_data(extracted)
        st.rerun()

    st.markdown("""
        <div style="text-align: center; color: #DC2626; font-size: 0.9rem; margin-top: 1rem;">
            If microphone is not working, please type details below.<br>
            यदि माइक्रोफ़ोन काम नहीं कर रहा है, तो नीचे विवरण टाइप करें।
        </div>
    """, unsafe_allow_html=True)
    
    with st.expander("📝 Enter/Review Details / विवरण भरें", expanded=True):
        name = st.text_input("Name (Optional)", key="name_field_input")
        age = st.number_input("Age", min_value=0, max_value=120, step=1, key="age_field_input")
        symptoms = st.text_area("Symptoms (Required if no voice)", key="symptoms_field_input", height=100)
    
    st.write("")
    
    if st.button("🖨️ PRINT TOKEN / टोकन लें", type="primary", use_container_width=True, key="kiosk_submit"):
        if symptoms:
             extracted_data = {
                 'name': name if name else 'Unknown',
                 'age': age,
                 'symptoms': symptoms,
                 'emergency_detected': False
             }
             
             risk_score = predict_risk_score(symptoms, age)
             
             if name and st.session_state.patient_data.get('name') == 'Unknown':
                 update_patient_name(st.session_state.patient_phone, name)
                 
             visit_id = create_visit(
                 st.session_state.patient_phone,
                 symptoms,
                 json.dumps([symptoms]),
                 risk_score,
                 'SENIOR' if risk_score > 0.7 else ('MEDIUM' if risk_score > 0.4 else 'LOW'),
                 'SENIOR' if risk_score > 0.7 else 'JUNIOR'
             )
             
             if visit_id:
                 assigned_tier = 'SENIOR' if risk_score > 0.7 else 'JUNIOR'
                 queue_position = get_queue_position(assigned_tier)
                 
                 st.session_state.token_data = {
                     'token': f"{visit_id:08d}",
                     'tier': assigned_tier,
                     'wait_time': queue_position * 8,
                     'queue_position': queue_position
                 }
                 st.session_state.token_generated = True
                 st.session_state.kiosk_step = 'SUCCESS'
                 st.balloons()
                 st.rerun()
        else:
             st.warning("Please describe symptoms first.")

    st.markdown('</div>', unsafe_allow_html=True)

def render_kiosk_success():
    """Screen 4: Success Screen"""
    render_sticky_header()
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    token = st.session_state.token_data
    
    st.markdown(f"""
<div class="kiosk-attractor" style="height: auto; padding: 3rem; background: white; color: #1F2937; animation: none;">
<div style="width: 120px; height: 120px; background: linear-gradient(135deg, #16A34A 0%, #15803D 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 2rem;">
<div style="font-size: 64px; color: white;">✓</div>
</div>
<div style="font-size: 2rem; font-weight: 800; color: #16A34A; margin-bottom: 1rem;">Success!</div>
<div style="font-size: 1.2rem; color: #6B7280;">Please take your token ticket</div>
<br>
<div style="border: 4px dashed #0E9F8A; padding: 2rem; border-radius: 20px; background: #F0FDFA; margin-bottom: 2rem;">
<div style="font-size: 1.5rem; font-weight: 700; color: #0F766E;">TOKEN NUMBER</div>
<div style="font-size: 5rem; font-weight: 900; color: #0F766E; line-height: 1;">T-{token['token']}</div>
</div>
<div style="font-size: 1.5rem;">Wait Time: <strong style="color: #D97706">{token['wait_time']} mins</strong></div>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<script>
setTimeout(function(){window.location.reload();}, 8000);
</script>
""", unsafe_allow_html=True)
    
    st.progress(100, "Printing Ticket... (Auto-reset in 8s)")
    time.sleep(1)
    
    if st.button("Finish Now", use_container_width=True, key="kiosk_finish"):
        reset_kiosk_state()
        st.rerun()
        
    st.markdown('</div>', unsafe_allow_html=True)

def update_form_with_extracted_data(extracted):
    if not extracted:
        return
    
    if 'name' in extracted and extracted['name'] and extracted['name'] != 'Unknown':
        st.session_state.name_field_input = extracted['name']
    
    if 'age' in extracted and extracted['age']:
        st.session_state.age_field_input = int(extracted['age'])
    
    if 'symptoms' in extracted and extracted['symptoms']:
        if isinstance(extracted['symptoms'], list):
            st.session_state.symptoms_field_input = ', '.join(extracted['symptoms'])
        else:
            st.session_state.symptoms_field_input = str(extracted['symptoms'])

def render_numeric_keypad():
    """Render touch-friendly numeric keypad"""
    active_field = st.session_state.get('active_input', 'phone')
    
    if active_field == 'phone':
        max_length = 10
        field_label = "Phone Number"
        session_key = 'keypad_phone_value'
    else:
        max_length = 4
        field_label = "Year of Birth"
        session_key = 'keypad_yob_value'
    
    st.markdown(f'<div class="keypad-title">✍️ Entering: {field_label}</div>', unsafe_allow_html=True)
    
    cols = st.columns(3)
    for i in range(1, 10):
        col_idx = (i - 1) % 3
        with cols[col_idx]:
            if st.button(str(i), key=f"keypad_num_{i}", use_container_width=True):
                current_value = st.session_state[session_key]
                if len(current_value) < max_length:
                    st.session_state[session_key] = current_value + str(i)
                    st.rerun()
    
    cols_bottom = st.columns(3)
    with cols_bottom[0]:
        if st.button("🗑️ Clear", key="keypad_clear", use_container_width=True):
            st.session_state[session_key] = ''
            st.rerun()
    
    with cols_bottom[1]:
        if st.button("0", key="keypad_0", use_container_width=True):
            current_value = st.session_state[session_key]
            if len(current_value) < max_length:
                st.session_state[session_key] = current_value + "0"
                st.rerun()
    
    with cols_bottom[2]:
        if st.button("⌫ Back", key="keypad_back", use_container_width=True):
            current_value = st.session_state[session_key]
            if len(current_value) > 0:
                st.session_state[session_key] = current_value[:-1]
                st.rerun()

def render_sticky_header():
    """Render sticky header with branding"""
    st.markdown("""
        <div class="sticky-header">
            <div class="header-brand">
                <div class="header-logo-icon">🏥</div>
                <div class="header-brand-text">AarogyaQueue</div>
            </div>
            <div class="header-badge">Patient Kiosk</div>
        </div>
    """, unsafe_allow_html=True)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'patient_phone' not in st.session_state:
    st.session_state.patient_phone = None
if 'patient_data' not in st.session_state:
    st.session_state.patient_data = None
if 'token_generated' not in st.session_state:
    st.session_state.token_generated = False

def main():
    """Kiosk Flow Controller"""
    step = st.session_state.kiosk_step
    
    if step == 'HOME':
        render_kiosk_home()
    elif step == 'ACTION':
        render_kiosk_action_selection()
    elif step == 'CHECKIN_LOGIN':
        st.session_state.kiosk_step = 'KIOSK_PHONE'
        st.rerun()
    elif step == 'KIOSK_PHONE':
        render_kiosk_phone_input()
    elif step == 'KIOSK_YOB':
        render_kiosk_yob_input()
    elif step == 'KIOSK_VOICE':
        render_kiosk_voice_input()
    elif step == 'SUCCESS':
        render_kiosk_success()
    else:
        render_kiosk_home()

if __name__ == "__main__":
    main()
