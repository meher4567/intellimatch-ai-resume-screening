"""
Simple backend test - verify all imports work
"""
import sys

print("🧪 Testing backend imports...")

try:
    print("1. Testing FastAPI...")
    from fastapi import FastAPI
    print("   ✅ FastAPI OK")
    
    print("2. Testing database...")
    from src.core.db import SessionLocal
    print("   ✅ Database OK")
    
    print("3. Testing routers...")
    from src.api import resumes, jobs, matches
    print("   ✅ Routers OK")
    
    print("4. Testing main app...")
    from src.main import app
    print("   ✅ Main app OK")
    
    print("\n✅ All imports successful!")
    print("\n🚀 Starting server...")
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
