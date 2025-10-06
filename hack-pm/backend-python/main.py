from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os
from typing import Dict, Any

app = FastAPI(title="Hack PM Python API", version="1.0.0")

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GoバックエンドのURL
GO_API_URL = "http://backend-go:8080/api"

class RepositoryRequest(BaseModel):
    template_repo: str = "keel"
    project_name: str

@app.get("/")
async def root():
    return {"message": "Hack PM Python API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/api/stats")
async def get_stats():
    """プロジェクト統計情報を取得"""
    try:
        # Goバックエンドからプロジェクト一覧を取得
        print(f"Requesting: {GO_API_URL}/projects")
        response = requests.get(f"{GO_API_URL}/projects", timeout=10)
        print(f"Response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Error response: {response.text}")
            raise HTTPException(status_code=500, detail=f"プロジェクトデータの取得に失敗しました: {response.status_code}")
        
        projects = response.json()
        print(f"Projects received: {len(projects)}")
        
        total = len(projects)
        active = len([p for p in projects if p.get("status") == "active"])
        completed = len([p for p in projects if p.get("status") == "completed"])
        
        return {
            "total": total,
            "active": active,
            "completed": completed
        }
    except requests.ConnectionError as e:
        print(f"Connection error: {str(e)}")
        # Goバックエンドに接続できない場合はダミーデータを返す
        return {
            "total": 0,
            "active": 0,
            "completed": 0,
            "error": "Goバックエンドに接続できません"
        }
    except requests.RequestException as e:
        print(f"Request error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"統計情報の取得に失敗しました: {str(e)}")

@app.post("/api/projects/{project_id}/repository")
async def create_repository(project_id: int):
    """プロジェクト用のリポジトリを作成（Keelテンプレートから）"""
    try:
        # プロジェクト情報を取得
        response = requests.get(f"{GO_API_URL}/projects/{project_id}")
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="プロジェクトが見つかりません")
        
        project = response.json()
        
        # 実際の実装では、ここでGitHubやGitLabのAPIを使用してリポジトリを作成
        # 今回はモックとして処理
        repository_url = f"https://github.com/hackathon/{project['name'].lower().replace(' ', '-')}"
        
        # Keelテンプレートからリポジトリを作成する処理をシミュレート
        # 実際の実装では以下のような処理を行う：
        # 1. GitHub/GitLab APIでリポジトリ作成
        # 2. Keelテンプレートをクローン
        # 3. 新しいリポジトリにプッシュ
        
        return {
            "message": "リポジトリが正常に作成されました",
            "repository_url": repository_url,
            "template_used": "keel",
            "project_id": project_id
        }
        
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"リポジトリの作成に失敗しました: {str(e)}")

@app.get("/api/templates")
async def get_templates():
    """利用可能なテンプレート一覧を取得"""
    templates = [
        {
            "name": "keel",
            "description": "ハッカソン用の基本テンプレート",
            "technologies": ["React", "Node.js", "Docker"],
            "url": "https://github.com/hackathon/keel"
        },
        {
            "name": "keel-python",
            "description": "Python/FastAPI版テンプレート",
            "technologies": ["React", "FastAPI", "Docker"],
            "url": "https://github.com/hackathon/keel-python"
        },
        {
            "name": "keel-go",
            "description": "Go版テンプレート",
            "technologies": ["React", "Go", "Docker"],
            "url": "https://github.com/hackathon/keel-go"
        }
    ]
    return templates

@app.post("/api/analyze/project")
async def analyze_project(project_data: Dict[str, Any]):
    """プロジェクトデータを分析して推奨事項を提供"""
    try:
        # プロジェクトの複雑さや技術スタックに基づいて推奨事項を生成
        recommendations = []
        
        if "AI" in project_data.get("description", "").upper():
            recommendations.append({
                "type": "technology",
                "message": "AI機能にはPythonとTensorFlow/PyTorchの使用を推奨します",
                "priority": "high"
            })
        
        if "API" in project_data.get("description", "").upper():
            recommendations.append({
                "type": "architecture",
                "message": "RESTful APIの設計パターンを推奨します",
                "priority": "medium"
            })
        
        if len(project_data.get("description", "")) > 200:
            recommendations.append({
                "type": "scope",
                "message": "プロジェクトスコープが大きい可能性があります。MVP（最小実行可能製品）に焦点を当てることを推奨します",
                "priority": "high"
            })
        
        return {
            "analysis": {
                "complexity": "medium",
                "estimated_duration": "2-3 days",
                "team_size_recommendation": "3-4 people"
            },
            "recommendations": recommendations
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"プロジェクト分析に失敗しました: {str(e)}")

