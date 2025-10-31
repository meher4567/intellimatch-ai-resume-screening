from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class InterviewCreate(BaseModel):
    match_id: int = Field(..., description="ID of the match")
    scheduled_date: datetime = Field(..., description="Interview scheduled date and time")
    meeting_link: Optional[str] = Field(None, max_length=500, description="Virtual meeting link")
    notes: Optional[str] = None


class InterviewUpdate(BaseModel):
    scheduled_date: Optional[datetime] = None
    meeting_link: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None
    feedback: Optional[str] = None


class InterviewResponse(BaseModel):
    id: int
    match_id: int
    scheduled_date: datetime
    meeting_link: Optional[str]
    status: str
    notes: Optional[str]
    feedback: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
