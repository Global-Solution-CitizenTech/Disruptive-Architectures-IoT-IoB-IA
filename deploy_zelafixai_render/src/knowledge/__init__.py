"""
Base de Conhecimento Consolidada: ZelaFix AI — RAG Normativo Municipal
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)
"""
from typing import List, Dict, Any

from src.knowledge.pavimentacao import CHUNKS_PAVIMENTACAO
from src.knowledge.drenagem_bueiros import CHUNKS_DRENAGEM
from src.knowledge.iluminacao_publica import CHUNKS_ILUMINACAO
from src.knowledge.limpeza_urbana_residuos import CHUNKS_LIMPEZA
from src.knowledge.manejo_arboreo import CHUNKS_MANEJO_ARBOREO
from src.knowledge.sinalizacao_transito import CHUNKS_SINALIZACAO
from src.knowledge.saneamento_sabesp import CHUNKS_SANEAMENTO
from src.knowledge.direitos_cidadao_faq import CHUNKS_DIREITOS_CIDADAO

# Catálogo consolidado de chunks oficiais da base RAG do ZelaFix
BASE_CHUNKS_RAG: List[Dict[str, Any]] = (
    CHUNKS_PAVIMENTACAO
    + CHUNKS_DRENAGEM
    + CHUNKS_ILUMINACAO
    + CHUNKS_LIMPEZA
    + CHUNKS_MANEJO_ARBOREO
    + CHUNKS_SINALIZACAO
    + CHUNKS_SANEAMENTO
    + CHUNKS_DIREITOS_CIDADAO
)

# Validação defensiva de unicidade de IDs e presença de campos essenciais
_ids_vistos = set()
for c in BASE_CHUNKS_RAG:
    cid = c["id"]
    if cid in _ids_vistos:
        raise ValueError(f"ID duplicado detectado na base de conhecimento: {cid}")
    _ids_vistos.add(cid)
    assert "source" in c and "category" in c and "title" in c and "content" in c, f"Chunk {cid} incompleto"

__all__ = [
    "BASE_CHUNKS_RAG",
    "CHUNKS_PAVIMENTACAO",
    "CHUNKS_DRENAGEM",
    "CHUNKS_ILUMINACAO",
    "CHUNKS_LIMPEZA",
    "CHUNKS_MANEJO_ARBOREO",
    "CHUNKS_SINALIZACAO",
    "CHUNKS_SANEAMENTO",
    "CHUNKS_DIREITOS_CIDADAO",
]