@app.post("/api/ideas/generate")
async def generate_ideas(prompt: Dict[str, Any]):
    """アイデアを生成"""
    try:
        # AIを使ったアイデア生成のシミュレーション
        theme = prompt.get("theme", "")
        technology = prompt.get("technology", "")
        difficulty = prompt.get("difficulty", "medium")
        duration = prompt.get("duration", "48h")
        
        # サンプルアイデア生成
        sample_ideas = [
            {
                "title": f"{theme}を活用したスマート管理システム",
                "description": f"{technology}を使用して{theme}分野の課題を解決するWebアプリケーション",
                "technologies": [technology, "React", "PostgreSQL"] if technology else ["React", "Node.js", "PostgreSQL"],
                "features": [
                    "ユーザー認証システム",
                    "データ可視化ダッシュボード",
                    "リアルタイム通知機能",
                    "モバイル対応UI"
                ],
                "difficulty": difficulty,
                "estimated_hours": 24 if duration == "24h" else 48
            },
            {
                "title": f"{theme} × IoTモニタリングシステム",
                "description": f"IoTセンサーと{technology}を組み合わせたリアルタイム監視システム",
                "technologies": [technology, "IoT", "WebSocket"] if technology else ["Python", "IoT", "WebSocket"],
                "features": [
                    "センサーデータ収集",
                    "異常検知アラート",
                    "データ分析機能",
                    "API連携"
                ],
                "difficulty": difficulty,
                "estimated_hours": 36 if duration == "48h" else 24
            },
            {
                "title": f"{theme}コミュニティプラットフォーム",
                "description": f"{theme}に興味のある人々をつなぐソーシャルプラットフォーム",
                "technologies": [technology, "React", "Socket.io"] if technology else ["React", "Node.js", "Socket.io"],
                "features": [
                    "ユーザープロフィール",
                    "チャット機能",
                    "イベント管理",
                    "マッチング機能"
                ],
                "difficulty": difficulty,
                "estimated_hours": 48 if duration == "72h" else 36
            }
        ]
        
        return {"ideas": sample_ideas}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"アイデア生成に失敗しました: {str(e)}")

@app.get("/api/templates/service")
async def get_service_templates(type: str = "web-app"):
    """サービステンプレート一覧を取得"""
    templates = {
        "web-app": [
            {
                "name": "react-node",
                "description": "React + Node.js + PostgreSQL",
                "type": "web-app",
                "technologies": ["React", "Node.js", "PostgreSQL", "Docker"],
                "files": ["frontend/", "backend/", "docker-compose.yml"]
            },
            {
                "name": "react-python",
                "description": "React + FastAPI + PostgreSQL",
                "type": "web-app", 
                "technologies": ["React", "FastAPI", "PostgreSQL", "Docker"],
                "files": ["frontend/", "backend/", "docker-compose.yml"]
            }
        ],
        "api": [
            {
                "name": "fastapi-basic",
                "description": "FastAPI REST API",
                "type": "api",
                "technologies": ["FastAPI", "PostgreSQL", "Docker"],
                "files": ["main.py", "models/", "routers/", "Dockerfile"]
            },
            {
                "name": "go-gin",
                "description": "Go + Gin REST API",
                "type": "api",
                "technologies": ["Go", "Gin", "PostgreSQL", "Docker"],
                "files": ["main.go", "handlers/", "models/", "Dockerfile"]
            }
        ]
    }
    
    return templates.get(type, [])

