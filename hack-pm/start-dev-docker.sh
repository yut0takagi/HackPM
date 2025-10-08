#!/bin/bash

# Docker開発環境でHack PMを起動するスクリプト

set -e

echo "🚀 Starting Hack PM Development Environment with Docker..."
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

# 既存のコンテナを停止
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.dev.yml down 2>/dev/null || true

# Docker Composeで開発環境を起動
echo "🐳 Starting development services with Docker Compose..."
docker-compose -f docker-compose.dev.yml up --build

echo ""
echo "✅ Development services started!"
echo ""
echo "📍 Frontend: http://localhost:5173"
echo "📍 Backend API: http://localhost:8000"
echo "📍 API Docs: http://localhost:8000/docs"
echo "📍 Health Check: http://localhost:8000/health"