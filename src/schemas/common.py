from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class QualityGrade(BaseModel):
    """Resume quality assessment result with dynamic scoring"""
    score: float = Field(..., description="Overall score 0-100")
    grade: str = Field(..., description="Letter grade (A, B+, C, etc.)")
    tier: str = Field(..., description="Quality tier (Excellent, Good, Average, etc.)")
    summary: str = Field(..., description="One-line quality summary")
    strengths: List[str] = Field(default_factory=list, description="Resume strengths")
    improvements: List[str] = Field(default_factory=list, description="Areas to improve")
    missing: List[str] = Field(default_factory=list, description="Critical missing elements")
    ats_score: float = Field(..., description="ATS compatibility score 0-100")
    # Dynamic scoring additions
    breakdown: Optional[Dict[str, float]] = Field(None, description="Score breakdown by category")
    bonuses: Optional[List[str]] = Field(None, description="Bonus points earned")
    penalties: Optional[List[str]] = Field(None, description="Penalties applied")
    job_relevance_score: Optional[float] = Field(None, description="Job match score if job provided")


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
    quality_assessment: Optional[QualityGrade] = Field(None, description="Resume quality grade and feedback")
    
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
