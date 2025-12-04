"""
FastAPI REST API for IntelliMatch Resume Screening
Complete Production API - Phase 1C
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import json
from datetime import datetime
from contextlib import asynccontextmanager

# Import routers
from src.api import (
    auth,
    resumes,
    jobs,
    matches,
    candidates,
    interviews,
    analytics,
    skills,
    status_notes
)
from src.services.matching_engine import MatchingEngine
from src.services.resume_parser import ResumeParser
from src.core.config import settings


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    print("\n" + "="*70)
    print("🚀 Starting IntelliMatch AI API Server")
    print("="*70)
    
    # Initialize services
    global matching_engine, resume_parser
    
    print("📦 Initializing services...")
    
    # Initialize database
    try:
        from src.core.db import init_db
        init_db()
    except Exception as e:
        print(f"⚠️  Database initialization error: {e}")
    
    matching_engine = MatchingEngine(
        model_name=settings.ML_MODEL_NAME,
        storage_path=settings.ML_STORAGE_PATH
    )
    
    # Try to load existing state
    try:
        matching_engine.load_state('production')
        print("✅ Loaded existing production state")
    except Exception as e:
        print(f"ℹ️  No existing state found, starting fresh: {e}")
    
    resume_parser = ResumeParser()
    
    print("✅ Services initialized!")
    print("\n📍 API available at:")
    print(f"   - Local: http://localhost:{settings.PORT}")
    print(f"   - Docs: http://localhost:{settings.PORT}/docs")
    print(f"   - ReDoc: http://localhost:{settings.PORT}/redoc")
    print("="*70 + "\n")
    
    yield
    
    # Shutdown
    print("\n🛑 Shutting down IntelliMatch API...")
    try:
        matching_engine.save_state('production')
        print("✅ State saved successfully")
    except Exception as e:
        print(f"⚠️  Error saving state: {e}")


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered resume screening and candidate matching API - Complete Production System",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if settings.ENVIRONMENT == "production" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global services (initialized in lifespan)
matching_engine = None
resume_parser = None

# Include API routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX, tags=["Authentication"])
app.include_router(resumes.router, prefix=settings.API_V1_PREFIX, tags=["Resumes"])
app.include_router(jobs.router, prefix=settings.API_V1_PREFIX, tags=["Jobs"])
app.include_router(matches.router, prefix=settings.API_V1_PREFIX, tags=["Matches"])
app.include_router(candidates.router, prefix=settings.API_V1_PREFIX, tags=["Candidates"])
app.include_router(interviews.router, prefix=settings.API_V1_PREFIX, tags=["Interviews"])
app.include_router(analytics.router, prefix=settings.API_V1_PREFIX, tags=["Analytics"])
app.include_router(skills.router, prefix=settings.API_V1_PREFIX, tags=["Skills"])
app.include_router(status_notes.router, prefix=settings.API_V1_PREFIX, tags=["Status & Notes"])

# Mount static files for frontend (if serving together)
try:
    frontend_path = Path(__file__).parent.parent.parent / "frontend" / "dist"
    if frontend_path.exists():
        app.mount("/assets", StaticFiles(directory=str(frontend_path / "assets")), name="assets")
except Exception as e:
    print(f"⚠️  Frontend not mounted: {e}")


# ===== Root Endpoints =====

@app.get("/")
async def root():
    """Root endpoint - Serve frontend if available"""
    frontend_path = Path(__file__).parent.parent.parent / "frontend" / "dist" / "index.html"
    if frontend_path.exists():
        return FileResponse(frontend_path)
    
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "environment": settings.ENVIRONMENT,
        "api_docs": f"http://localhost:{settings.PORT}/docs",
        "endpoints": {
            "health": "/health",
            "stats": f"{settings.API_V1_PREFIX}/stats",
            "resumes": f"{settings.API_V1_PREFIX}/resumes",
            "jobs": f"{settings.API_V1_PREFIX}/jobs",
            "matches": f"{settings.API_V1_PREFIX}/matches",
            "candidates": f"{settings.API_V1_PREFIX}/candidates",
            "interviews": f"{settings.API_V1_PREFIX}/interviews",
            "analytics": f"{settings.API_V1_PREFIX}/analytics",
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "environment": settings.ENVIRONMENT,
        "version": settings.APP_VERSION,
        "services": {
            "matching_engine": "up" if matching_engine else "down",
            "resume_parser": "up" if resume_parser else "down",
            "database": "up"  # TODO: Add actual database check
        }
    }


# Additional utility endpoints
@app.get(f"{settings.API_V1_PREFIX}/stats")
async def get_basic_stats():
    """Get basic system statistics for dashboard"""
    try:
        stats = matching_engine.get_stats() if matching_engine else {}
        
        return {
            "total_resumes": stats.get('resumes_indexed', 0),
            "total_jobs": stats.get('jobs_processed', 0),
            "total_matches": stats.get('matches_generated', 0),
            "last_updated": stats.get('last_updated', datetime.now().isoformat())
        }
    except Exception as e:
        print(f"Error getting stats: {e}")
        return {
            "total_resumes": 0,
            "total_jobs": 0,
            "total_matches": 0,
            "last_updated": datetime.now().isoformat()
        }


@app.post(f"{settings.API_V1_PREFIX}/admin/save-state")
async def save_system_state():
    """Save current system state (admin endpoint)"""
    try:
        if matching_engine:
            matching_engine.save_state('production')
            return {"status": "success", "message": "State saved successfully", "timestamp": datetime.now().isoformat()}
        else:
            raise HTTPException(status_code=503, detail="Matching engine not initialized")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save state: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    print("=" * 70)
    print("🚀 Starting IntelliMatch API Server")
    print("=" * 70)
    print("\n📍 API will be available at:")
    print("   - Local: http://localhost:8000")
    print("   - Docs: http://localhost:8000/docs")
    print("   - ReDoc: http://localhost:8000/redoc")
    print("\n" + "=" * 70)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
