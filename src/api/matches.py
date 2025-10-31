from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.core.dependencies import get_db
from src.models.match import Match
from src.models.job import Job
from src.models.resume import Resume
from src.schemas.match import MatchCreate, MatchUpdate, MatchResponse
from typing import List
import datetime

router = APIRouter(prefix="/matches", tags=["Matches"])

@router.post("/", response_model=MatchResponse, summary="Create a match between a resume and a job")
def create_match(match_data: MatchCreate, db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == match_data.resume_id, Resume.deleted_at.is_(None)).first()
    job = db.query(Job).filter(Job.id == match_data.job_id, Job.deleted_at.is_(None)).first()
    if not resume or not job:
        raise HTTPException(status_code=404, detail="Resume or Job not found")
    
    # Calculate match score using the matching engine if not provided
    score = match_data.score
    if score is None:
        from src.services.matching_engine import MatchingEngine
        from src.services.skill_extractor import SkillExtractor
        
        try:
            matcher = MatchingEngine()
            skill_extractor = SkillExtractor()
            
            # Extract skills from resume and job
            resume_text = resume.raw_text or ""
            job_text = job.description or ""
            
            resume_skills = skill_extractor.extract_skills(resume_text)
            resume_skill_names = [s['name'] for s in resume_skills]
            
            job_skills = skill_extractor.extract_skills(job_text)
            job_skill_names = [s['name'] for s in job_skills]
            
            # Compute match score
            match_result = matcher.match_resume_to_job(
                resume_text=resume_text,
                job_description=job_text,
                resume_skills=resume_skill_names,
                job_requirements=job_skill_names
            )
            
            score = match_result['overall_score'] * 100  # Convert to percentage
        except Exception as e:
            print(f"Error computing match score: {e}")
            score = 50.0  # Default score if computation fails
    
    match = Match(
        resume_id=match_data.resume_id, 
        job_id=match_data.job_id,
        score=score,
        created_at=datetime.datetime.utcnow()
    )
    db.add(match)
    try:
        db.commit()
        db.refresh(match)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Match already exists for this resume and job")
    return match

@router.get("/", response_model=List[MatchResponse], summary="List all matches")
def list_matches(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: str = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Match)
    if status:
        query = query.filter(Match.status == status)
    matches = query.offset(skip).limit(limit).all()
    return matches

@router.get("/{match_id}", response_model=MatchResponse, summary="Get match details")
def get_match(match_id: int, db: Session = Depends(get_db)):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return match

@router.put("/{match_id}", response_model=MatchResponse, summary="Update a match")
def update_match(match_id: int, update_data: MatchUpdate, db: Session = Depends(get_db)):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(match, key, value)
    
    match.updated_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(match)
    return match

@router.delete("/{match_id}", summary="Delete a match (soft delete)")
def delete_match(match_id: int, db: Session = Depends(get_db)):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    match.status = "deleted"
    match.updated_at = datetime.datetime.utcnow()
    db.commit()
    return {"id": match.id, "deleted": True}

@router.get("/job/{job_id}", response_model=List[MatchResponse], summary="List all matches for a job")
def job_matches(
    job_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    matches = db.query(Match).filter(Match.job_id == job_id).offset(skip).limit(limit).all()
    return matches

@router.get("/resume/{resume_id}", response_model=List[MatchResponse], summary="List all matches for a resume")
def resume_matches(
    resume_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    matches = db.query(Match).filter(Match.resume_id == resume_id).offset(skip).limit(limit).all()
    return matches
