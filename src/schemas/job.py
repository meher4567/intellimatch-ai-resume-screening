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
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Senior Python Engineer",
                    "description": "We're looking for an experienced Python engineer to join our backend team. You'll work on building scalable APIs and microservices using FastAPI and PostgreSQL.",
                    "company": "TechCorp Inc",
                    "location": "Remote",
                    "priority": "high",
                    "requirements_json": {
                        "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
                        "nice_to_have": ["Kubernetes", "AWS", "Redis"],
                        "min_experience": 5,
                        "education": "Bachelor's in Computer Science or equivalent"
                    }
                }
            ]
        }
    }

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
