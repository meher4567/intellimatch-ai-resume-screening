from sqlalchemy import Column, Integer, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from src.models.base import Base
import datetime

class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False, index=True)
    scheduled_date = Column(DateTime, nullable=True)
    interviewer_id = Column(Integer, nullable=True)
    status = Column(String, default="scheduled")
    meeting_link = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    
    # Relationships
    match = relationship("Match", back_populates="interviews")
