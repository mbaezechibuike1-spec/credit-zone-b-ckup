#!/bin/bash

# ============================================================
# CREDIT ZONE - Startup Script
# ============================================================

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Clear screen
clear

echo -e "${BLUE}==================================================${NC}"
echo -e "${GREEN}🚀 CREDIT ZONE STARTUP SCRIPT${NC}"
echo -e "${BLUE}==================================================${NC}"

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo -e "${RED}❌ Error: app.py not found!${NC}"
    echo -e "${YELLOW}📁 Please make sure you're in the credit-zone-backend folder${NC}"
    echo -e "${YELLOW}   Current directory: $(pwd)${NC}"
    echo -e "${YELLOW}   Run: cd ~/credit-zone-backend${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Found app.py in: $(pwd)${NC}"

# Check Python installation
if ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Python not found!${NC}"
    echo -e "${YELLOW}📦 Installing Python...${NC}"
    pkg install python -y
fi

# Check if requirements are installed
echo -e "${YELLOW}📦 Checking dependencies...${NC}"
if ! python -c "import flask" &> /dev/null; then
    echo -e "${YELLOW}📦 Installing Flask and dependencies...${NC}"
    pip install flask flask-cors
fi

# Check data folder
if [ ! -d "data" ]; then
    echo -e "${YELLOW}📁 Creating data folder...${NC}"
    mkdir -p data
fi

# Show status
echo -e "${BLUE}==================================================${NC}"
echo -e "${GREEN}📊 Current Status:${NC}"
echo -e "${YELLOW}   Users:${NC} $(python -c "import json; f=open('data/users.json'); print(len(json.load(f))); f.close()" 2>/dev/null || echo "0")"
echo -e "${YELLOW}   Pending Deposits:${NC} $(python -c "import json; f=open('data/pending.json'); pending=json.load(f); print(len([p for p in pending if not p.get('confirmed')])); f.close()" 2>/dev/null || echo "0")"
echo -e "${YELLOW}   Referrals:${NC} $(python -c "import json; f=open('data/referrals.json'); print(len(json.load(f))); f.close()" 2>/dev/null || echo "0")"
echo -e "${BLUE}==================================================${NC}"

# Check network
echo -e "${YELLOW}🌐 Checking network...${NC}"
IP=$(ifconfig | grep -oP '(?<=inet )\d+\.\d+\.\d+\.\d+' | grep -v 127.0.0.1 | head -1)
if [ -n "$IP" ]; then
    echo -e "${GREEN}✅ Network IP: ${IP}${NC}"
else
    echo -e "${YELLOW}⚠️  Could not detect IP address${NC}"
fi

echo -e "${BLUE}==================================================${NC}"
echo -e "${GREEN}🌐 Server will run on:${NC}"
echo -e "   ${YELLOW}Local:${NC} http://localhost:5000"
echo -e "   ${YELLOW}Network:${NC} http://$IP:5000"
echo -e "   ${YELLOW}Frontend:${NC} http://localhost:5000/static/index.html"
echo -e "${BLUE}==================================================${NC}"
echo -e "${GREEN}💡 Tips:${NC}"
echo -e "   ${YELLOW}• Admin Panel:${NC} python admin.py"
echo -e "   ${YELLOW}• Check Data:${NC} cat data/users.json | python -m json.tool"
echo -e "   ${YELLOW}• Stop Server:${NC} Press CTRL+C"
echo -e "${BLUE}==================================================${NC}"
echo ""

# Ask if user wants to start
read -p "🚀 Start server now? (y/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}👋 Server not started.${NC}"
    echo -e "${YELLOW}   To start manually: python app.py${NC}"
    exit 0
fi

# Start the server
echo -e "${GREEN}🚀 Starting CREDIT ZONE Server...${NC}"
echo -e "${BLUE}==================================================${NC}"
echo -e "${YELLOW}⚠️  Press CTRL+C to stop the server${NC}"
echo -e "${BLUE}==================================================${NC}"
echo ""

python app.py
