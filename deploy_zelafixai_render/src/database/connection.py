"""
Módulo de Conexão e Inicialização do Banco de Dados SQLite — ZelaFix AI
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)
"""
import os
import sqlite3
from typing import Generator
from contextlib import contextmanager

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "zelafixai.db")

def ensure_data_directory() -> None:
    """Garante que a pasta 'data' exista."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)

def init_db() -> None:
    """
    Inicializa o esquema do banco SQLite com tabelas e índices.
    Configura WAL mode (Write-Ahead Logging) para concorrência de alta performance.
    """
    ensure_data_directory()
    with sqlite3.connect(DB_PATH, timeout=15.0) as conn:
        cursor = conn.cursor()
        
        # Otimizações de concorrência e integridade SQLite
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA synchronous=NORMAL;")
        cursor.execute("PRAGMA busy_timeout=5000;")
        
        # 1. Tabela de Mensagens do Chat Conversacional ZelaBot
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mensagens_chat (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                chamado_id INTEGER,
                sender TEXT NOT NULL,
                text TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_mensagens_session ON mensagens_chat (session_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_mensagens_chamado ON mensagens_chat (chamado_id);")

        # 2. Tabela de Auditoria de Triagens Técnicas de Zeladoria Urbana
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auditoria_triagens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                chamado_id INTEGER,
                bairro TEXT,
                pergunta TEXT NOT NULL,
                resposta TEXT NOT NULL,
                categoria TEXT NOT NULL,
                urgencia TEXT NOT NULL,
                orgao_responsavel TEXT,
                sla_horas INTEGER,
                origem_resposta TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_auditoria_session ON auditoria_triagens (session_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_auditoria_chamado ON auditoria_triagens (chamado_id);")

        conn.commit()

@contextmanager
def get_db_connection() -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager para conexões seguras com SQLite.
    Aplica WAL mode e timeout defensivo contra locks de concorrência.
    """
    ensure_data_directory()
    conn = sqlite3.connect(DB_PATH, timeout=15.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout=5000;")
    try:
        yield conn
    finally:
        conn.close()
