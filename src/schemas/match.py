from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class MatchCreate(BaseModel):
    resume_id: int = Field(..., description="ID of the resume")
    job_id: int = Field(..., description="ID of the job")
    score: Optional[float] = Field(None, ge=0, le=100, description="Match score percentage")
    include_explanation: Optional[bool] = Field(False, description="Generate natural language explanation")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "resume_id": 12,
                    "job_id": 5,
                    "include_explanation": True
                }
            ]
        }
    }


class MatchUpdate(BaseModel):
    score: Optional[float] = Field(None, ge=0, le=100)
    status: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None


class MatchResponse(BaseModel):
    id: int
    resume_id: int
    job_id: int
    similarity_score: Optional[float] = Field(None, alias="score")  # Support both names
    status: str
    recruiter_notes: Optional[str] = Field(None, alias="notes")  # Support both names
    created_at: datetime
    updated_at: Optional[datetime]
    explanation: Optional[Dict[str, Any]] = Field(None, description="Natural language match explanation")

    class Config:
        from_attributes = True
        populate_by_name = True  # Allow using aliases
