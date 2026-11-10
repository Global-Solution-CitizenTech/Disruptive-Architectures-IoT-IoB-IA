"""
Router de Health Check e Status da Aplicação — ZelaFix AI
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)
"""
from typing import Dict, Any
from fastapi import APIRouter
from src.core.config import AI_PROVIDER, GROQ_MODEL, GEMINI_MODEL, APP_TITLE, APP_VERSION

health_router = APIRouter(tags=["Health"])

@health_router.get("/")
@health_router.get("/health")
def health_check() -> Dict[str, Any]:
    """
    Retorna o status operacional do microsserviço de IA e versões dos motores.
    """
    return {
        "status": "healthy",
        "service": APP_TITLE,
        "provider": AI_PROVIDER,
        "model": f"{GROQ_MODEL if AI_PROVIDER == 'groq' else GEMINI_MODEL} / Semantic Knowledge Engine",
        "framework": "FastAPI + Clean Mobile Pipeline",
        "version": APP_VERSION
    }

@health_router.get("/health/ready")
def health_ready() -> Dict[str, Any]:
    """
    Verifica a prontidão da base RAG e dos serviços locais.
    """
    from src.database.vector_store import get_vector_store
    vs = get_vector_store()
    return {
        "status": "ready",
        "vector_store": "online" if vs.is_ready else "fallback_mode",
        "indexed_chunks": vs.count
    }
