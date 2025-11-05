from sqlalchemy import Column, Integer, String, DateTime, JSON
from src.models.base import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="candidate")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    preferences_json = Column(JSON, nullable=True)
