from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from src.core.dependencies import get_db
from src.models.job import Job
from src.schemas.job import JobCreate, JobUpdate, JobResponse
from typing import List
import datetime

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post(
    "/",
    summary="Create a new job posting",
    response_model=JobResponse,
    responses={
        201: {
            "description": "Job created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 5,
                        "title": "Senior Python Engineer",
                        "company": "TechCorp Inc",
                        "department": "Engineering",
                        "location": "Remote",
                        "status": "active",
                        "description": "We're looking for an experienced Python engineer...",
                        "requirements": "5+ years Python, FastAPI, PostgreSQL",
                        "created_at": "2025-11-24T10:30:00"
                    }
                }
            }
        }
    }
)
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    """Create a new job posting with title, description, and requirements."""
    new_job = Job(**job.dict())
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job

@router.get(
    "/",
    summary="List all jobs with filtering",
    response_model=List[JobResponse],
    responses={
        200: {
            "description": "List of jobs matching filters",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "title": "Senior Python Engineer",
                            "company": "TechCorp",
                            "department": "Engineering",
                            "location": "Remote",
                            "status": "active"
                        },
                        {
                            "id": 2,
                            "title": "Data Scientist",
                            "company": "DataCo",
                            "department": "Data Science",
                            "location": "San Francisco",
                            "status": "active"
                        }
                    ]
                }
            }
        }
    }
)
def list_jobs(
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    status: str = Query(None, description="Filter by status: active, closed, or draft"),
    department: str = Query(None, description="Filter by department (case-insensitive partial match)"),
    location: str = Query(None, description="Filter by location (case-insensitive partial match)"),
    db: Session = Depends(get_db)
):
    """
    List all jobs with optional filtering and pagination.
    
    **Example Usage:**
    - Get all active jobs: `?status=active`
    - Filter by department: `?department=Engineering`
    - Remote positions: `?location=Remote`
    - Combine filters: `?status=active&department=Engineering&location=Remote`
    - Pagination: `?skip=20&limit=10` (page 3, 10 per page)
    """
    query = db.query(Job).filter(Job.deleted_at.is_(None))
    
    if status:
        query = query.filter(Job.status == status)
    if department:
        query = query.filter(Job.department.ilike(f"%{department}%"))
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    
    jobs = query.offset(skip).limit(limit).all()
    return jobs

@router.get("/{job_id}", summary="Get job details", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id, Job.deleted_at.is_(None)).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.put("/{job_id}", summary="Update job details", response_model=JobResponse)
def update_job(job_id: int, job_update: JobUpdate, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id, Job.deleted_at.is_(None)).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    for key, value in job_update.dict(exclude_unset=True).items():
        setattr(job, key, value)
    db.commit()
    db.refresh(job)
    return job

@router.delete("/{job_id}", summary="Delete a job (soft delete)")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job.deleted_at = datetime.datetime.utcnow()
    db.commit()
    return {"id": job.id, "deleted": True}


@router.get("/search", summary="Search jobs by keywords")
def search_jobs(
    q: str = Query(..., description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Search jobs by keywords in title and description.
    """
    search_pattern = f"%{q}%"
    jobs = db.query(Job).filter(
        Job.deleted_at.is_(None),
        (Job.title.ilike(search_pattern) | Job.description.ilike(search_pattern))
    ).limit(limit).all()
    
    return jobs


@router.post("/{job_id}/activate", summary="Activate a job posting")
def activate_job(job_id: int, db: Session = Depends(get_db)):
    """
    Change job status to 'active' to start receiving applications.
    """
    job = db.query(Job).filter(Job.id == job_id, Job.deleted_at.is_(None)).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job.status = "active"
    job.updated_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(job)
    
    return job


@router.post("/{job_id}/close", summary="Close a job posting")
def close_job(job_id: int, db: Session = Depends(get_db)):
    """
    Change job status to 'closed' to stop receiving applications.
    """
    job = db.query(Job).filter(Job.id == job_id, Job.deleted_at.is_(None)).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job.status = "closed"
    job.updated_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(job)
    
    return job


@router.get("/stats/summary", summary="Get job statistics")
def get_job_stats(db: Session = Depends(get_db)):
    """
    Get summary statistics about jobs.
    """
    total_jobs = db.query(Job).filter(Job.deleted_at.is_(None)).count()
    active_jobs = db.query(Job).filter(
        Job.deleted_at.is_(None),
        Job.status == "active"
    ).count()
    closed_jobs = db.query(Job).filter(
        Job.deleted_at.is_(None),
        Job.status == "closed"
    ).count()
    draft_jobs = db.query(Job).filter(
        Job.deleted_at.is_(None),
        Job.status == "draft"
    ).count()
    
    return {
        "total": total_jobs,
        "active": active_jobs,
        "closed": closed_jobs,
        "draft": draft_jobs
    }
