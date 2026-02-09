#!/bin/bash

# Fixora Backend - Quick Deployment Script
# This script helps deploy database initialization to your server

echo "========================================================================"
echo "          FIXORA BACKEND - DEPLOYMENT HELPER"
echo "========================================================================"

# Configuration
SERVER_IP="143.244.136.25"
SERVER_USER="root"  # Change this to your SSH username
BACKEND_PATH="/root/Fixora/backend"  # Change this to your actual backend path

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${YELLOW}⚠️  Please update these variables in the script:${NC}"
echo "   SERVER_USER: $SERVER_USER"
echo "   BACKEND_PATH: $BACKEND_PATH"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel and edit the script..."

# Step 1: Upload initialization script
echo ""
echo -e "${BLUE}Step 1: Uploading init_database.py to server...${NC}"
scp init_database.py ${SERVER_USER}@${SERVER_IP}:${BACKEND_PATH}/

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ File uploaded successfully${NC}"
else
    echo -e "${RED}❌ Failed to upload file. Check SSH connection and path.${NC}"
    exit 1
fi

# Step 2: SSH and run initialization
echo ""
echo -e "${BLUE}Step 2: Connecting to server and initializing database...${NC}"
echo ""

ssh ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
cd ${BACKEND_PATH}

echo "Current directory: $(pwd)"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found!"
    exit 1
fi

# Check if venv exists and activate it
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Run initialization
echo "Running database initialization..."
python3 init_database.py

echo ""
echo "✅ Deployment completed!"
ENDSSH

# Step 3: Run tests
echo ""
echo -e "${BLUE}Step 3: Running tests from local machine...${NC}"
echo ""
sleep 2

bash test_backend.sh

echo ""
echo "========================================================================"
echo "                    DEPLOYMENT COMPLETE"
echo "========================================================================"
echo ""
echo "If all tests passed, your backend is ready for Slack bot integration!"
echo ""
