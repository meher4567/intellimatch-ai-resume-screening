from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from src.core.dependencies import get_db
from src.models.job import Job
from src.schemas.job import JobCreate, JobUpdate, JobResponse
from typing import List
import datetime

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post("/", summary="Create a new job posting", response_model=JobResponse)
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    new_job = Job(**job.dict())
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job

@router.get("/", summary="List all jobs", response_model=List[JobResponse])
def list_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    jobs = db.query(Job).filter(Job.deleted_at.is_(None)).offset(skip).limit(limit).all()
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
