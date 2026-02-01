#!/bin/bash
################################################################################
# AarogyaQueue - One-Click Launcher
# 
# This script starts the complete telemedicine queue system:
# - Patient Kiosk (Port 8501)
# - Doctor Dashboard (Port 8502)
################################################################################

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       🏥 AarogyaQueue System Launcher      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo -e "${YELLOW}📂 Project Directory: $PROJECT_DIR${NC}"
echo ""

# Activate virtual environment if exists
if [ -d "venv" ]; then
    echo -e "${GREEN}✓${NC} Activating virtual environment..."
    source venv/bin/activate
else
    echo -e "${YELLOW}⚠${NC} No virtual environment found. Using system Python."
fi

# Setup database (safe - creates tables if not exist)
echo -e "${GREEN}✓${NC} Initializing database..."
python3 scripts/setup_db.py 2>/dev/null || echo "  (Database already initialized)"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🚀 Starting Applications...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Kill any existing Streamlit processes on these ports
lsof -ti:8501 | xargs kill -9 2>/dev/null || true
lsof -ti:8502 | xargs kill -9 2>/dev/null || true

sleep 1

# Start Patient Kiosk (Port 8501)
echo -e "${GREEN}📱 Patient Kiosk${NC} starting on ${BLUE}http://localhost:8501${NC}"
streamlit run app/patient/app.py \
    --server.port=8501 \
    --server.headless=true \
    --browser.gatherUsageStats=false \
    --server.fileWatcherType=none \
    > /dev/null 2>&1 &
PATIENT_PID=$!

sleep 3

# Start Doctor Dashboard (Port 8502)
echo -e "${GREEN}👨‍⚕️  Doctor Dashboard${NC} starting on ${BLUE}http://localhost:8502${NC}"
streamlit run app/doctor/app.py \
    --server.port=8502 \
    --server.headless=true \
    --browser.gatherUsageStats=false \
    --server.fileWatcherType=none \
    > /dev/null 2>&1 &
DOCTOR_PID=$!

sleep 3

# Check if both apps started successfully
if ps -p $PATIENT_PID > /dev/null && ps -p $DOCTOR_PID > /dev/null; then
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✓ System Ready!${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "  ${GREEN}Patient Portal:${NC}  http://localhost:8501"
    echo -e "  ${GREEN}Doctor Portal:${NC}   http://localhost:8502"
    echo ""
    echo -e "${YELLOW}📋 Sample Credentials:${NC}"
    echo -e "  Doctor Login: Role=${BLUE}SENIOR${NC}, PIN=${BLUE}1234${NC}"
    echo -e "  Doctor Login: Role=${BLUE}JUNIOR${NC}, PIN=${BLUE}5678${NC}"
    echo ""
    echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
    echo ""
    
    # Wait for Ctrl+C
    trap "echo ''; echo -e '${YELLOW}Shutting down...${NC}'; kill $PATIENT_PID $DOCTOR_PID 2>/dev/null; exit 0" INT
    wait
else
    echo ""
    echo -e "${YELLOW}⚠ Error: One or more services failed to start${NC}"
    kill $PATIENT_PID $DOCTOR_PID 2>/dev/null
    exit 1
fi
