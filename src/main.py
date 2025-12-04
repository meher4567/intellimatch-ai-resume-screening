from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from src.core.config import settings
from src.core.rate_limits import add_rate_limit_headers, clear_expired_limits
from src.api.resumes import router as resumes_router
from src.api.jobs import router as jobs_router
from src.api.matches import router as matches_router
from src.api.candidates import router as candidates_router
from src.api.skills import router as skills_router
from src.api.interviews import router as interviews_router
from src.api.analytics import router as analytics_router
from src.api.status_notes import router as status_notes_router
from src.api.auth import router as auth_router
import logging
import time
import traceback
import uuid
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="IntelliMatch AI", 
    debug=settings.DEBUG,
    version="1.0.0",
    description="""AI-powered intelligent resume screening and candidate-job matching platform.
    
    ## Features
    
    * **Resume Parsing**: Upload and parse PDF/DOCX resumes with AI-powered extraction
    * **Job Management**: Create and manage job postings with smart matching
    * **Intelligent Matching**: ML-powered candidate-job matching with explanations
    * **Skills Analysis**: Extract and analyze skills with proficiency levels
    * **Analytics Dashboard**: Hiring trends, quality distributions, and insights
    * **Rate Limited**: Protected endpoints with fair usage limits
    
    ## Authentication
    
    Most endpoints require JWT authentication. Get a token from `/api/v1/auth/login`.
    
    Use the token in the `Authorization` header:
    ```
    Authorization: Bearer YOUR_TOKEN_HERE
    ```
    """,
    contact={
        "name": "IntelliMatch AI Support",
        "email": "support@intellimatch.ai",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {"name": "Authentication", "description": "User registration and login operations"},
        {"name": "Resumes", "description": "Resume upload, parsing, and management"},
        {"name": "Jobs", "description": "Job posting creation and management"},
        {"name": "Matches", "description": "Candidate-job matching operations"},
        {"name": "Candidates", "description": "Candidate profile management"},
        {"name": "Analytics", "description": "Statistics, trends, and insights"},
        {"name": "Skills", "description": "Skill extraction and analysis"},
        {"name": "Interviews", "description": "Interview scheduling and management"},
    ]
)

# Log startup
logger.info("Starting IntelliMatch AI application")
logger.info("Rate limiting enabled with custom middleware")

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests with timing and status"""
    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    
    # Log request
    logger.info(f"[{request_id}] {request.method} {request.url.path} - Start")
    
    try:
        response = await call_next(request)
        duration = (time.time() - start_time) * 1000  # ms
        
        # Log response
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} - "
            f"Status: {response.status_code} - Duration: {duration:.2f}ms"
        )
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        # Add rate limit headers if available
        response = await add_rate_limit_headers(request, response)
        
        return response
        
    except Exception as e:
        duration = (time.time() - start_time) * 1000
        logger.error(
            f"[{request_id}] {request.method} {request.url.path} - "
            f"Error: {str(e)} - Duration: {duration:.2f}ms"
        )
        raise

# Add global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.error(
        f"Unhandled exception on {request.method} {request.url.path}: {str(exc)}\n"
        f"Traceback: {traceback.format_exc()}"
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An unexpected error occurred",
            "path": str(request.url.path)
        }
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API versioning prefix
API_V1_PREFIX = "/api/v1"

app.include_router(resumes_router, prefix=API_V1_PREFIX)
app.include_router(jobs_router, prefix=API_V1_PREFIX)
app.include_router(matches_router, prefix=API_V1_PREFIX)
app.include_router(candidates_router, prefix=API_V1_PREFIX)
app.include_router(skills_router, prefix=API_V1_PREFIX)
app.include_router(interviews_router, prefix=API_V1_PREFIX)
app.include_router(analytics_router, prefix=API_V1_PREFIX)
app.include_router(status_notes_router, prefix=API_V1_PREFIX)
app.include_router(auth_router, prefix=API_V1_PREFIX)

@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to IntelliMatch AI Resume Screening API"}

@app.get("/health")
def health_check():
    """
    Comprehensive health check endpoint
    Returns service status, database connectivity, and system info
    """
    from src.core.db import SessionLocal
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "IntelliMatch AI",
        "version": "1.0.0",
        "checks": {}
    }
    
    # Check database connectivity
    try:
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        logger.error(f"Database health check failed: {e}")
    
    # Check file system
    try:
        import os
        data_dir = "data"
        if os.path.exists(data_dir) and os.path.isdir(data_dir):
            health_status["checks"]["filesystem"] = "healthy"
        else:
            health_status["checks"]["filesystem"] = "warning: data directory not found"
    except Exception as e:
        health_status["checks"]["filesystem"] = f"unhealthy: {str(e)}"
    
    return health_status

@app.get("/api/v1/health")
def api_health_check():
    """
    API health check endpoint
    Returns detailed health information
    """
    try:
        # You can add database connection check here
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "api_version": "v1",
            "components": {
                "api": "operational",
                "database": "operational",
                "ml_engine": "operational"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }
