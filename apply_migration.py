"""Apply database migrations for authentication fields"""
from src.core.database import engine
import sqlalchemy as sa

print("🔄 Applying database migrations...")

with engine.connect() as conn:
    try:
        # Add new columns if they don't exist
        conn.execute(sa.text("ALTER TABLE users ADD COLUMN IF NOT EXISTS username VARCHAR(50)"))
        conn.execute(sa.text("ALTER TABLE users ADD COLUMN IF NOT EXISTS full_name VARCHAR(255)"))
        conn.execute(sa.text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE"))
        conn.execute(sa.text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE"))
        conn.execute(sa.text("ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP"))
        conn.execute(sa.text("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP"))
        conn.execute(sa.text("ALTER TABLE users ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP"))
        
        # Rename password_hash to hashed_password if needed
        try:
            conn.execute(sa.text("ALTER TABLE users RENAME COLUMN password_hash TO hashed_password"))
            print("  ✅ Renamed password_hash to hashed_password")
        except:
            print("  ℹ️  Column already named hashed_password")
        
        conn.commit()
        print("✅ All migrations applied successfully!")
        
    except Exception as e:
        print(f"❌ Error applying migrations: {e}")
        conn.rollback()
