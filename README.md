# 🏥 AarogyaQueue - AI-Powered Telemedicine Queue System

**Team:** Error_404
**Problem:** Long waiting times and inefficient patient triage in clinics

---

## 🎯 Solution

AarogyaQueue is an intelligent queue management system that:
- ✅ Uses AI to assess patient risk from voice/text symptoms
- ✅ Automatically assigns patients to appropriate doctors (Junior/Senior)
- ✅ Optimizes wait times with ML-based risk scoring
- ✅ Works completely **offline** (no cloud dependencies)

---

## 🚀 Quick Start (One Command)

```bash
./scripts/run_all.sh
```

That's it! The system will:
1. Initialize the database
2. Start patient kiosk on **http://localhost:8501**
3. Start doctor dashboard on **http://localhost:8502**

---

## 🔐 Demo Credentials

### Doctor Login
- **Senior Doctor:** Role=`SENIOR`, PIN=`1234`
- **Junior Doctor:** Role=`JUNIOR`, PIN=`5678`

### Patient Login
- Any 10-digit phone number (e.g., `9123456789`)
- Any 4-digit year of birth (e.g., `1990`)
- System auto-registers new patients

---

## 🏗️ Architecture

```
├── app/                    # Streamlit UI applications
│   ├── patient/           # Patient kiosk (voice/text input)
│   └── doctor/            # Doctor dashboard (queue management)
├── db/                    # SQLite database layer
│   ├── connection.py      # Connection management
│   ├── schema.py          # Table definitions
│   ├── patient_repo.py    # Patient operations
│   └── visit_repo.py      # Visit/queue operations
├── ai/                    # AI processing (optional)
│   └── processing.py      # Voice transcription & extraction
├── ml/                    # Machine learning
│   ├── model.py           # Risk prediction
│   └── risk_model.pkl     # Trained model
├── scripts/               # Utility scripts
│   ├── run_all.sh         # One-click launcher
│   └── setup_db.py        # Database initialization
└── telemedicine_queue.db  # SQLite database
```

---

## 🎨 Key Features

1. **Voice Input** - Patients describe symptoms by speaking
2. **AI Risk Scoring** - ML model predicts urgency (0.0 - 1.0)
3. **Smart Routing** - High-risk → Senior doctors, Low-risk → Junior doctors
4. **Real-time Queue** - Doctors see prioritized patient list
5. **Offline Operation** - No internet required during demo

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit (Python)
- **Database:** SQLite (local file)
- **ML:** scikit-learn (Random Forest Regressor)
- **AI (Optional):** Groq/OpenAI for voice processing
- **Architecture:** Repository pattern, clean separation

---

## 📊 Risk Scoring

| Risk Score | Level  | Assigned To    | Example Symptoms           |
|------------|--------|----------------|----------------------------|
| 0.7 - 1.0  | HIGH   | Senior Doctor  | Chest pain, heart attack   |
| 0.4 - 0.7  | MEDIUM | Senior Doctor  | Severe headache, fever     |
| 0.0 - 0.4  | LOW    | Junior Doctor  | Mild cold, minor headache  |

---

## 🧪 Testing

```bash
# Initialize database
python3 scripts/setup_db.py

# Check database
python3 verify_database.py

# Test patient flow
# 1. Open http://localhost:8501
# 2. Register with phone + year of birth
# 3. Enter symptoms
# 4. Get token number

# Test doctor flow
# 1. Open http://localhost:8502
# 2. Login with credentials
# 3. View queue
# 4. Complete consultation
```

---

## 📝 Future Enhancements

- Multi-language support
- SMS notifications for queue updates
- Analytics dashboard for clinic management
- Integration with hospital EMR systems

---

**Built with ❤️**
