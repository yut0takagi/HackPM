#!/bin/bash
set -e

echo "🚀 Starting Hack PM Backend Server..."
echo "📍 API will be available at: http://localhost:8000"
echo "📖 API docs will be available at: http://localhost:8000/docs"
echo "🔍 Health check: http://localhost:8000/health"
echo ""
echo "🗄️  Database: $DATABASE_URL"
echo "🐍 Python path: $PYTHONPATH"
echo ""
echo "=" * 50

# Wait a moment for any dependencies
sleep 2

# Start the application
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level info