"""
Pydantic schemas for document-related request / response models.
"""
from typing import List, Optional
from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: str
    name: str
    status: str
    upload_date: str
    processing_stage: Optional[str] = None
    progress_percent: Optional[int] = 0
    contradictions: List[str] = []

    class Config:
        from_attributes = True


class DocumentUploadResponse(BaseModel):
    id: str
    name: str
    status: str
    upload_date: str
    contradictions: List[str] = []
