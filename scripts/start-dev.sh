#!/bin/bash
# Startup script for development environment
# Usage: ./scripts/start-dev.sh

set -e  # Exit on error

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo "🚀 Starting AI Tutor Platform (Development Mode)"
echo "=================================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "Creating from .env.example..."
    cp .env.example .env
    echo "✏️  Please edit .env with your API keys"
    echo "🔑 Set GOOGLE_API_KEY before running again"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
REQUIRED_VERSION="3.11"

if [ "$PYTHON_VERSION" != "$REQUIRED_VERSION" ]; then
    echo "⚠️  Python $REQUIRED_VERSION required, found $PYTHON_VERSION"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate 2>/dev/null || . .venv/Scripts/activate 2>/dev/null

# Install dependencies
echo "📚 Installing dependencies..."
pip install -q -e . 2>/dev/null

# Create required directories
mkdir -p chroma_data temp_uploads

# Check if port 8000 is available
if lsof -i :8000 >/dev/null 2>&1 || netstat -ano 2>/dev/null | grep -q ":8000 "; then
    echo "❌ Port 8000 is already in use"
    exit 1
fi

if lsof -i :8501 >/dev/null 2>&1 || netstat -ano 2>/dev/null | grep -q ":8501 "; then
    echo "❌ Port 8501 is already in use"
    exit 1
fi

echo "✅ Environment ready!"
echo ""
echo "🎯 To start services:"
echo ""
echo "   Option 1 - Docker Compose (Recommended):"
echo "   $ docker-compose up"
echo ""
echo "   Option 2 - Separate terminals:"
echo ""
echo "   Terminal 1 (Backend):"
echo "   $ cd backend"
echo "   $ uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "   Terminal 2 (Frontend):"
echo "   $ streamlit run frontend/app.py"
echo ""
echo "📍 Access:"
echo "   - Frontend: http://localhost:8501"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo ""
