from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from src.models.base import Base
import datetime

class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    category = Column(String, nullable=True)
    normalized_name = Column(String, nullable=True)
    aliases = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    candidate_skills = relationship("CandidateSkill", back_populates="skill")
