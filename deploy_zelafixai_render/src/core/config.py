"""
Módulo Core: Configurações Globais da Aplicação ZelaFix AI
Microsserviço de Inteligência Artificial Generativa e Triagem Urbana
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega o .env do deploy, da raiz ou da pasta Java-Advanced
_dir_deploy = Path(__file__).resolve().parent.parent.parent
load_dotenv(_dir_deploy / ".env")
load_dotenv(_dir_deploy.parent / ".env")
load_dotenv(_dir_deploy.parent.parent / "Java-Advanced" / ".env")

# Metadados e versão
APP_TITLE = "ZelaFix AI — Microsserviço de Inteligência Artificial e Triagem Urbana"
APP_DESCRIPTION = (
    "API de IA Generativa Multimodal (Qwen 3.8 27B via Groq), RAG Normativo Municipal (PMSP), "
    "Integração Oracle FIAP (somente leitura) e Triagem de Zeladoria Urbana para a plataforma CitizenTech ZelaFix."
)
APP_VERSION = "2.0.0"

# Modelo Generativo Multimodal Groq
GROQ_MODEL = os.environ.get("GROQ_MODEL", "qwen/qwen3.8-27b").strip()
GROQ_BASE_URL = os.environ.get("GROQ_BASE_URL", "https://api.groq.com").strip()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "").strip()
GROQ_TIMEOUT_SECONDS = float(os.environ.get("GROQ_TIMEOUT_SECONDS", "15.0"))

# Provedor padrão e fallback de contingência
AI_PROVIDER = "groq"
FALLBACK_PROVIDER = "local_heuristic"

# Banco de Dados Oracle FIAP (somente leitura via variáveis de ambiente)
ORACLE_USER = os.environ.get("ORACLE_USER", "").strip()
ORACLE_PASSWORD = os.environ.get("ORACLE_PASSWORD", "").strip()
ORACLE_URL = os.environ.get("ORACLE_URL", "jdbc:oracle:thin:@//oracle.fiap.com.br:1521/orcl").strip()
ORACLE_DSN = os.environ.get("ORACLE_DSN", "oracle.fiap.com.br:1521/orcl").strip()

# Similaridade de cosseno mínima para um trecho da base ser usado como fundamento (RAG)
RAG_MIN_SCORE = 0.18

# Portas de Execução
PORT = int(os.environ.get("PORT", 8000))

# Configuração de CORS para comunicação fluida com Mobile (React Native / Expo) e Web
CORS_ORIGINS = ["*"]
CORS_CREDENTIALS = False
CORS_METHODS = ["*"]
CORS_HEADERS = ["*"]
