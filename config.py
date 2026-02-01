"""
AarogyaQueue Configuration
Hackathon: Hack Nagpur 2.0
"""

import os
from pathlib import Path

# Project root
BASE_DIR = Path(__file__).parent

# Database
DB_PATH = BASE_DIR / 'telemedicine_queue.db'

# ML Model
MODEL_PATH = BASE_DIR / 'ml' / 'risk_model.pkl'

# Streamlit Ports
PATIENT_PORT = 8501
DOCTOR_PORT = 8502

# AI Settings (optional, for voice processing)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Demo Mode
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"
