from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from src.models.base import Base
import datetime

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    parsed_data_json = Column(JSON, nullable=True)
    source = Column(String, nullable=True)  # upload, email, api, etc.
    upload_date = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    status = Column(String, default="uploaded")
    deleted_at = Column(DateTime, nullable=True)  # soft delete
    
    # Relationships
    candidate = relationship("Candidate", back_populates="resume", uselist=False)
    matches = relationship("Match", back_populates="resume")
