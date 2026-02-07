#!/bin/bash

# Dashboard Setup Verification Script
# Checks all dashboard components are in place

echo "=== MVP Trading Bot Dashboard Setup Verification ==="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

FAILED=0

# Check 1: API Server File
echo -n "✓ Checking api/server.py... "
if [ -f "api/server.py" ]; then
    if grep -q "dashboard_api" api/server.py; then
        echo -e "${GREEN}OK${NC}"
    else
        echo -e "${RED}MISSING DASHBOARD INTEGRATION${NC}"
        FAILED=$((FAILED+1))
    fi
else
    echo -e "${RED}NOT FOUND${NC}"
    FAILED=$((FAILED+1))
fi

# Check 2: Dashboard API File
echo -n "✓ Checking api/dashboard_api.py... "
if [ -f "api/dashboard_api.py" ]; then
    if grep -q "async def get_portfolio" api/dashboard_api.py; then
        echo -e "${GREEN}OK${NC}"
    else
        echo -e "${RED}INCOMPLETE${NC}"
        FAILED=$((FAILED+1))
    fi
else
    echo -e "${RED}NOT FOUND${NC}"
    FAILED=$((FAILED+1))
fi

# Check 3: Static HTML File
echo -n "✓ Checking api/static/index.html... "
if [ -f "api/static/index.html" ]; then
    if grep -q "MVP Trading Bot Dashboard" api/static/index.html; then
        echo -e "${GREEN}OK${NC}"
    else
        echo -e "${RED}INCOMPLETE${NC}"
        FAILED=$((FAILED+1))
    fi
else
    echo -e "${RED}NOT FOUND${NC}"
    FAILED=$((FAILED+1))
fi

# Check 4: Startup Script
echo -n "✓ Checking start_dashboard.sh... "
if [ -f "start_dashboard.sh" ]; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}NOT FOUND${NC}"
    FAILED=$((FAILED+1))
fi

# Check 5: Dashboard Documentation
echo -n "✓ Checking DASHBOARD.md... "
if [ -f "DASHBOARD.md" ]; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}NOT FOUND${NC}"
    FAILED=$((FAILED+1))
fi

# Check 6: Quick Start Guide
echo -n "✓ Checking QUICK_DASHBOARD.md... "
if [ -f "QUICK_DASHBOARD.md" ]; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}NOT FOUND${NC}"
    FAILED=$((FAILED+1))
fi

# Check 7: FastAPI Installation
echo -n "✓ Checking FastAPI installation... "
if pip list 2>/dev/null | grep -q fastapi; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${YELLOW}NOT INSTALLED${NC} (run: pip install fastapi uvicorn)"
fi

# Check 8: Uvicorn Installation  
echo -n "✓ Checking Uvicorn installation... "
if pip list 2>/dev/null | grep -q uvicorn; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${YELLOW}NOT INSTALLED${NC} (run: pip install uvicorn)"
fi

# Check 9: Bot Main File
echo -n "✓ Checking bot/main.py... "
if [ -f "bot/main.py" ]; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}NOT FOUND${NC}"
    FAILED=$((FAILED+1))
fi

# Check 10: Port Availability
echo -n "✓ Checking port 8000 availability... "
if netstat -tuln 2>/dev/null | grep -q "8000\|LISTEN"; then
    echo -e "${YELLOW}IN USE${NC} (dashboard might conflict)"
else
    echo -e "${GREEN}AVAILABLE${NC}"
fi

echo ""
echo "=== Summary ==="

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All dashboard components are in place!${NC}"
    echo ""
    echo "To start the dashboard:"
    echo "  1. Make startup script executable: chmod +x start_dashboard.sh"
    echo "  2. Run: ./start_dashboard.sh"
    echo "  3. Open browser: http://localhost:8000/dashboard"
    echo ""
    echo "For more info: cat QUICK_DASHBOARD.md"
else
    echo -e "${RED}✗ $FAILED component(s) need attention${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Ensure you're in the project root directory"
    echo "  2. Verify git clone was successful"
    echo "  3. Check that files weren't accidentally deleted"
    echo ""
    echo "To reinstall dashboard components:"
    echo "  git pull  # Get latest from repository"
fi

exit $FAILED
