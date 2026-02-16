"""
CrossContradiction SQLAlchemy ORM model.

Represents a contradiction found between clauses from different documents
during a multi-document comparison session.
"""
from sqlalchemy import Column, String, Float, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship

from db.base import Base


class CrossContradiction(Base):
    __tablename__ = "cross_contradictions"

    id = Column(String, primary_key=True)  # UUID
    comparison_id = Column(String, ForeignKey("comparison_sessions.id"), nullable=False)

    # Source clause from document A
    clause_a_id = Column(String, ForeignKey("clauses.id", ondelete="SET NULL"), nullable=True)
    document_a_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)

    # Source clause from document B
    clause_b_id = Column(String, ForeignKey("clauses.id", ondelete="SET NULL"), nullable=True)
    document_b_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)

    type = Column(String, nullable=False)       # "semantic", "numeric", "modal", "authority"
    severity = Column(String, nullable=False)    # "high", "medium", "low"
    description = Column(Text, nullable=True)
    confidence = Column(Float, nullable=False)

    # Relationships
    comparison = relationship("ComparisonSession", back_populates="cross_contradictions")
    document_a = relationship("Document", foreign_keys=[document_a_id])
    document_b = relationship("Document", foreign_keys=[document_b_id])
