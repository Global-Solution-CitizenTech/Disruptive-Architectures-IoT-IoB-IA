"""
Módulo de Configuração Central do ZelaFix IA & IoT
FIAP Global Solution 2026/2 - Disruptive Architectures: IoT, IoB & Generative IA
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis de ambiente a partir de .env se existir
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Identificação da Solução
PROJECT_NAME = "ZelaFix - Zeladoria Urbana Inteligente (IoT, IoB & GenAI)"
PROJECT_VERSION = "2.0.0"
ODS_TARGET = "ODS 11 — Cidades e Comunidades Sustentáveis"

# Configurações do Servidor
APP_ENV = os.getenv("APP_ENV", "development")
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8000"))
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")

# Provedor de IA Generativa
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.2"))
MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", "1024"))

# Limiares de IoT & IoB
IOT_ANOMALY_THRESHOLD_G = float(os.getenv("IOT_ANOMALY_THRESHOLD_G", "2.5"))
IOB_MIN_COMMUNITY_SUPPORTS_URGENT = int(os.getenv("IOB_MIN_COMMUNITY_SUPPORTS_URGENT", "15"))
IOB_MIN_COMMUNITY_SUPPORTS_CRITICAL = int(os.getenv("IOB_MIN_COMMUNITY_SUPPORTS_CRITICAL", "25"))

# Parâmetros de RAG
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "3"))
RAG_SIMILARITY_THRESHOLD = float(os.getenv("RAG_SIMILARITY_THRESHOLD", "0.15"))
KNOWLEDGE_BASE_DIR = BASE_DIR / "data" / "knowledge_base"
DATASET_DIR = BASE_DIR / "data" / "dataset_urban"
IOT_SAMPLES_DIR = BASE_DIR / "data" / "iot_samples"

# Categorias Oficiais do ZelaFix (Alinhadas ao ZelaFix Mobile e Backend Java)
CATEGORIAS_OFICIAIS = [
    "Buraco na Rua",
    "Bueiro Entupido",
    "Iluminação Pública",
    "Entulho e Descarte Irregular",
    "Poda de Árvore",
    "Sinalização e Trânsito",
    "Vazamento de Água",
    "Outros"
]

SEVERIDADES_OFICIAIS = ["Baixa", "Média", "Alta", "Crítica"]

ORGAOS_COMPETENTES = {
    "Buraco na Rua": "Subprefeitura — Equipe de Pavimentação e Tapa-Buraco",
    "Bueiro Entupido": "Subprefeitura — Drenagem Urbana e Hidrojateamento",
    "Iluminação Pública": "Central Ilumina SP — Manutenção de Rede LED",
    "Entulho e Descarte Irregular": "Subprefeitura — Limpeza Pública e Fiscalização Ambiental",
    "Poda de Árvore": "Defesa Civil & Equipe de Manejo Arbóreo",
    "Sinalização e Trânsito": "CET — Engenharia de Tráfego e Sinalização",
    "Vazamento de Água": "Concessionária de Saneamento (Sabesp) & Fiscalização Municipal",
    "Outros": "Central de Zeladoria Municipal 156"
}

