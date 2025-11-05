from sqlalchemy import Column, Integer, String, JSON, DateTime
from src.models.base import Base
import datetime

class SavedFilter(Base):
    __tablename__ = "saved_filters"

    id = Column(Integer, primary_key=True, index=True)
    manager_id = Column(Integer, nullable=True)
    filter_json = Column(JSON, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