@app.post("/api/services/generate")
async def generate_service(config: Dict[str, Any]):
    """サービスを生成"""
    try:
        service_name = config.get("name")
        service_type = config.get("type", "web-app")
        template = config.get("template", "react-node")
        features = config.get("features", [])
        
        # サービス生成のシミュレーション
        generated_files = []
        
        if template == "react-node":
            generated_files = [
                {
                    "path": "package.json",
                    "content": f'{{\n  "name": "{service_name}",\n  "version": "1.0.0",\n  "scripts": {{\n    "start": "node server.js",\n    "dev": "nodemon server.js"\n  }}\n}}'
                },
                {
                    "path": "server.js",
                    "content": f'const express = require("express");\nconst app = express();\n\napp.get("/", (req, res) => {{\n  res.json({{ message: "Welcome to {service_name}!" }});\n}});\n\nconst PORT = process.env.PORT || 3000;\napp.listen(PORT, () => {{\n  console.log(`Server running on port ${{PORT}}`);\n}});'
                },
                {
                    "path": "Dockerfile",
                    "content": "FROM node:16\nWORKDIR /app\nCOPY package*.json ./\nRUN npm install\nCOPY . .\nEXPOSE 3000\nCMD [\"npm\", \"start\"]"
                }
            ]
        
        # 機能に応じてファイルを追加
        if "ユーザー認証" in features:
            generated_files.append({
                "path": "auth.js",
                "content": "// ユーザー認証機能\nconst jwt = require('jsonwebtoken');\n\n// JWT認証ミドルウェア\nconst authenticateToken = (req, res, next) => {\n  // 認証ロジック\n};\n\nmodule.exports = { authenticateToken };"
            })
        
        return {"files": generated_files, "message": "サービスが正常に生成されました"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"サービス生成に失敗しました: {str(e)}")

@app.post("/api/discord/notify")
async def send_discord_notification(data: Dict[str, Any]):
    """Discord通知を送信"""
    try:
        webhook_url = data.get("webhook_url")
        message = data.get("message")
        
        if not webhook_url or not message:
            raise HTTPException(status_code=400, detail="webhook_urlとmessageは必須です")
        
        # Discord Webhook送信のシミュレーション
        # 実際の実装では requests.post(webhook_url, json={"content": message})
        print(f"Discord notification: {message}")
        
        return {"message": "通知が送信されました"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Discord通知の送信に失敗しました: {str(e)}")

@app.get("/api/dashboard")
async def get_dashboard_data():
    """ダッシュボードデータを取得"""
    try:
        # Mock dashboard data
        stats = {
            "totalFeatures": 12,
            "completedFeatures": 8,
            "activeMembers": 5,
            "activeBranches": 7,
            "upcomingDeadlines": 3,
            "overdueTasks": 2
        }
        
        recent_activity = [
            {
                "type": "feature",
                "message": "ユーザー認証機能が完了しました",
                "time": "2時間前",
                "user": "田中"
            },
            {
                "type": "branch",
                "message": "feature/payment-integrationブランチが作成されました",
                "time": "4時間前",
                "user": "佐藤"
            },
            {
                "type": "merge",
                "message": "feature/user-profileがdevelopにマージされました",
                "time": "6時間前",
                "user": "鈴木"
            }
        ]
        
        return {
            "stats": stats,
            "recentActivity": recent_activity
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ダッシュボードデータの取得に失敗しました: {str(e)}")

@app.post("/api/projects/{project_id}/github/workflow")
async def create_github_workflow(project_id: int):
    """GitHub Workflowを作成"""
    try:
        # GitHub Workflow YAML生成
        workflow_content = """name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '16'
    - name: Install dependencies
      run: npm install
    - name: Run tests
      run: npm test
    - name: Build
      run: npm run build

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v3
    - name: Deploy to production
      run: echo "Deploying to production..."
"""
        
        return {
            "message": "GitHub Workflowが作成されました",
            "workflow_file": ".github/workflows/ci-cd.yml",
            "content": workflow_content
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GitHub Workflow作成に失敗しました: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)