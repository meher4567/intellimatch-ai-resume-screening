from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from src.core.dependencies import get_db
from src.models.interview import Interview
from src.models.match import Match
from src.schemas.interview import InterviewCreate, InterviewUpdate, InterviewResponse
from typing import List
import datetime

router = APIRouter(prefix="/interviews", tags=["Interviews"])

@router.post("/", response_model=InterviewResponse, summary="Schedule a new interview")
def schedule_interview(interview_data: InterviewCreate, db: Session = Depends(get_db)):
    match = db.query(Match).filter(Match.id == interview_data.match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    interview = Interview(
        match_id=interview_data.match_id,
        scheduled_date=interview_data.scheduled_date,
        meeting_link=interview_data.meeting_link,
        notes=interview_data.notes,
        status="scheduled"
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)
    return interview

@router.get("/", response_model=List[InterviewResponse], summary="List all interviews")
def list_interviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: str = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Interview)
    if status:
        query = query.filter(Interview.status == status)
    interviews = query.offset(skip).limit(limit).all()
    return interviews

@router.get("/{interview_id}", response_model=InterviewResponse, summary="Get interview details")
def get_interview(interview_id: int, db: Session = Depends(get_db)):
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    return interview

@router.put("/{interview_id}", response_model=InterviewResponse, summary="Update interview status or details")
def update_interview(interview_id: int, update_data: InterviewUpdate, db: Session = Depends(get_db)):
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(interview, key, value)
    
    interview.updated_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(interview)
    return interview

@router.delete("/{interview_id}", summary="Delete an interview")
def delete_interview(interview_id: int, db: Session = Depends(get_db)):
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    db.delete(interview)
    db.commit()
    return {"id": interview_id, "deleted": True}
