#!/bin/bash

# ApplyX LinkedIn Bot Startup Script
# This script starts both the backend and frontend services

echo "🚀 Starting ApplyX LinkedIn Bot..."
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please run: python3 setup_secrets.py"
    exit 1
fi

# Load environment variables
source .env 2>/dev/null

echo "✅ Environment variables loaded"
echo ""

# Function to kill processes on script exit
cleanup() {
    echo ""
    echo "🛑 Stopping ApplyX services..."
    pkill -f "python3.*app.py" 2>/dev/null
    pkill -f "npm.*dev" 2>/dev/null
    pkill -f "next.*dev" 2>/dev/null
    echo "✅ Services stopped"
    exit 0
}

# Set up cleanup on script exit
trap cleanup SIGINT SIGTERM EXIT

echo "🔧 Starting Backend Server..."
cd backend
python3 app.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

echo "🎨 Starting Frontend Server..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "🎉 ApplyX is now running!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend:  http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop both services"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID 