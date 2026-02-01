# 🛠️ AarogyaQueue Scripts

## Quick Start

### 🚀 Run Everything (Recommended)
```bash
./scripts/run_all.sh
```
This script will:
1. ✅ Set up/migrate the database
2. ✅ Create all tables
3. ✅ Start Patient Portal (http://localhost:8501)
4. ✅ Start Doctor Portal (http://localhost:8502)

**Press `Ctrl+C` to stop all services**

---

## Individual Scripts

### 📊 Database Setup
```bash
python scripts/setup_db.py
```
- Creates database tables (patients, visits, doctors)
- Inserts sample doctor credentials
- Safe to run multiple times (idempotent)

---

## Code Quality

### 🔍 Lint Code
```bash
./scripts/lint.sh
```
Check for code issues, unused imports, style violations

### 🔧 Auto-Fix Issues
```bash
./scripts/lint-fix.sh
```
Automatically fix linting issues and format code

---

## Logs

Application logs are saved to:
- `logs/patient.log` - Patient portal logs
- `logs/doctor.log` - Doctor portal logs

View logs in real-time:
```bash
tail -f logs/patient.log
tail -f logs/doctor.log
```

---

## Sample Credentials

**Doctor Login:**
- SENIOR Doctor: Role=`SENIOR`, PIN=`1234`
- JUNIOR Doctor: Role=`JUNIOR`, PIN=`5678`
- SENIOR Doctor: Role=`SENIOR`, PIN=`9999`

---

## Troubleshooting

**Port already in use:**
```bash
# Kill processes on port 8501 or 8502
lsof -ti:8501 | xargs kill -9
lsof -ti:8502 | xargs kill -9
```

**Database issues:**
```bash
# Reset database
rm telemedicine_queue.db
python scripts/setup_db.py
```

**Check app status:**
```bash
# See running Streamlit processes
ps aux | grep streamlit
```
