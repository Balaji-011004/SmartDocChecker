"""
Pydantic schemas for analysis results / contradictions.
"""
from typing import List, Any
from pydantic import BaseModel


class ContradictionOut(BaseModel):
    id: str
    type: str
    description: str
    confidence: float
    document_id: str

    class Config:
        from_attributes = True


class AnalysisPairResult(BaseModel):
    doc_pair: List[int]
    contradiction_score: float
    similarity_score: float
    entities_doc1: Any
    entities_doc2: Any


class AnalysisResponse(BaseModel):
    contradictions: List[AnalysisPairResult]
