@echo off
REM Startup script for development environment (Windows)
REM Usage: scripts\start-dev.bat

setlocal enabledelayedexpansion

cd /d "%~dp0\.."
set PROJECT_DIR=%CD%

echo.
echo 🚀 Starting AI Tutor Platform ^(Development Mode^)
echo ==================================================
echo.

REM Check if .env exists
if not exist .env (
    echo ⚠️  .env file not found!
    echo Creating from .env.example...
    copy .env.example .env
    echo ✏️  Please edit .env with your API keys
    echo 🔑 Set GOOGLE_API_KEY before running again
    echo.
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist .venv (
    echo 📦 Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install dependencies
echo 📚 Installing dependencies...
pip install -q -e . >nul 2>&1

REM Create required directories
if not exist chroma_data mkdir chroma_data
if not exist temp_uploads mkdir temp_uploads

echo ✅ Environment ready!
echo.
echo 🎯 To start services:
echo.
echo    Option 1 - Docker Compose ^(Recommended^):
echo    ^> docker-compose up
echo.
echo    Option 2 - Separate terminals:
echo.
echo    Terminal 1 ^(Backend^):
echo    ^> cd backend
echo    ^> uvicorn main:app --reload --host 0.0.0.0 --port 8000
echo.
echo    Terminal 2 ^(Frontend^):
echo    ^> streamlit run frontend\app.py
echo.
echo 📍 Access:
echo    - Frontend: http://localhost:8501
echo    - Backend API: http://localhost:8000
echo    - API Docs: http://localhost:8000/docs
echo.
