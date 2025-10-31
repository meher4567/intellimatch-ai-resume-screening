from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ResumeResponse(BaseModel):
    id: int
    file_path: str
    file_type: str
    source: Optional[str]
    upload_date: datetime
    status: str
    
    class Config:
        from_attributes = True


class PaginationResponse(BaseModel):
    total: int = Field(..., description="Total number of items")
    skip: int = Field(..., description="Number of items skipped")
    limit: int = Field(..., description="Number of items per page")
    has_more: bool = Field(..., description="Whether there are more items")
