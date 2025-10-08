#!/usr/bin/env python3
"""
サーバー起動テスト
"""
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from main import app
    print("✅ App imported successfully")
    
    # Test basic functionality
    print("✅ FastAPI app created")
    print(f"✅ App title: {app.title}")
    print(f"✅ App version: {app.version}")
    
    # Test if we can create a test client
    from fastapi.testclient import TestClient
    client = TestClient(app)
    
    # Test root endpoint
    response = client.get("/")
    print(f"✅ Root endpoint status: {response.status_code}")
    print(f"✅ Root response: {response.json()}")
    
    # Test health endpoint
    response = client.get("/health")
    print(f"✅ Health endpoint status: {response.status_code}")
    print(f"✅ Health response: {response.json()}")
    
    print("\n🎉 All tests passed! Server should work correctly.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)