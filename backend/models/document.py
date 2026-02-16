"""
Document SQLAlchemy ORM model.
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from db.base import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    file_path = Column(String, nullable=True)       # Supabase Storage path
    status = Column(String, nullable=False, default="pending")
    processing_stage = Column(String, nullable=True)  # Current pipeline stage
    progress_percent = Column(Integer, nullable=True, default=0)  # 0-100
    upload_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    analysis_start_time = Column(DateTime, nullable=True)
    analysis_end_time = Column(DateTime, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    contradictions = relationship("Contradiction", back_populates="document", cascade="all, delete-orphan")
    clauses = relationship("Clause", back_populates="document", cascade="all, delete-orphan")

