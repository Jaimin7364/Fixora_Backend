@echo off
echo ========================================
echo Fixora Backend - Quick Start
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
echo.

REM Check if .env exists
if not exist ".env" (
    echo ⚠️  WARNING: .env file not found!
    echo Please copy .env.example to .env and configure your DATABASE_URL
    echo.
    pause
    exit /b 1
)

REM Start the server
echo ========================================
echo Starting Fixora Backend Server...
echo ========================================
echo.
echo API Documentation: http://localhost:8000/docs
echo Health Check: http://localhost:8000/health
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
