#!/usr/bin/env python3
"""
Test API connectivity from frontend perspective
"""
import sys
import os
import requests
import json
import time
from typing import Dict, Any

def test_api_endpoint(url: str, method: str = "GET", data: Dict[Any, Any] = None) -> Dict[str, Any]:
    """Test a single API endpoint"""
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            return {"success": False, "error": f"Unsupported method: {method}"}
        
        return {
            "success": response.status_code < 400,
            "status_code": response.status_code,
            "response_time": response.elapsed.total_seconds(),
            "content_type": response.headers.get("content-type", ""),
            "data": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text[:200]
        }
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Connection refused - server may not be running"}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timeout"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    """Test API connectivity"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing API Connectivity...")
    print(f"Base URL: {base_url}")
    print("=" * 60)
    
    # Test endpoints
    endpoints = [
        ("/", "GET", None, "Root endpoint"),
        ("/health", "GET", None, "Health check"),
        ("/api/test", "GET", None, "API test endpoint"),
        ("/api/stats", "GET", None, "Statistics"),
        ("/api/repos", "GET", None, "Repositories"),
        ("/api/templates/parse-issue", "POST", {
            "body": "Simple test issue",
            "labels": ["feature"]
        }, "Template parsing"),
    ]
    
    results = []
    
    for endpoint, method, data, description in endpoints:
        url = f"{base_url}{endpoint}"
        print(f"Testing {description}...")
        print(f"  {method} {url}")
        
        result = test_api_endpoint(url, method, data)
        results.append({
            "endpoint": endpoint,
            "description": description,
            "method": method,
            "result": result
        })
        
        if result["success"]:
            print(f"  ✅ SUCCESS ({result['status_code']}) - {result['response_time']:.3f}s")
        else:
            print(f"  ❌ FAILED - {result['error']}")
        
        print()
    
    # Summary
    print("=" * 60)
    print("CONNECTIVITY TEST SUMMARY")
    print("=" * 60)
    
    successful = sum(1 for r in results if r["result"]["success"])
    total = len(results)
    
    print(f"Total endpoints tested: {total}")
    print(f"Successful: {successful}")
    print(f"Failed: {total - successful}")
    print(f"Success rate: {(successful/total)*100:.1f}%")
    
    if successful == total:
        print("\n🎉 All API endpoints are accessible!")
        print("Frontend should be able to connect to the backend.")
    else:
        print(f"\n❌ {total - successful} endpoint(s) failed.")
        print("Troubleshooting steps:")
        print("1. Make sure the backend server is running: python3 main.py")
        print("2. Check if port 8000 is available: lsof -i :8000")
        print("3. Verify CORS settings in main.py")
        print("4. Check firewall settings")
    
    print("\nFailed endpoints:")
    for r in results:
        if not r["result"]["success"]:
            print(f"  ❌ {r['method']} {r['endpoint']} - {r['result']['error']}")
    
    return 0 if successful == total else 1

if __name__ == "__main__":
    sys.exit(main())