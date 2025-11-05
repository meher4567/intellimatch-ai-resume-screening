from sqlalchemy import Column, Integer, String, Text
from src.models.base import Base

class EmailTemplate(Base):
    __tablename__ = "email_templates"

    id = Column(Integer, primary_key=True, index=True)
    template_name = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    variables = Column(String, nullable=True)
