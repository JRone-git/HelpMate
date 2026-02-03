@echo off
REM ClawMate Startup Script for Windows

echo 🚀 Starting ClawMate AI Assistant...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH. Please install Python 3.10 or later.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed or not in PATH. Please install Node.js 18 or later.
    pause
    exit /b 1
)

REM Check if npm is installed
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ npm is not installed or not in PATH. Please install npm.
    pause
    exit /b 1
)

REM Install Python dependencies
echo 📦 Installing Python dependencies...
cd core
if not exist requirements.txt (
    echo ❌ requirements.txt not found in core directory
    pause
    exit /b 1
)
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Failed to install Python dependencies
    pause
    exit /b 1
)

REM Install Node.js dependencies
echo 📦 Installing Node.js dependencies...
cd ..\web
if not exist package.json (
    echo ❌ package.json not found in web directory
    pause
    exit /b 1
)
npm install
if %errorlevel% neq 0 (
    echo ❌ Failed to install Node.js dependencies
    pause
    exit /b 1
)

REM Check if Ollama is running
echo 🔍 Checking Ollama status...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Ollama is not running. Please start Ollama first:
    echo    ollama serve
    echo    ollama pull qwen3-coder:latest
    echo.
    set /p continue="Do you want to continue anyway? (y/n): "
    if /i not "%continue%"=="y" (
        exit /b 1
    )
)

REM Start the backend server
echo 🐍 Starting backend server...
cd ..\core
start "ClawMate Backend" cmd /k "python main.py"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start the frontend server
echo 🌐 Starting frontend server...
cd ..\web
start "ClawMate Frontend" cmd /k "npm run dev"

echo ✅ ClawMate is now running!
echo    Backend: http://localhost:8000
echo    Frontend: http://localhost:3000
echo.
echo To stop ClawMate, close both command windows.

pause