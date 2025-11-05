from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.orm import relationship
from src.models.base import Base
import datetime

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    requirements_json = Column(JSON, nullable=True)
    company = Column(String, nullable=True)
    location = Column(String, nullable=True)
    priority = Column(String, default="normal")  # urgent, high, normal, low
    posted_date = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    status = Column(String, default="open")
    custom_weights_json = Column(JSON, nullable=True)
    screening_questions_json = Column(JSON, nullable=True)
    deleted_at = Column(DateTime, nullable=True)  # soft delete
    
    # Relationships
    matches = relationship("Match", back_populates="job")
    knockout_criteria = relationship("KnockoutCriteria", back_populates="job")
