"""
Módulo de Banco de Dados Vetorial ChromaDB — ZelaFix AI
Persistência vetorial em disco (./data/chroma) com embeddings densos em nuvem (Azure AI Foundry).
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)
"""
import os
import json
import hashlib
import logging
import threading
from typing import List, Dict, Any, Optional

from src.core.config import RAG_MIN_SCORE, AI_EMBEDDING_MODEL, AI_EMBEDDING_DIMENSIONS

logger = logging.getLogger("ZelaFixAI.VectorStore")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
CHROMA_DIR = os.path.join(DATA_DIR, "chroma")
FINGERPRINT_PATH = os.path.join(DATA_DIR, "kb_fingerprint.json")
COLLECTION_NAME = f"zelafix_knowledge_foundry_{AI_EMBEDDING_DIMENSIONS}d"

_vector_store_lock = threading.Lock()


def calcular_fingerprint_kb(chunks: List[Dict[str, Any]], embedding_model: str = AI_EMBEDDING_MODEL) -> str:
    """Calcula assinatura determinística dos chunks + modelo de embedding para evitar reindexação desnecessária."""
    payload = {
        "model": embedding_model,
        "dims": AI_EMBEDDING_DIMENSIONS,
        "chunks": [
            {
                "id": c["id"],
                "source": c["source"],
                "category": c["category"],
                "urgency": c.get("urgency", "baixa"),
                "title": c["title"],
                "content": c["content"],
                "keywords": c.get("keywords", []),
            }
            for c in chunks
        ],
    }
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


class ChromaVectorStore:
    """Gerenciador persistente do ChromaDB com índice HNSW (distância cosseno)."""

    _instance: Optional["ChromaVectorStore"] = None
    _client = None
    _collection = None
    _is_ready: bool = False

    def __init__(self) -> None:
        self.chroma_dir = CHROMA_DIR
        os.makedirs(self.chroma_dir, exist_ok=True)
        self._init_chroma()

    def _init_chroma(self) -> None:
        try:
            import chromadb
            from chromadb.config import Settings

            self._client = chromadb.PersistentClient(
                path=self.chroma_dir,
                settings=Settings(anonymized_telemetry=False, allow_reset=True),
            )
            self._collection = self._client.get_or_create_collection(
                name=COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"},
            )
            self._is_ready = True
            logger.info(f"ChromaDB pronto em '{self.chroma_dir}' (Coleção: '{COLLECTION_NAME}').")
        except Exception as err:
            logger.warning(f"ChromaDB indisponível, operando em memória: {err}")
            self._is_ready = False

    @classmethod
    def get_instance(cls) -> "ChromaVectorStore":
        with _vector_store_lock:
            if cls._instance is None:
                cls._instance = ChromaVectorStore()
            return cls._instance

    @property
    def is_ready(self) -> bool:
        return self._is_ready

    @property
    def count(self) -> int:
        if self._is_ready and self._collection is not None:
            try:
                return self._collection.count()
            except Exception:
                return 0
        return 0

    def indice_atualizado(self, chunks: List[Dict[str, Any]], embedding_model: str = AI_EMBEDDING_MODEL) -> bool:
        """Verifica se o índice persistido no ChromaDB já corresponde exatamente ao catálogo atual."""
        if not self._is_ready or self.count != len(chunks) or not os.path.isfile(FINGERPRINT_PATH):
            return False
        try:
            with open(FINGERPRINT_PATH, "r", encoding="utf-8") as fp:
                salvo = json.load(fp).get("fingerprint")
            return salvo == calcular_fingerprint_kb(chunks, embedding_model)
        except Exception:
            return False

    def seed_knowledge_base(
        self,
        chunks: List[Dict[str, Any]],
        embeddings: List[List[float]],
        embedding_model: str = AI_EMBEDDING_MODEL,
    ) -> int:
        """Persiste todos os chunks normativos e seus vetores densos no ChromaDB."""
        if not self._is_ready or self._collection is None:
            return 0

        try:
            ids = [c["id"] for c in chunks]
            documents = [c["content"] for c in chunks]
            metadatas = [
                {
                    "source": str(c.get("source", "knowledge_base")),
                    "category": str(c.get("category", "geral")),
                    "title": str(c.get("title", "")),
                    "urgency": str(c.get("urgency", "baixa")),
                    "content": str(c.get("content", "")),
                }
                for c in chunks
            ]

            existentes = self._collection.get(include=[])
            ids_orfaos = list(set(existentes.get("ids") or []) - set(ids))
            if ids_orfaos:
                self._collection.delete(ids=ids_orfaos)

            self._collection.upsert(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)

            with open(FINGERPRINT_PATH, "w", encoding="utf-8") as fp:
                json.dump({"fingerprint": calcular_fingerprint_kb(chunks, embedding_model)}, fp)

            logger.info(f"ChromaDB indexado: {len(ids)} chunks ({embedding_model}, {AI_EMBEDDING_DIMENSIONS}D).")
            return len(ids)
        except Exception as err:
            logger.error(f"Erro ao indexar chunks no ChromaDB: {err}")
            return 0

    def carregar_embeddings_em_disco(self) -> Dict[str, List[float]]:
        """Recupera embeddings persistidos no ChromaDB para aquecimento em memória sem custo de API."""
        if not self._is_ready or self._collection is None or self.count == 0:
            return {}
        try:
            dados = self._collection.get(include=["embeddings"])
            ids = dados.get("ids") or []
            embs = dados.get("embeddings")
            if embs is None:
                return {}
            return {cid: list(vec) for cid, vec in zip(ids, embs)}
        except Exception as err:
            logger.warning(f"Falha ao ler embeddings persistidos do ChromaDB: {err}")
            return {}

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 3,
        min_score: float = RAG_MIN_SCORE,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Busca vetorial HNSW por distância de cosseno no ChromaDB."""
        if not self._is_ready or self._collection is None or self.count == 0:
            return []

        try:
            query_kwargs: Dict[str, Any] = {
                "query_embeddings": [query_embedding],
                "n_results": min(top_k, max(1, self.count)),
                "include": ["documents", "metadatas", "distances"],
            }
            if where:
                query_kwargs["where"] = where

            results = self._collection.query(**query_kwargs)
            if not results or not results["ids"] or not results["ids"][0]:
                return []

            matched = []
            for doc_id, doc_text, meta, dist in zip(
                results["ids"][0],
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            ):
                score = round(max(0.0, 1.0 - float(dist)), 4)
                if score >= min_score:
                    matched.append({
                        "id": doc_id,
                        "source": meta.get("source", "chromadb") if meta else "chromadb",
                        "category": meta.get("category", "geral") if meta else "geral",
                        "title": meta.get("title", "") if meta else "",
                        "urgency": meta.get("urgency", "baixa") if meta else "baixa",
                        "content": meta.get("content", doc_text) if meta else doc_text,
                        "similarity_score": score,
                        "vector_db": "ChromaDB",
                    })
            return matched
        except Exception as err:
            logger.error(f"Erro na busca vetorial do ChromaDB: {err}")
            return []


def get_vector_store() -> ChromaVectorStore:
    return ChromaVectorStore.get_instance()
