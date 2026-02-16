"""
Contradiction SQLAlchemy ORM model.
"""
from sqlalchemy import Column, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from db.base import Base


class Contradiction(Base):
    __tablename__ = "contradictions"

    id = Column(String, primary_key=True)
    clause_a_id = Column(String, ForeignKey("clauses.id", ondelete="SET NULL"), nullable=True)
    clause_b_id = Column(String, ForeignKey("clauses.id", ondelete="SET NULL"), nullable=True)
    type = Column(String)  # "numeric", "modal", "authority", "semantic"
    severity = Column(String)  # "high", "medium", "low"
    description = Column(String)
    confidence = Column(Float)
    document_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"))

    document = relationship("Document", back_populates="contradictions")

