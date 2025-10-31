from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class MatchCreate(BaseModel):
    resume_id: int = Field(..., description="ID of the resume")
    job_id: int = Field(..., description="ID of the job")
    score: Optional[float] = Field(None, ge=0, le=100, description="Match score percentage")


class MatchUpdate(BaseModel):
    score: Optional[float] = Field(None, ge=0, le=100)
    status: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None


class MatchResponse(BaseModel):
    id: int
    resume_id: int
    job_id: int
    score: Optional[float]
    status: str
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
