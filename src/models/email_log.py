from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from src.models.base import Base
import datetime

class EmailLog(Base):
    __tablename__ = "email_logs"

    id = Column(Integer, primary_key=True, index=True)
    recipient_email = Column(String, nullable=False)
    template_id = Column(Integer, ForeignKey("email_templates.id"), nullable=True)
    sent_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="sent")
