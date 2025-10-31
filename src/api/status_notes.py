from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from src.core.dependencies import get_db
from src.models.candidate_status_history import CandidateStatusHistory
from src.models.note import Note
from src.schemas.status_note import StatusCreate, StatusResponse, NoteCreate, NoteResponse
from typing import List
import datetime

router = APIRouter(prefix="/status-notes", tags=["Status & Notes"])

# Candidate status tracking
@router.post("/status", response_model=StatusResponse, summary="Update candidate status")
def update_status(status_data: StatusCreate, db: Session = Depends(get_db)):
    status_entry = CandidateStatusHistory(
        match_id=status_data.match_id,
        status=status_data.status,
        changed_by=status_data.changed_by,
        changed_at=datetime.datetime.utcnow(),
        notes=status_data.notes
    )
    db.add(status_entry)
    db.commit()
    db.refresh(status_entry)
    return status_entry

@router.get("/status/{match_id}", response_model=List[StatusResponse], summary="Get status history for a match")
def get_status_history(
    match_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    history = db.query(CandidateStatusHistory).filter(
        CandidateStatusHistory.match_id == match_id
    ).order_by(CandidateStatusHistory.changed_at.desc()).offset(skip).limit(limit).all()
    return history

# Notes system
@router.post("/note", response_model=NoteResponse, summary="Add a note to an entity")
def add_note(note_data: NoteCreate, db: Session = Depends(get_db)):
    note = Note(
        entity_type=note_data.entity_type,
        entity_id=note_data.entity_id,
        note_text=note_data.note_text,
        created_by=note_data.created_by,
        created_at=datetime.datetime.utcnow()
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note

@router.get("/note/{entity_type}/{entity_id}", response_model=List[NoteResponse], summary="Get notes for an entity")
def get_notes(
    entity_type: str,
    entity_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    notes = db.query(Note).filter(
        Note.entity_type == entity_type,
        Note.entity_id == entity_id
    ).order_by(Note.created_at.desc()).offset(skip).limit(limit).all()
    return notes
