from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from src.models.base import Base

class CandidateTag(Base):
    __tablename__ = "candidate_tags"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False, index=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), nullable=False, index=True)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="tags")
    tag = relationship("Tag", back_populates="candidate_tags")
