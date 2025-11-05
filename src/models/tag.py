from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from src.models.base import Base
import datetime

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    candidate_tags = relationship("CandidateTag", back_populates="tag")
