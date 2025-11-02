"""
FastAPI REST API for IntelliMatch Resume Screening
Provides endpoints for resume upload, job posting, and candidate matching
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import json
from datetime import datetime
import uuid

from src.services.matching_engine import MatchingEngine
from src.services.resume_parser import ResumeParser

# Initialize FastAPI app
app = FastAPI(
    title="IntelliMatch API",
    description="AI-powered resume screening and candidate matching API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
matching_engine = None
resume_parser = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global matching_engine, resume_parser
    
    print("🚀 Starting IntelliMatch API...")
    
    # Initialize matching engine
    matching_engine = MatchingEngine(
        model_name='mini',
        storage_path='data/production'
    )
    
    # Try to load existing state
    try:
        matching_engine.load_state('production')
        print("✅ Loaded existing production state")
    except Exception as e:
        print(f"ℹ️ No existing state found, starting fresh: {e}")
    
    # Initialize resume parser
    resume_parser = ResumeParser()
    
    print("✅ IntelliMatch API ready!")


# ===== Request/Response Models =====

class JobRequest(BaseModel):
    """Job posting request"""
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    description: str = Field(..., description="Full job description")
    required_skills: List[str] = Field(default=[], description="Required skills")
    preferred_skills: List[str] = Field(default=[], description="Preferred skills")
    min_experience_years: Optional[int] = Field(None, description="Minimum years of experience")
    education_requirements: Optional[str] = Field(None, description="Education requirements")
    location: Optional[str] = Field(None, description="Job location")


class MatchRequest(BaseModel):
    """Request to find matching candidates"""
    job_id: str = Field(..., description="Job ID to match against")
    top_k: int = Field(50, description="Number of candidates to return", ge=1, le=200)
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional filters")


class CandidateResponse(BaseModel):
    """Candidate match response"""
    resume_id: str
    name: str
    email: Optional[str]
    score: float
    tier: str
    skills_match: float
    experience_match: float
    education_match: float
    explanation: str


class JobResponse(BaseModel):
    """Job response"""
    job_id: str
    title: str
    company: str
    status: str
    created_at: str


class StatsResponse(BaseModel):
    """System statistics response"""
    total_resumes: int
    total_jobs: int
    total_matches: int
    last_updated: Optional[str]


# ===== API Endpoints =====

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "IntelliMatch API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "resumes": "/api/v1/resumes",
            "jobs": "/api/v1/jobs",
            "matches": "/api/v1/matches"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "matching_engine": "up" if matching_engine else "down",
            "resume_parser": "up" if resume_parser else "down"
        }
    }


@app.post("/api/v1/resumes/upload", status_code=201)
async def upload_resume(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Upload and parse a resume
    
    - **file**: PDF or DOCX resume file
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.docx', '.doc')):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only PDF and DOCX files are supported."
            )
        
        # Generate unique resume ID
        resume_id = f"resume_{uuid.uuid4().hex[:8]}_{file.filename}"
        
        # Save uploaded file temporarily
        temp_path = Path(f"data/uploads/{resume_id}")
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        
        content = await file.read()
        with open(temp_path, 'wb') as f:
            f.write(content)
        
        # Parse resume
        parsed_data = resume_parser.parse(str(temp_path))
        
        # Index in matching engine
        matching_engine.index_resume(parsed_data, resume_id)
        
        # Clean up temp file
        temp_path.unlink()
        
        return {
            "resume_id": resume_id,
            "filename": file.filename,
            "status": "indexed",
            "candidate_name": parsed_data.get('personal_info', {}).get('name', 'Unknown'),
            "skills_count": len(parsed_data.get('skills', {}).get('all_skills', [])),
            "experience_years": sum(exp.get('duration_months', 0) for exp in parsed_data.get('experience', [])) // 12,
            "quality_score": parsed_data.get('metadata', {}).get('quality_score', 0)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process resume: {str(e)}")


@app.post("/api/v1/resumes/batch-upload", status_code=201)
async def batch_upload_resumes(files: List[UploadFile] = File(...)):
    """
    Upload multiple resumes at once
    
    - **files**: List of PDF/DOCX resume files
    """
    results = []
    errors = []
    
    for file in files:
        try:
            # Process each file
            resume_id = f"resume_{uuid.uuid4().hex[:8]}_{file.filename}"
            temp_path = Path(f"data/uploads/{resume_id}")
            temp_path.parent.mkdir(parents=True, exist_ok=True)
            
            content = await file.read()
            with open(temp_path, 'wb') as f:
                f.write(content)
            
            parsed_data = resume_parser.parse(str(temp_path))
            matching_engine.index_resume(parsed_data, resume_id)
            
            temp_path.unlink()
            
            results.append({
                "resume_id": resume_id,
                "filename": file.filename,
                "status": "success"
            })
            
        except Exception as e:
            errors.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return {
        "total": len(files),
        "successful": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors
    }


@app.post("/api/v1/jobs/create", status_code=201, response_model=JobResponse)
async def create_job(job: JobRequest):
    """
    Create a new job posting
    
    - **job**: Job details including title, description, and requirements
    """
    try:
        # Generate job ID
        job_id = f"job_{uuid.uuid4().hex[:8]}"
        
        # Parse job description
        job_data = matching_engine.parse_job(job.description)
        
        # Enhance with additional fields
        job_data.update({
            'job_id': job_id,
            'title': job.title,
            'company': job.company,
            'required_skills': job.required_skills,
            'preferred_skills': job.preferred_skills,
            'min_experience_years': job.min_experience_years,
            'education_requirements': job.education_requirements,
            'location': job.location,
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        })
        
        # Save job to disk
        jobs_path = Path('data/jobs')
        jobs_path.mkdir(parents=True, exist_ok=True)
        
        with open(jobs_path / f"{job_id}.json", 'w') as f:
            json.dump(job_data, f, indent=2)
        
        return JobResponse(
            job_id=job_id,
            title=job.title,
            company=job.company,
            status='active',
            created_at=job_data['created_at']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create job: {str(e)}")


@app.post("/api/v1/matches/find", response_model=List[CandidateResponse])
async def find_matches(request: MatchRequest):
    """
    Find matching candidates for a job
    
    - **request**: Match request with job_id and filtering options
    """
    try:
        # Load job data
        job_path = Path(f'data/jobs/{request.job_id}.json')
        if not job_path.exists():
            raise HTTPException(status_code=404, detail=f"Job {request.job_id} not found")
        
        with open(job_path, 'r') as f:
            job_data = json.load(f)
        
        # Find matches
        matches = matching_engine.find_matches(
            job_data,
            top_k=request.top_k,
            filters=request.filters
        )
        
        # Format response
        candidates = []
        for match in matches:
            candidates.append(CandidateResponse(
                resume_id=match['resume_id'],
                name=match['name'],
                email=match.get('email'),
                score=round(match['final_score'], 2),
                tier=match['tier'],
                skills_match=round(match['component_scores']['skills'] * 100, 2),
                experience_match=round(match['component_scores']['experience'] * 100, 2),
                education_match=round(match['component_scores']['education'] * 100, 2),
                explanation=match['explanation']['summary']
            ))
        
        return candidates
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to find matches: {str(e)}")


@app.get("/api/v1/jobs/{job_id}")
async def get_job(job_id: str):
    """Get job details by ID"""
    try:
        job_path = Path(f'data/jobs/{job_id}.json')
        if not job_path.exists():
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        with open(job_path, 'r') as f:
            return json.load(f)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job: {str(e)}")


@app.get("/api/v1/jobs")
async def list_jobs():
    """List all jobs"""
    try:
        jobs_path = Path('data/jobs')
        if not jobs_path.exists():
            return []
        
        jobs = []
        for job_file in jobs_path.glob('*.json'):
            with open(job_file, 'r') as f:
                job_data = json.load(f)
                jobs.append({
                    'job_id': job_data['job_id'],
                    'title': job_data['title'],
                    'company': job_data['company'],
                    'status': job_data['status'],
                    'created_at': job_data['created_at']
                })
        
        return jobs
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list jobs: {str(e)}")


@app.get("/api/v1/stats", response_model=StatsResponse)
async def get_stats():
    """Get system statistics"""
    try:
        stats = matching_engine.get_stats()
        
        return StatsResponse(
            total_resumes=stats['resumes_indexed'],
            total_jobs=stats['jobs_processed'],
            total_matches=stats['matches_generated'],
            last_updated=stats.get('last_updated')
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@app.post("/api/v1/admin/save-state")
async def save_state():
    """Save current system state (admin endpoint)"""
    try:
        matching_engine.save_state('production')
        return {"status": "success", "message": "State saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save state: {str(e)}")


@app.delete("/api/v1/resumes/{resume_id}")
async def delete_resume(resume_id: str):
    """Delete a resume from the system"""
    # TODO: Implement resume deletion from vector store
    raise HTTPException(status_code=501, detail="Not implemented yet")


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
