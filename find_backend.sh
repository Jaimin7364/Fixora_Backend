#!/bin/bash
# Commands to find Fixora backend on your server

echo "======================================================================"
echo "  FINDING FIXORA BACKEND ON SERVER"
echo "======================================================================"

# 1. Check running Python/FastAPI processes
echo ""
echo "1. Checking running processes for FastAPI/uvicorn..."
echo "----------------------------------------------------------------------"
ps aux | grep -E "uvicorn|fastapi|main.py" | grep -v grep

# 2. Check common deployment locations
echo ""
echo "2. Searching common directories..."
echo "----------------------------------------------------------------------"
find /root /home /opt /var/www -maxdepth 3 -name "main.py" -type f 2>/dev/null | grep -E "Fixora|fixora|backend"

# 3. Search for Fixora directory
echo ""
echo "3. Searching for 'Fixora' or 'backend' directories..."
echo "----------------------------------------------------------------------"
find /root /home /opt /var/www -maxdepth 4 -type d -name "*Fixora*" -o -name "*fixora*" -o -name "*backend*" 2>/dev/null

# 4. Search for requirements.txt with fastapi
echo ""
echo "4. Searching for backend by requirements.txt..."
echo "----------------------------------------------------------------------"
find /root /home /opt /var/www -maxdepth 4 -name "requirements.txt" -type f 2>/dev/null | while read file; do
    if grep -q "fastapi" "$file" 2>/dev/null; then
        echo "Found: $(dirname $file)"
    fi
done

# 5. Check if there's a systemd service
echo ""
echo "5. Checking systemd services..."
echo "----------------------------------------------------------------------"
systemctl list-units --type=service --all | grep -E "fixora|backend|fastapi"

# 6. Check port 8000 (your backend port)
echo ""
echo "6. Checking what's listening on port 8000..."
echo "----------------------------------------------------------------------"
lsof -i :8000 2>/dev/null || ss -tulpn | grep :8000

# 7. Check for .env file with DATABASE_URL
echo ""
echo "7. Searching for .env files with DATABASE_URL..."
echo "----------------------------------------------------------------------"
find /root /home /opt /var/www -maxdepth 4 -name ".env" -type f 2>/dev/null | while read file; do
    if grep -q "DATABASE_URL" "$file" 2>/dev/null; then
        echo "Found: $(dirname $file)"
    fi
done

echo ""
echo "======================================================================"
echo "  MANUAL SEARCH COMMANDS"
echo "======================================================================"
echo ""
echo "Try these commands manually:"
echo ""
echo "# Search in current user's home"
echo "find ~ -name main.py -o -name requirements.txt | grep -i fixora"
echo ""
echo "# Search everywhere (slower)"
echo "find / -name \"*Fixora*\" -type d 2>/dev/null"
echo ""
echo "# Check process working directory"
echo "lsof -i :8000 | grep python"
echo "pwdx \$(pgrep -f uvicorn)"
echo ""
