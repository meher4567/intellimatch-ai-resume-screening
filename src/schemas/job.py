from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Job schemas
class JobCreate(BaseModel):
    title: str
    description: str
    company: Optional[str] = None
    location: Optional[str] = None
    priority: Optional[str] = "normal"
    requirements_json: Optional[dict] = None
    custom_weights_json: Optional[dict] = None
    screening_questions_json: Optional[dict] = None

class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    requirements_json: Optional[dict] = None
    custom_weights_json: Optional[dict] = None
    screening_questions_json: Optional[dict] = None

class JobResponse(BaseModel):
    id: int
    title: str
    description: str
    company: Optional[str]
    location: Optional[str]
    priority: str
    status: str
    posted_date: datetime
    
    class Config:
        from_attributes = True
