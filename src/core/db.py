from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.config import settings
from src.models.base import Base  # Import the Base that models use

# Create engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL, 
    echo=False,  # Set to True for SQL query debugging
    future=True,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600    # Recycle connections after 1 hour
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database - create all tables"""
    try:
        # Import all models to register them with Base
        import src.models.candidate
        import src.models.resume
        import src.models.job
        import src.models.match
        import src.models.interview
        import src.models.skill
        import src.models.candidate_skill
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created/verified")
    except Exception as e:
        print(f"⚠️  Database initialization warning: {e}")
        # Try to create tables anyway with basic metadata
        Base.metadata.create_all(bind=engine)

def get_db_session():
    """Get a database session (context manager)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
