"""
DTOs para o módulo de Recuperação Aumentada por Geração (RAG)
"""

from typing import List, Optional
from pydantic import BaseModel, Field

class RagQueryRequest(BaseModel):
    query: str = Field(..., example="Buraco profundo com risco de acidente de moto na avenida")
    categoria: Optional[str] = Field(None, example="Buraco na Rua")
    top_k: int = Field(3, ge=1, le=10)

class RagDocumentChunk(BaseModel):
    chunk_id: str
    source_file: str
    title: str
    content: str
    law_article: Optional[str] = None
    sla_hours: Optional[int] = None
    competent_agency: Optional[str] = None
    similarity_score: float

class RagQueryResponse(BaseModel):
    query: str
    total_chunks_found: int
    chunks: List[RagDocumentChunk]
    context_text: str

