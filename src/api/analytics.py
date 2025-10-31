from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.core.dependencies import get_db
from src.models.analytics_event import AnalyticsEvent
from src.models.skill import Skill
from src.models.resume import Resume
from src.models.match import Match
from src.models.job import Job
from src.models.interview import Interview

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/dashboard", summary="Get dashboard metrics")
def dashboard_metrics(db: Session = Depends(get_db)):
    total_resumes = db.query(Resume).filter(Resume.deleted_at.is_(None)).count()
    total_jobs = db.query(Job).filter(Job.deleted_at.is_(None)).count()
    total_matches = db.query(Match).count()
    active_jobs = db.query(Job).filter(Job.status == "active", Job.deleted_at.is_(None)).count()
    scheduled_interviews = db.query(Interview).filter(Interview.status == "scheduled").count()
    
    return {
        "total_resumes": total_resumes,
        "total_jobs": total_jobs,
        "active_jobs": active_jobs,
        "total_matches": total_matches,
        "scheduled_interviews": scheduled_interviews
    }

@router.get("/skills", summary="Get top skills in database")
def top_skills(
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    # Get most common skills across all resumes
    skills = db.query(Skill).limit(limit).all()
    skill_names = [s.name for s in skills]
    return {"skills": skill_names, "count": len(skill_names)}

@router.get("/events", summary="Get analytics events")
def analytics_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    event_type: str = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(AnalyticsEvent).order_by(AnalyticsEvent.created_at.desc())
    if event_type:
        query = query.filter(AnalyticsEvent.event_type == event_type)
    events = query.offset(skip).limit(limit).all()
    return events
