#!/usr/bin/env python3
"""
Server startup script with enhanced logging and error handling
"""
import sys
import os
import logging
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

def setup_logging():
    """Setup enhanced logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('server.log')
        ]
    )

def check_dependencies():
    """Check if all required dependencies are available"""
    required_modules = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'pydantic'
    ]
    
    missing = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    
    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        print("Please install them with: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies available")
    return True

def main():
    """Main server startup function"""
    print("🚀 Starting Hack PM Backend Server...")
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    try:
        # Import after path setup
        import uvicorn
        from main import app
        
        logger.info("Server configuration:")
        logger.info("  Host: 0.0.0.0")
        logger.info("  Port: 8000")
        logger.info("  CORS: Enabled")
        logger.info("  Docs: http://localhost:8000/docs")
        logger.info("  Health: http://localhost:8000/health")
        logger.info("  API Test: http://localhost:8000/api/test")
        
        print("\n📡 Server URLs:")
        print("  🌐 Main: http://localhost:8000")
        print("  📚 Docs: http://localhost:8000/docs")
        print("  ❤️  Health: http://localhost:8000/health")
        print("  🧪 Test: http://localhost:8000/api/test")
        print("\n🔄 Starting server...\n")
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
            access_log=True,
            reload=False  # Set to True for development
        )
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        print(f"❌ Failed to import required modules: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Server startup error: {e}")
        print(f"❌ Server startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()