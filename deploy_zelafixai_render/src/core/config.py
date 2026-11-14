"""
Módulo Core: Configurações Globais da Aplicação ZelaFix AI
Microsserviço de Inteligência Artificial Generativa e Triagem Urbana
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega exclusivamente o .env local do microsserviço ou da raiz deste repositório
_dir_deploy = Path(__file__).resolve().parent.parent.parent
load_dotenv(_dir_deploy / ".env")
load_dotenv(_dir_deploy.parent / ".env")

APP_TITLE = "ZelaFix AI — Microsserviço de Inteligência Artificial e Triagem Urbana"
APP_DESCRIPTION = (
    "API de IA Generativa Multimodal, Embeddings Semânticos em Nuvem (Azure AI Foundry), "
    "RAG Normativo Municipal (PMSP), Integração Oracle FIAP (somente leitura) e Triagem Urbana ZelaFix."
)
APP_VERSION = "3.0.0"

# Azure AI Foundry (API OpenAI-compatible v1)
AI_BASE_URL = os.environ.get("AI_BASE_URL", "").strip()
AI_API_KEY = os.environ.get("AI_API_KEY", "").strip()
AI_MODEL = os.environ.get("AI_MODEL", "phi-4-multimodal").strip()
AI_EMBEDDING_MODEL = os.environ.get("AI_EMBEDDING_MODEL", "embed-v-4-0").strip()
AI_EMBEDDING_DIMENSIONS = int(os.environ.get("AI_EMBEDDING_DIMENSIONS", "1536"))
AI_TIMEOUT_SECONDS = float(os.environ.get("AI_TIMEOUT_SECONDS", "25.0"))
AI_PROVIDER = "azure-ai-foundry"

# Oracle FIAP (somente leitura SELECT via variáveis de ambiente)
ORACLE_USER = os.environ.get("ORACLE_USER", "").strip()
ORACLE_PASSWORD = os.environ.get("ORACLE_PASSWORD", "").strip()
ORACLE_URL = os.environ.get("ORACLE_URL", "jdbc:oracle:thin:@//oracle.fiap.com.br:1521/orcl").strip()
ORACLE_DSN = os.environ.get("ORACLE_DSN", "oracle.fiap.com.br:1521/orcl").strip()

# Corte mínimo de similaridade de cosseno para fundamentação RAG
RAG_MIN_SCORE = float(os.environ.get("RAG_MIN_SCORE", "0.28"))

# Execução & CORS (React Native / Expo e Web)
PORT = int(os.environ.get("PORT", 8000))
CORS_ORIGINS = ["*"]
CORS_CREDENTIALS = False
CORS_METHODS = ["*"]
CORS_HEADERS = ["*"]
