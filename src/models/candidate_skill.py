from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from src.models.base import Base

class CandidateSkill(Base):
    __tablename__ = "candidate_skills"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False, index=True)
    proficiency_level = Column(String, nullable=True)
    years_experience = Column(Float, nullable=True)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="skills")
    skill = relationship("Skill", back_populates="candidate_skills")
