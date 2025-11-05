from sqlalchemy import Column, Integer, Float, String, DateTime, JSON, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from src.models.base import Base
import datetime

class Match(Base):
    __tablename__ = "matches"
    __table_args__ = (
        UniqueConstraint('resume_id', 'job_id', name='unique_resume_job_match'),
        Index('idx_job_score', 'job_id', 'similarity_score'),
    )

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)
    similarity_score = Column(Float, nullable=True)
    match_details_json = Column(JSON, nullable=True)
    status = Column(String, default="new")
    recruiter_notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    resume = relationship("Resume", back_populates="matches")
    job = relationship("Job", back_populates="matches")
    interviews = relationship("Interview", back_populates="match")
    status_history = relationship("CandidateStatusHistory", back_populates="match")
