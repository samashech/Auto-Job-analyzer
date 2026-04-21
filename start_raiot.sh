#!/bin/bash
# Cleaner startup script for RAIoT
# Usage: ./start_raiot.sh

# Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}=============================================${NC}"
echo -e "${GREEN}🚀 Starting Project RAIoT System...${NC}"
echo -e "${CYAN}=============================================${NC}"

# Ensure we are in the project root
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

# Cleanup on exit
cleanup() {
    echo ""
    echo -e "${RED}🛑 Stopping all services...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}
trap cleanup INT TERM

# Start Flask Backend
echo -e "${YELLOW}📦 Starting Flask Backend (Port 5000)...${NC}"
python3 -u app.py > backend.log 2>&1 &
BACKEND_PID=$!

# Wait for Backend
echo -n "   Waiting for Backend..."
for i in {1..10}; do
    sleep 1
    echo -n "."
    if curl -s http://localhost:5000 > /dev/null 2>&1; then
        echo -e " ${GREEN}OK${NC}"
        break
    fi
done

# Start Next.js Frontend
echo -e "${YELLOW}🎨 Starting Next.js Frontend (Port 3000)...${NC}"
cd frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!

echo -n "   Waiting for Frontend..."
for i in {1..30}; do
    sleep 1
    echo -n "."
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e " ${GREEN}OK${NC}"
        break
    fi
done

echo ""
echo -e "${GREEN}✅ System is LIVE!${NC}"
echo -e "${CYAN}👉 Frontend: http://localhost:3000${NC}"
echo -e "${CYAN}👉 Backend:  http://localhost:5000${NC}"
echo ""
echo -e "${YELLOW}📝 Logs are being saved to backend.log and frontend.log${NC}"
echo -e "${YELLOW}🛑 Press Ctrl+C to stop all services${NC}"
echo ""

echo -e "${YELLOW}🔍 Showing live Backend/Scraping Logs below...${NC}"
echo -e "${CYAN}---------------------------------------------${NC}"

# Return to project root before tailing
cd "$PROJECT_ROOT"

# Keep script running and tail the backend log
tail -f backend.log
