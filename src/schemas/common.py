from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class ResumeResponse(BaseModel):
    id: int
    file_path: str
    file_type: str
    source: Optional[str]
    upload_date: datetime
    status: str
    skills_with_proficiency: Optional[List[Dict[str, Any]]] = Field(None, description="Skills with proficiency levels")
    proficiency_summary: Optional[Dict[str, int]] = Field(None, description="Count by proficiency level")
    career_timeline: Optional[Dict[str, Any]] = Field(None, description="Career progression analysis")
    
    class Config:
        from_attributes = True


class CandidateResponse(BaseModel):
    id: int
    name: str
    email: Optional[str]
    phone: Optional[str]
    skills: Optional[str]
    experience_years: Optional[int]
    current_title: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class PaginationResponse(BaseModel):
    total: int = Field(..., description="Total number of items")
    skip: int = Field(..., description="Number of items skipped")
    limit: int = Field(..., description="Number of items per page")
    has_more: bool = Field(..., description="Whether there are more items")
