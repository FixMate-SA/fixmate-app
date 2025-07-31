#!/usr/bin/env python3
"""
Heroku deployment diagnostic script
"""
import os
import sys
import time

def check_environment():
    """Check critical environment variables"""
    print("🔍 Checking environment variables...")
    
    critical_vars = [
        'PORT', 'DATABASE_URL', 'GEMINI_API_KEY', 
        'DIALOG_360_API_KEY', 'PAYFAST_MERCHANT_ID'
    ]
    
    missing_vars = []
    for var in critical_vars:
        if os.getenv(var):
            print(f"  ✅ {var}: Set")
        else:
            print(f"  ❌ {var}: Missing")
            missing_vars.append(var)
    
    return len(missing_vars) == 0

def test_imports():
    """Test critical imports"""
    print("\n🔍 Testing critical imports...")
    
    try:
        import fastapi
        print(f"  ✅ FastAPI: {fastapi.__version__}")
    except Exception as e:
        print(f"  ❌ FastAPI: {e}")
        return False
    
    try:
        import uvicorn
        print(f"  ✅ Uvicorn: {uvicorn.__version__}")
    except Exception as e:
        print(f"  ❌ Uvicorn: {e}")
        return False
        
    try:
        from sqlalchemy import __version__
        print(f"  ✅ SQLAlchemy: {__version__}")
    except Exception as e:
        print(f"  ❌ SQLAlchemy: {e}")
        return False
    
    return True

def test_database():
    """Test database connection"""
    print("\n🔍 Testing database connection...")
    
    try:
        from database import get_db
        db = next(get_db())
        print("  ✅ Database connection successful")
        db.close()
        return True
    except Exception as e:
        print(f"  ❌ Database connection failed: {e}")
        return False

def test_server_import():
    """Test server import"""
    print("\n🔍 Testing server import...")
    
    try:
        from server import app
        print("  ✅ Server import successful")
        print(f"  ✅ FastAPI app type: {type(app)}")
        return True
    except Exception as e:
        print(f"  ❌ Server import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all diagnostic tests"""
    print("🚀 FixMate-SA Heroku Deployment Diagnostic")
    print("=" * 50)
    
    start_time = time.time()
    
    # Run tests
    env_ok = check_environment()
    imports_ok = test_imports()
    db_ok = test_database()
    server_ok = test_server_import()
    
    end_time = time.time()
    
    print(f"\n⏱️  Total time: {end_time - start_time:.2f} seconds")
    
    # Summary
    print("\n📊 DIAGNOSTIC SUMMARY")
    print("=" * 30)
    print(f"Environment Variables: {'✅' if env_ok else '❌'}")
    print(f"Critical Imports: {'✅' if imports_ok else '❌'}")
    print(f"Database Connection: {'✅' if db_ok else '❌'}")
    print(f"Server Import: {'✅' if server_ok else '❌'}")
    
    if all([env_ok, imports_ok, db_ok, server_ok]):
        print("\n🎉 ALL TESTS PASSED - Server should start successfully!")
        return 0
    else:
        print("\n❌ ISSUES FOUND - Review errors above")
        return 1

if __name__ == "__main__":
    sys.exit(main())