from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from src.models.base import Base
import datetime

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False, index=True)
    extracted_info_json = Column(JSON, nullable=True)
    quality_score = Column(Float, nullable=True)
    experience_level = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)  # soft delete
    
    # Relationships
    resume = relationship("Resume", back_populates="candidate")
    skills = relationship("CandidateSkill", back_populates="candidate")
    tags = relationship("CandidateTag", back_populates="candidate")
