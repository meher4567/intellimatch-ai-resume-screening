from sqlalchemy import Column, Integer, String, DateTime, JSON
from src.models.base import Base
import datetime

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    action_type = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)
    entity_id = Column(Integer, nullable=False)
    performed_by = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    details_json = Column(JSON, nullable=True)
