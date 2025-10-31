from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import settings
from src.api.resumes import router as resumes_router
from src.api.jobs import router as jobs_router
from src.api.matches import router as matches_router
from src.api.candidates import router as candidates_router
from src.api.skills import router as skills_router
from src.api.interviews import router as interviews_router
from src.api.analytics import router as analytics_router
from src.api.status_notes import router as status_notes_router

app = FastAPI(
    title="IntelliMatch AI", 
    debug=settings.DEBUG,
    version="1.0.0",
    description="AI-powered intelligent resume screening and candidate-job matching platform"
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

@app.get("/")
def read_root():
    return {"message": "Welcome to IntelliMatch AI Resume Screening API"}
