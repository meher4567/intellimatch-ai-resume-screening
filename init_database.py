"""
Initialize database tables for IntelliMatch AI
Run this once to create all required tables
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.db import init_db

if __name__ == "__main__":
    print("🔄 Initializing database...")
    try:
        init_db()
        print("✅ Database initialized successfully!")
        print("\nYou can now start the backend server with:")
        print("  python -m uvicorn src.main:app --reload --port 8000")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)
