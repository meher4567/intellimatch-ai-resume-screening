from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from src.models.base import Base
import datetime

class CandidateStatusHistory(Base):
    __tablename__ = "candidate_status_history"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False, index=True)
    status = Column(String, nullable=False)
    changed_by = Column(String, nullable=True)
    changed_at = Column(DateTime, default=datetime.datetime.utcnow)
    notes = Column(String, nullable=True)
    
    # Relationships
    match = relationship("Match", back_populates="status_history")
