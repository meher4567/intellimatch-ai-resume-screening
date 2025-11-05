from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from src.core.dependencies import get_db
from src.models.candidate import Candidate
from src.models.resume import Resume
from src.schemas.common import CandidateResponse
from datetime import datetime

router = APIRouter(prefix="/candidates", tags=["Candidates"])


@router.get("/", summary="List all candidates")
def list_candidates(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all candidates with optional search"""
    query = db.query(Candidate).filter(Candidate.deleted_at.is_(None))
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Candidate.name.ilike(search_filter)) |
            (Candidate.email.ilike(search_filter)) |
            (Candidate.skills.ilike(search_filter))
        )
    
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
