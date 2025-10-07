#!/bin/bash

echo "🚀 Starting Hack PM Development Environment..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env file with your configuration before continuing."
    exit 1
fi

# Start backend first
echo "🐍 Starting Python backend..."
cd backend-python
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

# Start backend in background
uvicorn main:app --reload --port 9000 &
BACKEND_PID=$!

cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "⚛️  Starting React frontend..."
cd frontend
npm install
npm run dev &
FRONTEND_PID=$!

cd ..

echo "✅ Development servers started!"
echo "📊 Frontend: http://localhost:5173"
echo "🔧 Backend API: http://localhost:9000"
echo "📚 API Docs: http://localhost:9000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"

# Function to cleanup on exit
cleanup() {
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup INT TERM

# Wait for processes
wait