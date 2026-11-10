"""
Ponto de Entrada Principal (FastAPI Application Factory & Bootstrap) — ZelaFix AI
Microsserviço de Inteligência Artificial Generativa, RAG Normativo e Triagem Urbana
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)
"""
import os
import sys
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Assegura que o diretório raiz do deploy esteja no sys.path para resolução do pacote 'src'
DIRETORIO_RAIZ = os.path.dirname(os.path.abspath(__file__))
if DIRETORIO_RAIZ not in sys.path:
    sys.path.insert(0, DIRETORIO_RAIZ)

from src.core.config import (
    APP_TITLE,
    APP_DESCRIPTION,
    APP_VERSION,
    CORS_ORIGINS,
    CORS_CREDENTIALS,
    CORS_METHODS,
    CORS_HEADERS,
    PORT,
)
from src.routers.health import health_router
from src.routers.ai import ai_router
from src.database.connection import init_db
from src.services.knowledge_service import KnowledgeService

def create_app() -> FastAPI:
    """
    Constrói e configura a instância do FastAPI com middlewares e roteadores modulares.
    """
    # 1. Inicializa o banco de dados relacional SQLite (tabelas e índices)
    init_db()

    # 2. Inicializa o banco de dados vetorial ChromaDB (persistência e embeddings em ./data/chroma)
    KnowledgeService.inicializar_indice_rag()

    aplicacao = FastAPI(
        title=APP_TITLE,
        description=APP_DESCRIPTION,
        version=APP_VERSION,
    )

    # Configuração de CORS para comunicação fluida com React Native e Web
    aplicacao.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=CORS_CREDENTIALS,
        allow_methods=CORS_METHODS,
        allow_headers=CORS_HEADERS,
    )

    # Inclusão de rotas modulares
    aplicacao.include_router(health_router)
    aplicacao.include_router(ai_router)

    return aplicacao

app = create_app()

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=PORT, reload=True)
