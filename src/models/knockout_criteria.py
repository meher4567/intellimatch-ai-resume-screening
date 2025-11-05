from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from src.models.base import Base

class KnockoutCriteria(Base):
    __tablename__ = "knockout_criteria"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)
    criterion_type = Column(String, nullable=False)
    criterion_value = Column(String, nullable=False)
    is_mandatory = Column(Boolean, default=True)
    
    # Relationships
    job = relationship("Job", back_populates="knockout_criteria")
