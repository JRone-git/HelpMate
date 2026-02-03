#!/bin/bash

# ClawMate Startup Script
echo "🚀 Starting ClawMate AI Assistant..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python 3.10 or later."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18 or later."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm."
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
cd core
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found in core directory"
    exit 1
fi

pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install Python dependencies"
    exit 1
fi

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
cd ../web
if [ ! -f "package.json" ]; then
    echo "❌ package.json not found in web directory"
    exit 1
fi

npm install
if [ $? -ne 0 ]; then
    echo "❌ Failed to install Node.js dependencies"
    exit 1
fi

# Check if Ollama is running
echo "🔍 Checking Ollama status..."
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "⚠️  Ollama is not running. Please start Ollama first:"
    echo "   ollama serve"
    echo "   ollama pull qwen3-coder:latest"
    echo ""
    read -p "Do you want to continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Start the backend server
echo "🐍 Starting backend server..."
cd ../core
python3 main.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start the frontend server
echo "🌐 Starting frontend server..."
cd ../web
npm run dev &
FRONTEND_PID=$!

echo "✅ ClawMate is now running!"
echo "   Backend: http://localhost:8000"
echo "   Frontend: http://localhost:3000"
echo ""
echo "To stop ClawMate, press Ctrl+C or run:"
echo "   kill $BACKEND_PID $FRONTEND_PID"

# Wait for user to stop
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait