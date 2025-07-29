#!/bin/bash

echo "🚀 Starting ApplyX Services..."

# Kill any existing processes
killall python3 2>/dev/null || true
killall node 2>/dev/null || true

echo "✅ Cleaned up existing processes"

# Start backend
echo "🔧 Starting Backend..."
cd backend
source ../venv/bin/activate
python3 app.py &
BACKEND_PID=$!

echo "Backend started with PID: $BACKEND_PID"

# Wait for backend to start
sleep 5

# Go back to root and start frontend
cd ..
echo "🎨 Starting Frontend..."
npm run dev &
FRONTEND_PID=$!

echo "Frontend started with PID: $FRONTEND_PID"

# Wait a bit and test services
sleep 5

echo "🧪 Testing services..."

# Test backend
if curl -s http://localhost:5001/api/health > /dev/null; then
    echo "✅ Backend running on http://localhost:5001"
else
    echo "❌ Backend failed to start"
fi

# Test frontend
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend running on http://localhost:3000"
else
    echo "❌ Frontend failed to start"
fi

echo ""
echo "🎉 Services started! Your credentials:"
echo "📧 Email: shaheersaud2004@gmail.com"
echo "🔑 Password: password123"
echo "🌐 URL: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for Ctrl+C
trap 'echo "Stopping services..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit' INT
wait 