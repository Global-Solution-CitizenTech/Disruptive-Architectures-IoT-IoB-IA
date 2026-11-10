"""
Módulo Core: Configurações Globais da Aplicação ZelaFix AI
Microsserviço de Inteligência Artificial Generativa e Triagem Urbana
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega o .env do deploy e, na ausência dele, o da raiz do repositório
_dir_deploy = Path(__file__).resolve().parent.parent.parent
load_dotenv(_dir_deploy / ".env")
load_dotenv(_dir_deploy.parent / ".env")

# Metadados e versão
APP_TITLE = "ZelaFix AI — Microsserviço de Inteligência Artificial e Triagem Urbana"
APP_DESCRIPTION = "API de IA Generativa, RAG Normativo Municipal (PMSP) e Triagem de Zeladoria Urbana para a plataforma CitizenTech ZelaFix."
APP_VERSION = "1.0.0"

# Modelos fixos por provedor
GROQ_MODEL = "openai/gpt-oss-20b"
GEMINI_MODEL = "gemini-3.5-flash"

# Provedor primário: "groq" (padrão) ou "gemini". O outro atua como fallback automático.
PROVIDERS = ("groq", "gemini")
AI_PROVIDER = os.environ.get("AI_PROVIDER", "").strip().lower()
if AI_PROVIDER not in PROVIDERS:
    AI_PROVIDER = "groq"
FALLBACK_PROVIDER = "gemini" if AI_PROVIDER == "groq" else "groq"

# Similaridade de cosseno mínima para um trecho da base ser usado como fundamento (RAG)
RAG_MIN_SCORE = 0.18

# Credenciais e Portas
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "").strip()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
PORT = int(os.environ.get("PORT", 8000))

# Configuração de CORS para comunicação fluida com Mobile (React Native / Expo) e Web
CORS_ORIGINS = ["*"]
CORS_CREDENTIALS = False
CORS_METHODS = ["*"]
CORS_HEADERS = ["*"]
