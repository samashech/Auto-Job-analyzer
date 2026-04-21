#!/bin/bash
# Project RAIoT - Start Script with Live Scraping Logs
# Usage: ./run.sh

# Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Cleanup function
cleanup() {
    echo ""
    echo -e "${RED}🛑 Shutting down servers...${NC}"
    kill $NEXT_PID 2>/dev/null
    pkill -f "python3 -u app.py" 2>/dev/null
    pkill -f "python app.py" 2>/dev/null
    pkill -f "next dev" 2>/dev/null
    echo -e "${GREEN}✅ All processes stopped${NC}"
    exit 0
}

# Trap Ctrl+C and cleanup
trap cleanup INT TERM

echo -e "${CYAN}=============================================${NC}"
echo -e "${GREEN}🚀  Project RAIoT - Starting...${NC}"
echo -e "${CYAN}=============================================${NC}"
echo ""

# Check if in correct directory
if [ ! -f "app.py" ]; then
    echo -e "${RED}❌ Error: Please run this script from the project root${NC}"
    echo -e "${YELLOW}   cd '/home/samash/Documents/Project RAIoT'${NC}"
    exit 1
fi

# Check if frontend exists
if [ ! -d "frontend" ]; then
    echo -e "${RED}❌ Error: frontend/ directory not found${NC}"
    exit 1
fi

# Store the project root
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"

# Start Next.js frontend in background
echo -e "${YELLOW}📦 Starting Next.js frontend on port 3000...${NC}"
cd "$PROJECT_ROOT/frontend" && nohup npm run dev > /tmp/nextjs.log 2>&1 &
NEXT_PID=$!
cd "$PROJECT_ROOT"

# Wait for Next.js to start (check if port is listening)
echo -n "   Waiting for Next.js..."
for i in $(seq 1 15); do
    sleep 1
    echo -n "."
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo ""
        echo -e "${GREEN}✅ Frontend running: ${CYAN}http://localhost:3000${NC}"
        break
    fi
    if [ $i -eq 15 ]; then
        echo ""
        echo -e "${RED}❌ Next.js failed to start after 15 seconds${NC}"
        echo -e "${YELLOW}   Check logs: cat /tmp/nextjs.log${NC}"
        cat /tmp/nextjs.log
        exit 1
    fi
done

# Start Flask backend in foreground (so you can see logs)
echo -e "${YELLOW}🔥 Starting Flask backend on port 5000...${NC}"
echo -e "${GREEN}✅ Backend running: ${CYAN}http://localhost:5000${NC}"
echo ""
echo -e "${CYAN}=============================================${NC}"
echo -e "${GREEN}🌐 Open in browser: ${CYAN}http://localhost:3000${NC}"
echo -e "${GREEN}📊 API endpoint: ${CYAN}http://localhost:5000${NC}"
echo -e "${CYAN}=============================================${NC}"
echo ""
echo -e "${YELLOW}📋 Scraping logs will appear below when you upload a resume${NC}"
echo -e "${YELLOW}⚠️  Press Ctrl+C to stop all servers${NC}"
echo ""
echo -e "${CYAN}---------------------------------------------${NC}"
echo ""

# Start Flask in foreground - this will show all scraping logs
cd "$PROJECT_ROOT" && python3 -u app.py
