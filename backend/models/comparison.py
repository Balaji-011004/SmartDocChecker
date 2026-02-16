"""
ComparisonSession SQLAlchemy ORM model.

Tracks multi-document comparison jobs: which documents are being compared,
status, timestamps, and the user who initiated the comparison.
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from db.base import Base


class ComparisonSession(Base):
    __tablename__ = "comparison_sessions"

    id = Column(String, primary_key=True)  # UUID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, nullable=False, default="pending")  # pending | processing | completed | failed
    processing_stage = Column(String, nullable=True)  # Current pipeline stage
    progress_percent = Column(Integer, nullable=True, default=0)  # 0-100
    document_ids = Column(Text, nullable=False)  # JSON-encoded list of document IDs
    total_cross_contradictions = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(String, nullable=True)

    # Relationships
    cross_contradictions = relationship("CrossContradiction", back_populates="comparison", cascade="all, delete-orphan")
