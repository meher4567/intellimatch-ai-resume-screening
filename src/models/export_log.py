from sqlalchemy import Column, Integer, String, DateTime
from src.models.base import Base
import datetime

class ExportLog(Base):
    __tablename__ = "export_logs"

    id = Column(Integer, primary_key=True, index=True)
    export_type = Column(String, nullable=False)  # excel, pdf
    job_id = Column(Integer, nullable=True)
    performed_by = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    file_path = Column(String, nullable=True)
