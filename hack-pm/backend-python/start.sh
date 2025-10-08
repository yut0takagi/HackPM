#!/bin/bash

echo "🚀 Starting Hack PM Backend Server..."
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ main.py not found. Please run this script from the backend-python directory"
    exit 1
fi

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "📦 Installing dependencies..."
    pip3 install -r requirements.txt
    echo ""
fi

# Start the server
echo "🌐 Server will be available at:"
echo "   http://localhost:8000"
echo "   http://127.0.0.1:8000"
echo ""
echo "📚 API Documentation: http://localhost:8000/docs"
echo "❤️  Health Check: http://localhost:8000/health"
echo "🧪 API Test: http://localhost:8000/api/test"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the server
python3 main.py