#!/bin/bash
# Bash script to run both FastAPI and Streamlit servers
# Works on Linux, Mac, and Windows (Git Bash)

echo ""
echo "========================================"
echo "Gemini Interview Q&A Generator"
echo "========================================"
echo ""

# Detect OS
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    echo "⚠️  You're on Windows!"
    echo "Please use run.bat instead:"
    echo "  run.bat"
    exit 1
fi

# Check if running from correct directory
if [ ! -f "backend/main.py" ]; then
    echo "Error: Please run this script from the gemini_interview directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -f "../venv/bin/activate" ]; then
    echo "Error: Virtual environment not found"
    echo "Please create one: python -m venv ../venv"
    exit 1
fi

# Activate virtual environment
source ../venv/bin/activate

echo "Virtual environment activated"
echo ""

# Start FastAPI backend in background
echo "Starting FastAPI backend..."
python backend/main.py &
BACKEND_PID=$!

sleep 2

# Start Streamlit frontend
echo "Starting Streamlit frontend..."
streamlit run frontend/streamlit_app.py

# Cleanup on exit
kill $BACKEND_PID 2>/dev/null
echo "Cleanup complete"
