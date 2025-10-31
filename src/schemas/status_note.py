from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class StatusCreate(BaseModel):
    match_id: int = Field(..., description="ID of the match")
    status: str = Field(..., max_length=50, description="New status")
    changed_by: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None


class StatusResponse(BaseModel):
    id: int
    match_id: int
    status: str
    changed_by: Optional[str]
    changed_at: datetime
    notes: Optional[str]

    class Config:
        from_attributes = True


class NoteCreate(BaseModel):
    entity_type: str = Field(..., max_length=50, description="Type of entity (e.g., 'resume', 'job', 'match')")
    entity_id: int = Field(..., description="ID of the entity")
    note_text: str = Field(..., min_length=1, description="Note content")
    created_by: Optional[str] = Field(None, max_length=255)


class NoteResponse(BaseModel):
    id: int
    entity_type: str
    entity_id: int
    note_text: str
    created_by: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
