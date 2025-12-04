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

@router.get(
    "/stats",
    summary="Get basic statistics for dashboard",
    responses={
        200: {
            "description": "Dashboard statistics",
            "content": {
                "application/json": {
                    "example": {
                        "total_resumes": 127,
                        "total_jobs": 23,
                        "total_matches": 456,
                        "active_jobs": 15
                    }
                }
            }
        }
    }
)
def basic_stats(db: Session = Depends(get_db)):
    """
    Get basic statistics for dashboard overview.
    
    Returns counts of:
    - Total resumes uploaded
    - Total jobs posted
    - Total candidate-job matches
    - Currently active jobs
    """
    total_resumes = db.query(Resume).filter(Resume.deleted_at.is_(None)).count()
    total_jobs = db.query(Job).filter(Job.deleted_at.is_(None)).count()
    total_matches = db.query(Match).count()
    active_jobs = db.query(Job).filter(Job.status == "active", Job.deleted_at.is_(None)).count()
    
    return {
        "total_resumes": total_resumes,
        "total_jobs": total_jobs,
        "total_matches": total_matches,
        "active_jobs": active_jobs
    }

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

@router.get(
    "/skills",
    summary="Get most common skills across candidates",
    responses={
        200: {
            "description": "List of skills with frequency counts",
            "content": {
                "application/json": {
                    "example": [
                        {"skill": "Python", "count": 89},
                        {"skill": "JavaScript", "count": 67},
                        {"skill": "SQL", "count": 54},
                        {"skill": "React", "count": 43},
                        {"skill": "Docker", "count": 38}
                    ]
                }
            }
        }
    }
)
def top_skills(
    limit: int = Query(50, ge=1, le=500, description="Maximum number of skills to return"),
    db: Session = Depends(get_db)
):
    """
    Get most frequently occurring skills across all candidates.
    
    Useful for:
    - Understanding skill demand in your candidate pool
    - Identifying trending technologies
    - Skills gap analysis
    - Talent pool insights
    """
    # Get most common skills across all resumes with frequency counts
    from src.models.candidate import Candidate
    
    candidates = db.query(Candidate).filter(
        Candidate.deleted_at.is_(None),
        Candidate.skills.isnot(None)
    ).all()
    
    # Count skill frequencies
    skill_counts = {}
    for candidate in candidates:
        if candidate.skills:
            candidate_skills = [s.strip() for s in candidate.skills.split(",")]
            for skill in candidate_skills:
                skill_lower = skill.lower()
                skill_counts[skill_lower] = skill_counts.get(skill_lower, 0) + 1
    
    # Sort by frequency and take top N
    top_skills_list = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    return {
        "skills": [{"name": skill, "count": count} for skill, count in top_skills_list],
        "total_unique_skills": len(skill_counts),
        "top_n": len(top_skills_list)
    }

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


@router.get("/trends/hiring", summary="Get hiring trends")
def hiring_trends(db: Session = Depends(get_db)):
    """
    Analyze hiring trends based on job postings and candidate activity.
    """
    from datetime import datetime, timedelta
    from src.models.candidate import Candidate
    
    # Jobs created in last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_jobs = db.query(Job).filter(
        Job.created_at >= thirty_days_ago,
        Job.deleted_at.is_(None)
    ).count()
    
    # Resumes uploaded in last 30 days
    recent_resumes = db.query(Resume).filter(
        Resume.created_at >= thirty_days_ago,
        Resume.deleted_at.is_(None)
    ).count()
    
    # Active vs closed jobs
    active_jobs = db.query(Job).filter(
        Job.status == "active",
        Job.deleted_at.is_(None)
    ).count()
    closed_jobs = db.query(Job).filter(
        Job.status == "closed",
        Job.deleted_at.is_(None)
    ).count()
    
    # Top departments hiring
    department_counts = db.query(
        Job.department,
        func.count(Job.id).label("job_count")
    ).filter(
        Job.deleted_at.is_(None),
        Job.status == "active"
    ).group_by(Job.department).order_by(func.count(Job.id).desc()).limit(10).all()
    
    # Top locations
    location_counts = db.query(
        Job.location,
        func.count(Job.id).label("job_count")
    ).filter(
        Job.deleted_at.is_(None),
        Job.status == "active"
    ).group_by(Job.location).order_by(func.count(Job.id).desc()).limit(10).all()
    
    return {
        "last_30_days": {
            "new_jobs": recent_jobs,
            "new_resumes": recent_resumes
        },
        "job_status": {
            "active": active_jobs,
            "closed": closed_jobs
        },
        "top_departments": [
            {"department": dept, "job_count": count}
            for dept, count in department_counts if dept
        ],
        "top_locations": [
            {"location": loc, "job_count": count}
            for loc, count in location_counts if loc
        ]
    }


@router.get("/quality/distribution", summary="Get candidate quality distribution")
def quality_distribution(db: Session = Depends(get_db)):
    """
    Analyze the distribution of candidate quality scores.
    """
    from src.models.candidate import Candidate
    
    candidates = db.query(Candidate).filter(
        Candidate.deleted_at.is_(None),
        Candidate.quality_score.isnot(None)
    ).all()
    
    # Create bins for quality score distribution
    bins = {
        "0.0-0.2": 0,
        "0.2-0.4": 0,
        "0.4-0.6": 0,
        "0.6-0.8": 0,
        "0.8-1.0": 0
    }
    
    for candidate in candidates:
        score = float(candidate.quality_score)
        if score < 0.2:
            bins["0.0-0.2"] += 1
        elif score < 0.4:
            bins["0.2-0.4"] += 1
        elif score < 0.6:
            bins["0.4-0.6"] += 1
        elif score < 0.8:
            bins["0.6-0.8"] += 1
        else:
            bins["0.8-1.0"] += 1
    
    # Calculate average quality
    avg_quality = sum(float(c.quality_score) for c in candidates) / len(candidates) if candidates else 0
    
    return {
        "total_candidates": len(candidates),
        "avg_quality_score": round(avg_quality, 2),
        "distribution": bins
    }


@router.get("/experience/distribution", summary="Get experience level distribution")
def experience_distribution(db: Session = Depends(get_db)):
    """
    Analyze the distribution of candidate experience levels.
    """
    from src.models.candidate import Candidate
    
    candidates = db.query(Candidate).filter(
        Candidate.deleted_at.is_(None),
        Candidate.total_experience.isnot(None)
    ).all()
    
    # Create bins for experience distribution
    bins = {
        "0-2 years": 0,
        "2-5 years": 0,
        "5-10 years": 0,
        "10-15 years": 0,
        "15+ years": 0
    }
    
    for candidate in candidates:
        exp = float(candidate.total_experience)
        if exp < 2:
            bins["0-2 years"] += 1
        elif exp < 5:
            bins["2-5 years"] += 1
        elif exp < 10:
            bins["5-10 years"] += 1
        elif exp < 15:
            bins["10-15 years"] += 1
        else:
            bins["15+ years"] += 1
    
    # Calculate average experience
    avg_exp = sum(float(c.total_experience) for c in candidates) / len(candidates) if candidates else 0
    
    return {
        "total_candidates": len(candidates),
        "avg_experience_years": round(avg_exp, 1),
        "distribution": bins
    }
