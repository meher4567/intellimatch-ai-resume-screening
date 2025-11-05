from sqlalchemy import Column, Integer, String, Text, DateTime
from src.models.base import Base
import datetime

class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String, nullable=False)  # candidate, match, interview
    entity_id = Column(Integer, nullable=False)
    note_text = Column(Text, nullable=False)
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
