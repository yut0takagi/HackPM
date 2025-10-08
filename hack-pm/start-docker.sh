#!/bin/bash

# Docker環境でHack PMを起動するスクリプト

set -e

echo "🚀 Starting Hack PM with Docker..."
echo ""

# 環境変数ファイルの確認
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration"
fi

# データディレクトリの作成
echo "📁 Creating data directory..."
mkdir -p ./data
chmod 755 ./data

# Docker Composeで起動
echo "🐳 Starting services with Docker Compose..."
docker-compose -f docker-compose.yml up --build -d

echo ""
echo "✅ Services started successfully!"
echo ""
echo "📍 Frontend: http://localhost:5173"
echo "📍 Backend API: http://localhost:8000"
echo "📍 API Docs: http://localhost:8000/docs"
echo "📍 Health Check: http://localhost:8000/health"
echo ""
echo "📊 To view logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 To stop services:"
echo "   docker-compose down"
echo ""
echo "🔄 To restart services:"
echo "   docker-compose restart"