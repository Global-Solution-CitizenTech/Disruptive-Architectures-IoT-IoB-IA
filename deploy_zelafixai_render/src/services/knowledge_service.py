"""
Serviço de Conhecimento RAG com Embeddings Semânticos em Nuvem (Azure AI Foundry) — ZelaFix AI
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)
"""
import logging
import threading
from typing import Optional, Dict, Any, List

import src.core.config as cfg
from src.knowledge import BASE_CHUNKS_RAG
from src.database.vector_store import get_vector_store
from src.services.foundry_service import FoundryService
from src.utils.text import normalizar_texto

logger = logging.getLogger("ZelaFixAI.KnowledgeService")


def _texto_indexacao_chunk(chunk: Dict[str, Any]) -> str:
    keywords = ", ".join(chunk.get("keywords", []))
    return f"[{chunk['category']}] {chunk['title']}\nFonte: {chunk['source']}\n{chunk['content']}\nTermos relacionados: {keywords}"


class KnowledgeService:
    """
    Motor RAG Semântico ZelaFix AI:
    - Vetorização semântica densa em nuvem (`embed-v-4-0`, 1536D) persistida no ChromaDB.
    - Fingerprint SHA-256 para evitar chamadas de reindexação no startup quando a base não mudou.
    - Fallback automático em memória e contingência offline caso a rede externa falhe.
    """

    _lock = threading.Lock()
    _chunks_indexados: List[Dict[str, Any]] = []
    _embeddings_por_id: Dict[str, List[float]] = {}
    _indice_inicializado: bool = False

    @classmethod
    def inicializar_indice_rag(cls) -> None:
        with cls._lock:
            if cls._indice_inicializado and len(cls._embeddings_por_id) == len(BASE_CHUNKS_RAG):
                return

            cls._chunks_indexados = list(BASE_CHUNKS_RAG)
            vs = get_vector_store()

            # 1. Reutiliza vetores já persistidos em disco se a base normativa não mudou
            if vs.is_ready and vs.indice_atualizado(cls._chunks_indexados, cfg.AI_EMBEDDING_MODEL):
                em_disco = vs.carregar_embeddings_em_disco()
                if len(em_disco) == len(cls._chunks_indexados):
                    cls._embeddings_por_id = em_disco
                    cls._indice_inicializado = True
                    logger.info(f"RAG aquecido do ChromaDB em disco ({len(em_disco)} chunks, 0 chamadas de API).")
                    return

            # 2. Caso base nova ou container limpo, gera embeddings em lote no Azure AI Foundry
            textos = [_texto_indexacao_chunk(c) for c in cls._chunks_indexados]
            vetores = FoundryService.gerar_embeddings(textos)
            if vetores and len(vetores) == len(cls._chunks_indexados):
                cls._embeddings_por_id = {c["id"]: v for c, v in zip(cls._chunks_indexados, vetores)}
                if vs.is_ready:
                    vs.seed_knowledge_base(cls._chunks_indexados, vetores, cfg.AI_EMBEDDING_MODEL)
                cls._indice_inicializado = True
                return

            logger.warning("Azure AI Foundry indisponível para indexação inicial; fallback offline habilitado.")
            cls._indice_inicializado = True

    @classmethod
    def _fallback_contingencia_offline(
        cls,
        pergunta: str,
        top_k: int,
        categoria_filtro: Optional[str],
    ) -> Dict[str, Any]:
        """Contingência mínima caso o endpoint de embeddings em nuvem esteja offline."""
        termos = {t for t in normalizar_texto(pergunta).split() if len(t) > 2}
        if not termos:
            return {"match_found": False, "chunks": []}

        ranqueados = []
        for c in cls._chunks_indexados:
            if categoria_filtro and c["category"] != categoria_filtro:
                continue
            alvo = normalizar_texto(f"{c['title']} {' '.join(c.get('keywords', []))}")
            hits = sum(1 for t in termos if t in alvo)
            if hits >= 2:
                score = round(min(0.95, 0.25 + 0.12 * hits), 4)
                ranqueados.append((score, c))

        ranqueados.sort(key=lambda x: x[0], reverse=True)
        chunks = [
            {
                "id": c["id"],
                "source": c["source"],
                "category": c["category"],
                "title": c["title"],
                "content": c["content"],
                "urgency": c.get("urgency", "baixa"),
                "similarity_score": s,
                "vector_db": "OfflineFallback",
            }
            for s, c in ranqueados[:top_k]
        ]
        return {"match_found": len(chunks) > 0, "chunks": chunks}

    @classmethod
    def buscar_chunks_rag(
        cls,
        pergunta: str,
        top_k: int = 3,
        categoria_filtro: Optional[str] = None,
    ) -> Dict[str, Any]:
        cls.inicializar_indice_rag()
        if not pergunta or not pergunta.strip():
            return {"match_found": False, "chunks": []}

        query_vec = FoundryService.gerar_embedding(pergunta)
        if query_vec is None:
            return cls._fallback_contingencia_offline(pergunta, top_k, categoria_filtro)

        # 1. Busca semântica primária no ChromaDB (HNSW Cosine)
        vs = get_vector_store()
        if vs.is_ready and vs.count > 0:
            where_filter = {"category": categoria_filtro} if categoria_filtro else None
            resultados = vs.search(
                query_embedding=query_vec,
                top_k=top_k,
                min_score=cfg.RAG_MIN_SCORE,
                where=where_filter,
            )
            if resultados:
                return {"match_found": True, "chunks": resultados}
            return {"match_found": False, "chunks": []}

        # 2. Fallback em memória com vetores do Foundry caso ChromaDB não esteja montado
        if cls._embeddings_por_id:
            scores = []
            for c in cls._chunks_indexados:
                if categoria_filtro and c["category"] != categoria_filtro:
                    continue
                emb = cls._embeddings_por_id.get(c["id"])
                if not emb:
                    continue
                sim = sum(a * b for a, b in zip(query_vec, emb))
                if sim >= cfg.RAG_MIN_SCORE:
                    scores.append((sim, c))
            scores.sort(key=lambda x: x[0], reverse=True)
            chunks = [
                {
                    "id": c["id"],
                    "source": c["source"],
                    "category": c["category"],
                    "title": c["title"],
                    "content": c["content"],
                    "urgency": c.get("urgency", "baixa"),
                    "similarity_score": round(s, 4),
                    "vector_db": "FoundryInMem",
                }
                for s, c in scores[:top_k]
            ]
            return {"match_found": len(chunks) > 0, "chunks": chunks}

        return cls._fallback_contingencia_offline(pergunta, top_k, categoria_filtro)

    @classmethod
    def buscar_chunk_por_id(cls, chunk_id: str) -> Optional[Dict[str, Any]]:
        cls.inicializar_indice_rag()
        for chunk in cls._chunks_indexados:
            if chunk["id"] == chunk_id:
                return chunk
        return None
