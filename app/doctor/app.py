import streamlit as st
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd
from datetime import datetime
import json
import time
from db.visit_repo import (
    verify_doctor, 
    get_next_visit_for_tier, 
    mark_visit_completed, 
    get_visit_by_id,
    get_waiting_visits,
    get_completed_visits
)
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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Reset & Standards */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 16px;
    }
    
    /* Hide Streamlit defaults */
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* App background - Clean solid color */
    .stApp {
        background: #F4F7F8;
    }
    
    /* Sticky Header - Consistent styling */
    .sticky-header {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background: #FFFFFF;
        border-bottom: 1px solid #E5E7EB;
        padding: 1rem 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        z-index: 1000;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    .header-brand {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .header-logo-icon {
        font-size: 1.75rem;
    }
    
    .header-brand-text {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1F2937;
    }
    
    /* Main Content Container */
    .main-content {
        margin-top: 90px;
        max-width: 1400px;
        margin-left: auto;
        margin-right: auto;
        padding: 2rem;
    }
    .doctor-info-header {
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    
    .doctor-name-header {
        font-size: 1rem;
        font-weight: 700;
        color: #1F2937;
    }
    
    .doctor-role-header {
        font-size: 0.85rem;
        color: #6B7280;
        font-weight: 500;
    }
    
    .live-indicator {
        background: #16A34A;
        color: white;
        padding: 0.5rem 1.25rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    /* Dashboard Tabs */
    .dashboard-tabs {
        margin-bottom: 2rem;
        max-width: 400px;
    }
    
    /* Queue Panel Header */
    .queue-panel-header {
        background: #F4F7F8;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin-bottom: 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid #E5E7EB;
    }
    
    .queue-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1F2937;
    }
    
    .queue-count {
        background: #0E9F8A;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.85rem;
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
    
    /* Queue Cards with Risk Colors */
    .queue-card {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        border: 2px solid #E5E7EB;
        transition: all 0.2s ease;
    }
    
    .queue-card-high {
        border-left: 4px solid #DC2626;
    }
    
    .queue-card-medium {
        border-left: 4px solid #D97706;
    }
    
    .queue-card-low {
        border-left: 4px solid #16A34A;
    }
    
    .queue-card:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        transform: translateY(-1px);
    }
    
    .queue-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    
    .queue-token {
        font-weight: 700;
        font-size: 1rem;
        color: #1F2937;
    }
    
    /* Risk Badges */
    .risk-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .risk-badge.risk-high {
        background: #FEE2E2;
        color: #991B1B;
    }
    
    .risk-badge.risk-medium {
        background: #FEF3C7;
        color: #92400E;
    }
    
    .risk-badge.risk-low {
        background: #D1FAE5;
        color: #065F46;
    }
    
    .queue-score {
        font-size: 0.8rem;
        color: #6B7280;
        margin-top: 0.25rem;
    }
    
    /* Consultation Title */
    .consult-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #1F2937;
        margin-bottom: 1.5rem;
    }
    
    /* Patient Info Card */
    .patient-info-card {
        background: #FFFFFF;
        border: 2px solid #E5E7EB;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    
    .patient-info-row {
        display: flex;
        justify-content: space-between;
        align-items: start;
    }
    
    .patient-name-large {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1F2937;
        margin-bottom: 0.5rem;
    }
    
    .patient-meta {
        color: #6B7280;
        font-size: 0.9rem;
    }
    
    .token-display-badge {
        background: #0E9F8A;
        color: white;
        padding: 0.5rem 1.25rem;
        border-radius: 8px;
        font-weight: 700;
        font-size: 1rem;
    }
    
    /* AI Section Title */
    .ai-section-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #6B7280;
        margin: 1.5rem 0 0.75rem;
    }
    
    .assistive-label {
        font-size: 0.8rem;
        color: #9CA3AF;
        font-weight: 500;
        font-style: italic;
    }
    
    /* AI Summary Panel - Soft Blue, Assistive */
    .ai-summary-panel {
        background: #F0F9FF;
        border: 1px solid #BAE6FD;
        border-radius: 8px;
        padding: 1.25rem;
        margin-bottom: 1.5rem;
    }
    
    .ai-disclaimer {
        font-size: 0.7rem;
        color: #7C3AED;
        font-weight: 500;
        margin-bottom: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.3px;
        opacity: 0.8;
    }
    
    .ai-content-limited {
        color: #475569;
        line-height: 1.6;
        white-space: pre-line;
        font-size: 0.85rem;
        max-height: 5.5rem;
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 4;
        -webkit-box-orient: vertical;
    }
    
    .ai-content-empty {
        color: #9CA3AF;
        font-style: italic;
        font-size: 0.85rem;
    }
    
    .ai-footer {
        margin-top: 0.75rem;
        padding-top: 0.75rem;
        border-top: 1px solid #BAE6FD;
        font-size: 0.75rem;
        color: #9CA3AF;
    }
    
    /* Section Label */
    .section-label {
        font-size: 1rem;
        font-weight: 700;
        color: #1F2937;
        margin: 1.25rem 0 0.75rem;
    }
    
    /* History Section */
    .history-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #E5E7EB;
    }
    
    .history-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1F2937;
    }
    
    .history-count {
        background: #F4F7F8;
        color: #6B7280;
        padding: 0.5rem 1rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    /* History Card - Clean & Scannable */
    .history-card {
        background: #FFFFFF;
        border: 2px solid #E5E7EB;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 0.75rem;
        transition: all 0.2s ease;
    }
    
    .history-card:hover {
        border-color: #0E9F8A;
        box-shadow: 0 4px 12px rgba(14, 159, 138, 0.1);
    }
    
    .history-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .history-card-left {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .history-token {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1F2937;
    }
    
    .history-patient {
        font-size: 1rem;
        color: #6B7280;
    }
    
    .history-card-right {
        display: flex;
        align-items: center;
        gap: 1rem;
        flex-direction: column;
        align-items: flex-end;
    }
    
    .history-time {
        font-size: 0.85rem;
        color: #16A34A;
        font-weight: 500;
    }
    
    /* History Details (Expandable) */
    .history-details {
        padding: 1rem 0;
    }
    
    .history-section {
        margin-bottom: 1.5rem;
    }
    
    .history-section-label {
        font-size: 0.9rem;
        font-weight: 700;
        color: #1F2937;
        margin-bottom: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .history-info-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        background: #F9FAFB;
        padding: 1rem;
        border-radius: 8px;
    }
    
    .history-info-item {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
    }
    
    .history-info-label {
        font-size: 0.75rem;
        color: #9CA3AF;
        font-weight: 600;
    }
    
    .history-info-value {
        font-size: 0.95rem;
        color: #1F2937;
        font-weight: 600;
    }
    
    .history-content-box {
        background: #F9FAFB;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 1rem;
        color: #475569;
        line-height: 1.6;
        font-size: 0.9rem;
    }
    
    .history-ai-box {
        background: #F0F9FF;
        border: 1px solid #BAE6FD;
        border-radius: 8px;
        padding: 1rem;
        color: #475569;
        line-height: 1.6;
        font-size: 0.85rem;
    }
    
    .history-doctor-box {
        background: #ECFDF5;
        border: 2px solid #10B981;
        border-radius: 8px;
        padding: 1.25rem;
        color: #065F46;
        line-height: 1.7;
        font-size: 0.95rem;
        font-weight: 500;
    }
    
    /* Emergency Alert */
    .emergency-alert {
        background: #FEF2F2;
        border: 2px solid #EF4444;
        border-radius: 8px;
        padding: 1rem;
        color: #991B1B;
        font-weight: 600;
        text-align: center;
    }
    
    /* Button Styling - Consistent across app */
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.625rem 1.25rem !important;
        transition: all 0.2s ease !important;
        font-size: 0.9rem !important;
        border: none !important;
    }
    
    .stButton > button[kind="primary"] {
        background: #0E9F8A !important;
        color: white !important;
        box-shadow: 0 2px 8px rgba(14, 159, 138, 0.25) !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: #0B7F6E !important;
        box-shadow: 0 4px 12px rgba(14, 159, 138, 0.35) !important;
        transform: translateY(-1px) !important;
    }
    
    .stButton > button[kind="secondary"] {
        background: #F4F7F8 !important;
        color: #6B7280 !important;
        border: 1px solid #E5E7EB !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: #E5E7EB !important;
        color: #1F2937 !important;
    }
    
    /* Input Styling - Consistent */
    .stTextArea textarea, .stTextInput input {
        border-radius: 8px !important;
        border: 1px solid #E5E7EB !important;
        padding: 0.625rem 1rem !important;
        font-size: 0.9rem !important;
    }
    
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #0E9F8A !important;
        box-shadow: 0 0 0 3px rgba(14, 159, 138, 0.1) !important;
    }
    
    /* Select Box - Consistent */
    .stSelectbox > div > div {
        border-radius: 8px !important;
        border: 1px solid #E5E7EB !important;
    }
    
    /* Info/Success/Warning boxes */
    .stAlert {
        border-radius: 8px !important;
        border: none !important;
    }
    
    /* Expander - Consistent */
    .streamlit-expanderHeader {
        border-radius: 8px !important;
        background: #F9FAFB !important;
        border: 1px solid #E5E7EB !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
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
    
    .header-badge-doctor {
        background: linear-gradient(135deg, #1F2937 0%, #374151 100%);
        color: #FFFFFF;
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
    
    /* Minimal Professional Doctor Login Card */
    .doctor-login-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 16px;
        padding: 3rem 2.5rem;
        max-width: 440px;
        margin: 3rem auto;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
    }
    
    /* Login Header - Minimal */
    .doctor-login-header {
        text-align: center;
        margin-bottom: 2.5rem;
        padding-bottom: 2rem;
        border-bottom: 1px solid #E5E7EB;
    }
    
    .doctor-login-icon {
        font-size: 3.5rem;
        margin-bottom: 1rem;
        line-height: 1;
    }
    
    .doctor-login-title {
        font-size: 1.75rem;
        font-weight: 700;
        color: #1F2937;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }
    
    .doctor-login-subtitle {
        font-size: 0.9rem;
        color: #6B7280;
        font-weight: 500;
    }
    
    /* Form Section */
    .form-section {
        margin-bottom: 1.5rem;
    }
    
    /* PIN Label with Security Badge */
    .pin-label {
        font-weight: 600;
        color: #1F2937;
        font-size: 0.95rem;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .security-badge {
        font-size: 0.75rem;
        color: #6B7280;
        background: #F4F7F8;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-weight: 500;
        border: 1px solid #E5E7EB;
    }
    
    /* Old login card styles (kept for compatibility) */
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
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = time.time()
if 'show_history' not in st.session_state:
    st.session_state.show_history = False

def login_page():
    # Sticky header
    st.markdown("""
        <div class="sticky-header">
            <div class="header-brand">
                <div class="header-logo-icon">🏥</div>
                <div class="header-brand-text">AarogyaQueue</div>
            </div>
            <div class="header-badge-doctor">Doctor Portal</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Main content wrapper
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    # Centered login card
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        st.markdown('<div class="doctor-login-card">', unsafe_allow_html=True)
        
        # Minimal header
        st.markdown("""
            <div class="doctor-login-header">
                <div class="doctor-login-icon">👨‍⚕️</div>
                <div class="doctor-login-title">Doctor Access</div>
                <div class="doctor-login-subtitle">Secure authentication required</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Role selection
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        role = st.selectbox(
            "Role", 
            ["JUNIOR", "SENIOR"],
            label_visibility="visible"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # PIN input with security cue
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown('<div class="pin-label">Access PIN <span class="security-badge">🔒 Secure</span></div>', unsafe_allow_html=True)
        pin = st.text_input(
            "PIN", 
            type="password", 
            placeholder="Enter 4-digit PIN",
            label_visibility="collapsed",
            max_chars=4
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.write("")
        
        # Login button
        if st.button("Access Portal", type="primary", use_container_width=True):
            try:
                doctor = verify_doctor(role, pin)
                
                if doctor:
                    st.session_state.doctor_auth = True
                    st.session_state.doctor_info = doctor
                    st.success(f"✓ Welcome, Dr. {doctor['name']}")
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please verify your role and PIN.")
            except Exception as e:
                st.error(f"Authentication failed: {str(e)}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def complete_visit(visit_id, diagnosis, prescription):
    try:
        mark_visit_completed(visit_id, diagnosis)
        return True
    except Exception as e:
        st.error(f"Error completing visit: {e}")
        return False

def dashboard():
    doc = st.session_state.doctor_info
    
    # Auto-refresh mechanism: Rerun every 5 seconds
    # This simulates real-time updates by polling the database
    current_time = time.time()
    if current_time - st.session_state.last_refresh > 5:
        st.session_state.last_refresh = current_time
        st.rerun()
    
    # Sticky Header with Doctor Info
    st.markdown(f"""
        <div class="sticky-header">
            <div class="header-brand">
                <div class="header-logo-icon">🏥</div>
                <div class="header-brand-text">AarogyaQueue</div>
            </div>
            <div class="doctor-info-header">
                <div class="doctor-name-header">Dr. {doc['name']}</div>
                <div class="doctor-role-header">{doc['role_tier']} Resident</div>
            </div>
            <div class="live-indicator">🟢 Live</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Main content wrapper
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    # Tabs for Live Queue / History
    st.markdown('<div class="dashboard-tabs">', unsafe_allow_html=True)
    tab_col1, tab_col2 = st.columns([1, 1])
    with tab_col1:
        if st.button("📋 Live Queue", use_container_width=True, 
                    type="primary" if not st.session_state.show_history else "secondary",
                    key="tab_queue"):
            st.session_state.show_history = False
            st.rerun()
    with tab_col2:
        if st.button("📚 History", use_container_width=True,
                    type="primary" if st.session_state.show_history else "secondary",
                    key="tab_history"):
            st.session_state.show_history = True
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Main Content
    if not st.session_state.show_history:
        # LIVE QUEUE VIEW - Left Panel + Center Panel Layout
        queue = get_waiting_visits(doc['role_tier'])
        
        # Two-column layout: Queue (Left) | Consultation (Center/Right)
        col_queue, col_consult = st.columns([1, 2], gap="large")
        
        with col_queue:
            # Left Panel: Live Queue
            st.markdown(f"""
                <div class="queue-panel-header">
                    <div class="queue-title">Waiting Queue</div>
                    <div class="queue-count">{len(queue)} patients</div>
                </div>
            """, unsafe_allow_html=True)
            
            if not queue:
                st.markdown("""
                    <div class="empty-state">
                        <div class="empty-icon">🎉</div>
                        <div>No patients waiting</div>
                    </div>
                """, unsafe_allow_html=True)
            
            for i, patient in enumerate(queue):
                visit_id = patient['id']
                score = patient['risk_score']
                
                # Determine risk level and color
                if score > 0.7:
                    risk_badge = '<span class="risk-badge risk-high">High Risk</span>'
                    risk_class = "queue-card-high"
                elif score > 0.4:
                    risk_badge = '<span class="risk-badge risk-medium">Medium Risk</span>'
                    risk_class = "queue-card-medium"
                else:
                    risk_badge = '<span class="risk-badge risk-low">Low Risk</span>'
                    risk_class = "queue-card-low"
                
                with st.container():
                    st.markdown(f"""
                        <div class="queue-card {risk_class}">
                            <div class="queue-card-header">
                                <div class="queue-token">T-{visit_id:08d}</div>
                                {risk_badge}
                            </div>
                            <div class="queue-score">Score: {score:.2f}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"Select", key=f"btn_{visit_id}", use_container_width=True):
                        st.session_state.current_patient = patient
                        st.rerun()
        
        with col_consult:
            # Center Panel: Current Consultation
            if 'current_patient' in st.session_state and st.session_state.current_patient:
                p = st.session_state.current_patient
                
                st.markdown('<div class="consult-title">🏥 Current Consultation</div>', unsafe_allow_html=True)
                
                # Patient Card
                st.markdown(f"""
                    <div class="patient-info-card">
                        <div class="patient-info-row">
                            <div>
                                <div class="patient-name-large">{p.get('patient_name') or 'Unknown Patient'}</div>
                                <div class="patient-meta">YOB: {p.get('patient_yob', 'N/A')}</div>
                            </div>
                            <div class="token-display-badge">T-{p['id']:08d}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # AI Summary in Soft Blue Panel - Assistive Only
                st.markdown('<div class="ai-section-title">🤖 AI Clinical Summary <span class="assistive-label">(Assistive)</span></div>', unsafe_allow_html=True)
                
                if p.get('ai_summary'):
                    st.markdown(f"""
                        <div class="ai-summary-panel">
                            <div class="ai-disclaimer">AI-generated suggestion • Not a diagnosis • For reference only</div>
                            <div class="ai-content-limited">{p['ai_summary']}</div>
                            <div class="ai-footer">
                                Risk Score: {p.get('risk_score', 0):.2f} • Level: {p.get('risk_level', 'UNKNOWN')}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div class="ai-summary-panel">
                            <div class="ai-content-empty">AI summary not available for this visit</div>
                            <div class="ai-footer">
                                Risk Score: {p.get('risk_score', 0):.2f} • Level: {p.get('risk_level', 'UNKNOWN')}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                
                # Emergency Check
                if p.get('symptoms_list'):
                    try:
                        symptoms_text = p.get('symptoms_raw', '')
                        if any(w in symptoms_text.lower() for w in ['heart attack', 'stroke', 'bleeding', 'unconscious', 'chest pain']):
                            st.markdown("""
                                <div class="emergency-alert">
                                    🚨 EMERGENCY KEYWORDS DETECTED - PRIORITIZE
                                </div>
                            """, unsafe_allow_html=True)
                    except:
                        pass
                
                # Symptoms
                st.markdown('<div class="section-label">🗣️ Reported Symptoms</div>', unsafe_allow_html=True)
                st.info(p.get('symptoms_raw', 'No symptoms recorded'))
                
                st.write("")
                
                # Doctor Actions
                st.markdown('<div class="section-label">📝 Diagnosis & Treatment</div>', unsafe_allow_html=True)
                
                diagnosis = st.text_area("Doctor's Notes / Diagnosis", height=100, placeholder="Enter your diagnosis...")
                prescription = st.text_area("Prescription", height=100, placeholder="Medication name, dosage, frequency...")
                
                st.write("")
                
                col_complete, col_skip = st.columns(2)
                
                with col_complete:
                    if st.button("✅ Complete Visit", type="primary", use_container_width=True):
                        if diagnosis:
                            if complete_visit(p['id'], diagnosis, prescription):
                                st.success("✅ Visit completed!")
                                del st.session_state.current_patient
                                st.rerun()
                        else:
                            st.warning("⚠️ Please enter a diagnosis")
                
                with col_skip:
                    if st.button("⏭️ Skip for Now", use_container_width=True):
                        del st.session_state.current_patient
                        st.rerun()
            else:
                # No patient selected
                st.markdown("""
                    <div class="empty-state" style="margin-top: 4rem;">
                        <div class="empty-icon">👈</div>
                        <div style="font-size: 1.1rem; color: #6B7280;">Select a patient from the queue</div>
                    </div>
                """, unsafe_allow_html=True)
    
    else:
        # HISTORY VIEW - Redesigned
        history = get_completed_visits(tier=doc['role_tier'], limit=20)
        
        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        
        st.markdown(f"""
            <div class="history-header">
                <div class="history-title">📚 Consultation History</div>
                <div class="history-count">{len(history)} completed</div>
            </div>
        """, unsafe_allow_html=True)
        
        if not history:
            st.markdown("""
                <div class="empty-state">
                    <div class="empty-icon">📋</div>
                    <div>No completed consultations yet</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            for h in history:
                # Determine risk badge
                risk_level = h.get('risk_level', 'UNKNOWN')
                if risk_level == 'HIGH':
                    risk_badge_html = '<span class="risk-badge risk-high">High Risk</span>'
                elif risk_level == 'MEDIUM':
                    risk_badge_html = '<span class="risk-badge risk-medium">Medium Risk</span>'
                elif risk_level == 'LOW':
                    risk_badge_html = '<span class="risk-badge risk-low">Low Risk</span>'
                else:
                    risk_badge_html = '<span class="risk-badge" style="background: #E5E7EB; color: #6B7280;">Unknown</span>'
                
                # Format completion time
                completed_time = h.get('completed_at', 'N/A')
                
                # Card header (always visible)
                st.markdown(f"""
                    <div class="history-card">
                        <div class="history-card-header">
                            <div class="history-card-left">
                                <div class="history-token">T-{h['id']:08d}</div>
                                <div class="history-patient">{h.get('patient_name', 'Unknown Patient')}</div>
                            </div>
                            <div class="history-card-right">
                                {risk_badge_html}
                                <div class="history-time">✓ {completed_time}</div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Expandable details
                with st.expander("View Details", expanded=False):
                    st.markdown('<div class="history-details">', unsafe_allow_html=True)
                    
                    # Patient Info
                    st.markdown(f"""
                        <div class="history-section">
                            <div class="history-section-label">Patient Information</div>
                            <div class="history-info-grid">
                                <div class="history-info-item">
                                    <span class="history-info-label">Name:</span>
                                    <span class="history-info-value">{h.get('patient_name', 'Unknown')}</span>
                                </div>
                                <div class="history-info-item">
                                    <span class="history-info-label">YOB:</span>
                                    <span class="history-info-value">{h.get('patient_yob', 'N/A')}</span>
                                </div>
                                <div class="history-info-item">
                                    <span class="history-info-label">Risk Score:</span>
                                    <span class="history-info-value">{h.get('risk_score', 0):.2f}</span>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Symptoms
                    st.markdown(f"""
                        <div class="history-section">
                            <div class="history-section-label">🗣️ Reported Symptoms</div>
                            <div class="history-content-box">
                                {h.get('symptoms_raw', 'No symptoms recorded')}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # AI Summary (if available)
                    if h.get('ai_summary'):
                        ai_summary_text = h['ai_summary'].replace('\n', '<br>')
                        st.markdown(f"""
                            <div class="history-section">
                                <div class="history-section-label">🤖 AI Clinical Summary <span style="font-size: 0.75rem; color: #9CA3AF; font-style: italic;">(Assistive)</span></div>
                                <div class="history-ai-box">
                                    {ai_summary_text}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    # Doctor's Notes (Prominent)
                    if h.get('doctor_notes'):
                        doctor_notes_text = h['doctor_notes'].replace('\n', '<br>')
                        st.markdown(f"""
                            <div class="history-section">
                                <div class="history-section-label">📝 Doctor's Diagnosis & Notes</div>
                                <div class="history-doctor-box">
                                    {doctor_notes_text}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                            <div class="history-section">
                                <div class="history-section-label">📝 Doctor's Diagnosis & Notes</div>
                                <div class="history-content-box" style="color: #D97706; font-style: italic;">
                                    No diagnosis recorded
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    # Prescription (if available)
                    if h.get('prescription'):
                        prescription_text = h['prescription'].replace('\n', '<br>')
                        st.markdown(f"""
                            <div class="history-section">
                                <div class="history-section-label">💊 Prescription</div>
                                <div class="history-content-box">
                                    {prescription_text}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Logout in sidebar
    with st.sidebar:
        st.write("")
        st.write("")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.doctor_auth = False
            st.session_state.doctor_info = None
            st.session_state.show_history = False
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
