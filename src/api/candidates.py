from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from src.core.dependencies import get_db
from src.models.candidate import Candidate
from src.models.resume import Resume
from src.schemas.common import CandidateResponse
from datetime import datetime

router = APIRouter(prefix="/candidates", tags=["Candidates"])


@router.get(
    "/",
    summary="List all candidates with advanced filtering",
    responses={
        200: {
            "description": "Paginated list of candidates",
            "content": {
                "application/json": {
                    "example": {
                        "total": 127,
                        "skip": 0,
                        "limit": 50,
                        "candidates": [
                            {
                                "id": 7,
                                "name": "John Doe",
                                "email": "john@example.com",
                                "total_experience": 5.5,
                                "quality_score": 0.85,
                                "status": "active",
                                "skills": "Python, FastAPI, PostgreSQL, Docker"
                            }
                        ]
                    }
                }
            }
        }
    }
)
def list_candidates(
    skip: int = Query(0, ge=0, description="Records to skip for pagination"),
    limit: int = Query(50, ge=1, le=200, description="Maximum records to return"),
    search: Optional[str] = Query(None, description="Search in name, email, and skills"),
    min_experience: Optional[float] = Query(None, description="Minimum years of experience"),
    max_experience: Optional[float] = Query(None, description="Maximum years of experience"),
    min_quality: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum quality score (0.0-1.0)"),
    status: Optional[str] = Query(None, description="Filter by status: active, inactive, or hired"),
    db: Session = Depends(get_db)
):
    """
    List all candidates with powerful filtering and search capabilities.
    
    **Filtering Options:**
    - `search`: Free-text search across name, email, and skills
    - `min_experience` & `max_experience`: Filter by years of experience
    - `min_quality`: Filter by resume quality score (0.0 to 1.0)
    - `status`: active, inactive, or hired
    
    **Example Queries:**
    - Senior developers: `?min_experience=5&search=python`
    - High-quality candidates: `?min_quality=0.8&status=active`
    - Mid-level range: `?min_experience=3&max_experience=7`
    
    Returns paginated results with total count.
    """
    query = db.query(Candidate).filter(Candidate.deleted_at.is_(None))
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Candidate.name.ilike(search_filter)) |
            (Candidate.email.ilike(search_filter)) |
            (Candidate.skills.ilike(search_filter))
        )
    
    if min_experience is not None:
        query = query.filter(Candidate.total_experience >= min_experience)
    
    if max_experience is not None:
        query = query.filter(Candidate.total_experience <= max_experience)
    
    if min_quality is not None:
        query = query.filter(Candidate.quality_score >= min_quality)
    
    if status:
        query = query.filter(Candidate.status == status)
    
    total = query.count()
    candidates = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "candidates": candidates
    }


@router.get("/{candidate_id}", summary="Get candidate by ID")
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """Get detailed candidate information"""
    candidate = db.query(Candidate).filter(
        Candidate.id == candidate_id,
        Candidate.deleted_at.is_(None)
    ).first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Get candidate's resumes
    resumes = db.query(Resume).filter(
        Resume.candidate_id == candidate_id,
        Resume.deleted_at.is_(None)
    ).all()
    
    return {
        "candidate": candidate,
        "resumes": resumes,
        "resume_count": len(resumes)
    }


@router.delete("/{candidate_id}", summary="Delete candidate")
def delete_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """Soft delete a candidate"""
    candidate = db.query(Candidate).filter(
        Candidate.id == candidate_id,
        Candidate.deleted_at.is_(None)
    ).first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    candidate.deleted_at = datetime.utcnow()
    db.commit()
    
    return {"status": "success", "message": "Candidate deleted"}


@router.get("/{candidate_id}/matches", summary="Get candidate matches")
def get_candidate_matches(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    """Get all job matches for a candidate"""
    from src.models.match import Match
    
    matches = db.query(Match).filter(
        Match.candidate_id == candidate_id
    ).order_by(Match.similarity_score.desc()).all()
    
    return {
        "candidate_id": candidate_id,
        "total_matches": len(matches),
        "matches": matches
    }


@router.get("/search/skills", summary="Search candidates by skills")
def search_candidates_by_skills(
    skills: str = Query(..., description="Comma-separated list of skills to search for"),
    min_match: int = Query(1, ge=1, description="Minimum number of skills that must match"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Search candidates who have specific skills.
    Returns candidates sorted by number of matching skills.
    """
    skill_list = [s.strip().lower() for s in skills.split(",")]
    
    candidates = db.query(Candidate).filter(Candidate.deleted_at.is_(None)).all()
    
    # Score each candidate by matching skills
    results = []
    for candidate in candidates:
        if not candidate.skills:
            continue
        
        candidate_skills = [s.strip().lower() for s in candidate.skills.split(",")]
        matching_skills = [s for s in skill_list if s in candidate_skills]
        
        if len(matching_skills) >= min_match:
            results.append({
                "candidate": candidate,
                "matching_skills": matching_skills,
                "match_count": len(matching_skills)
            })
    
    # Sort by match count descending
    results.sort(key=lambda x: x["match_count"], reverse=True)
    
    return {
        "query_skills": skill_list,
        "min_match": min_match,
        "total_results": len(results),
        "results": results[:limit]
    }


@router.put("/{candidate_id}/status", summary="Update candidate status")
def update_candidate_status(
    candidate_id: int,
    status: str = Query(..., description="New status (active, inactive, hired)"),
    db: Session = Depends(get_db)
):
    """
    Update candidate status (active, inactive, hired).
    """
    candidate = db.query(Candidate).filter(
        Candidate.id == candidate_id,
        Candidate.deleted_at.is_(None)
    ).first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    if status not in ["active", "inactive", "hired"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid status. Must be: active, inactive, or hired"
        )
    
    candidate.status = status
    candidate.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(candidate)
    
    return candidate


@router.get("/stats/summary", summary="Get candidate statistics")
def get_candidate_stats(db: Session = Depends(get_db)):
    """
    Get summary statistics about candidates.
    """
    total_candidates = db.query(Candidate).filter(Candidate.deleted_at.is_(None)).count()
    active_candidates = db.query(Candidate).filter(
        Candidate.deleted_at.is_(None),
        Candidate.status == "active"
    ).count()
    hired_candidates = db.query(Candidate).filter(
        Candidate.deleted_at.is_(None),
        Candidate.status == "hired"
    ).count()
    
    # Average experience
    from sqlalchemy import func
    avg_experience = db.query(func.avg(Candidate.total_experience)).filter(
        Candidate.deleted_at.is_(None),
        Candidate.total_experience.isnot(None)
    ).scalar() or 0
    
    # Average quality score
    avg_quality = db.query(func.avg(Candidate.quality_score)).filter(
        Candidate.deleted_at.is_(None),
        Candidate.quality_score.isnot(None)
    ).scalar() or 0
    
    return {
        "total": total_candidates,
        "active": active_candidates,
        "hired": hired_candidates,
        "inactive": total_candidates - active_candidates - hired_candidates,
        "avg_experience_years": round(float(avg_experience), 1),
        "avg_quality_score": round(float(avg_quality), 2)
    }
