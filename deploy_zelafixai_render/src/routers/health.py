"""
Router de Health Check e Status da Aplicação — ZelaFix AI
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)
"""
from typing import Dict, Any
from fastapi import APIRouter
from src.core.config import (
    AI_PROVIDER,
    AI_MODEL,
    AI_EMBEDDING_MODEL,
    APP_TITLE,
    APP_VERSION,
)

health_router = APIRouter(tags=["Health"])


@health_router.get("/")
@health_router.get("/health")
def health_check() -> Dict[str, Any]:
    """Retorna o status operacional do microsserviço e modelos ativos no Azure AI Foundry."""
    return {
        "status": "healthy",
        "service": APP_TITLE,
        "provider": AI_PROVIDER,
        "model": AI_MODEL,
        "embedding_model": AI_EMBEDDING_MODEL,
        "database_oracle": "Oracle Thin Client (FIAP — somente leitura)",
        "framework": "FastAPI + Azure AI Foundry + ChromaDB",
        "version": APP_VERSION,
    }


@health_router.get("/health/ready")
def health_ready() -> Dict[str, Any]:
    """Verifica a prontidão do índice vetorial RAG e serviços locais."""
    from src.database.vector_store import get_vector_store
    vs = get_vector_store()
    return {
        "status": "ready",
        "vector_store": "online" if vs.is_ready else "fallback_mode",
        "indexed_chunks": vs.count,
    }
