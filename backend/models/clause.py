"""
Clause SQLAlchemy ORM model.

Represents an atomic clause extracted from a document.
"""
from sqlalchemy import Column, String, Integer, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import TSVECTOR, JSONB
from pgvector.sqlalchemy import Vector

from db.base import Base


class Clause(Base):
    __tablename__ = "clauses"
    
    id = Column(String, primary_key=True)  # UUID
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    text = Column(Text, nullable=False)
    section = Column(String, nullable=True)  # section heading
    position = Column(Integer, nullable=False)  # order in document (0-indexed)
    
    # Full-text search (PostgreSQL specific)
    search_vector = Column(TSVECTOR, nullable=True)
    
    # Semantic embeddings (pgvector, 384 dimensions for all-MiniLM-L6-v2)
    # Note: Requires CREATE EXTENSION vector; in PostgreSQL
    embedding = Column(Vector(384), nullable=True)
    
    # Named entities extracted via spaCy NER (cached per clause)
    # Format: {"PERSON": ["John"], "ORG": ["Acme"], "DATE": ["Jan 2024"], ...}
    entities = Column(JSONB, nullable=True, default=None)
    
    # Relationships
    document = relationship("Document", back_populates="clauses")
    
    # Indexes
    __table_args__ = (
        Index('ix_clauses_document_id', 'document_id'),
        Index('ix_clauses_search_vector', 'search_vector', postgresql_using='gin'),
    )
