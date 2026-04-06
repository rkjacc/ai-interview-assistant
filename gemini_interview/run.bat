@echo off
setlocal enabledelayedexpansion

echo.
echo === Gemini Interview Q^&A Generator ===
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Check if running from correct directory
if not exist "backend\main.py" (
    echo ERROR: Please run this script from the gemini_interview directory
    pause
    exit /b 1
)

REM Check if virtual environment exists (in parent directory)
if not exist "..\venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found at ..\venv
    echo Please run from the parent directory or create venv there
    pause
    exit /b 1
)

set PYTHON_EXE=..\venv\Scripts\python.exe

echo [1] Installing dependencies...
"!PYTHON_EXE!" -m pip install -q -r requirements.txt
if errorlevel 1 (
    echo WARNING: Some dependencies may have failed
)

echo [2] Starting backend on port 8001...
start "Backend" cmd /k ""!PYTHON_EXE!" backend/main.py"

echo [3] Waiting for backend to initialize...
timeout /t 3 /nobreak

echo [4] Starting frontend on port 8501...
"!PYTHON_EXE!" -m streamlit run frontend/streamlit_app.py

pause
exit /b 0
