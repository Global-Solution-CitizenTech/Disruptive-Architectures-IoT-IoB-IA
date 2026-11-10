"""
Módulo de Banco de Dados Vetorial ChromaDB — ZelaFix AI
Persistência vetorial em disco (./data/chroma) com embeddings densos e busca por similaridade.
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)
"""
import os
import logging
import threading
from typing import List, Dict, Any, Optional

from src.core.config import RAG_MIN_SCORE
from src.utils.embeddings import LocalSemanticEmbedder

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
CHROMA_DIR = os.path.join(DATA_DIR, "chroma")
COLLECTION_NAME = f"zelafix_knowledge_{LocalSemanticEmbedder.DIMENSAO}d"

_vector_store_lock = threading.Lock()

class ChromaVectorStore:
    """
    Gerenciador do Banco de Dados Vetorial ChromaDB para o ZelaFix AI.
    - Persistência física em disco em `./data/chroma`.
    - Coleção 'zelafix_knowledge' com indexação vetorial HNSW.
    - Embeddings densos normalizados gerados pelo LocalSemanticEmbedder (512-D).
    """

    _instance: Optional["ChromaVectorStore"] = None
    _client = None
    _collection = None
    _is_ready: bool = False

    def __init__(self) -> None:
        self.chroma_dir = CHROMA_DIR
        self._ensure_storage_dir()
        self._init_chroma()

    def _ensure_storage_dir(self) -> None:
        """Garante a existência do diretório `./data/chroma`."""
        if not os.path.exists(self.chroma_dir):
            os.makedirs(self.chroma_dir, exist_ok=True)

    def _init_chroma(self) -> None:
        """Inicializa o cliente persistente do ChromaDB."""
        try:
            import chromadb
            from chromadb.config import Settings

            self._client = chromadb.PersistentClient(
                path=self.chroma_dir,
                settings=Settings(anonymized_telemetry=False, allow_reset=True)
            )

            # Obtém ou cria a coleção vetorial com distância de cosseno
            self._collection = self._client.get_or_create_collection(
                name=COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )
            self._is_ready = True
            logger.info(f"ChromaDB inicializado com sucesso em: {self.chroma_dir} (Coleção: '{COLLECTION_NAME}')")
        except ImportError:
            logger.warning("ChromaDB não instalado neste ambiente. Operando com motor vetorial resiliente integrado.")
            self._is_ready = False
        except Exception as e:
            logger.error(f"Erro ao inicializar ChromaDB: {e}. Ativando modo resiliente.")
            self._is_ready = False

    @classmethod
    def get_instance(cls) -> "ChromaVectorStore":
        """Singleton thread-safe para acesso ao banco vetorial."""
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

    def seed_knowledge_base(
        self,
        chunks: List[Dict[str, Any]],
        embeddings: Optional[List[List[float]]] = None
    ) -> int:
        """
        Carrega e indexa todos os chunks normativos da base de conhecimento no ChromaDB.
        Recebe a lista de embeddings do LocalSemanticEmbedder
        e os persiste diretamente no HNSW.
        """
        if not self._is_ready or self._collection is None:
            logger.warning("ChromaDB inativo; carga inicial armazenada no índice vetorial da memória.")
            return 0

        try:
            ids = [chunk["id"] for chunk in chunks]
            documents = [chunk["content"] for chunk in chunks]
            metadatas = [
                {
                    "source": str(chunk.get("source", "knowledge_base")),
                    "category": str(chunk.get("category", "geral")),
                    "title": str(chunk.get("title", "")),
                    "urgency": str(chunk.get("urgency", "baixa")),
                    "content": str(chunk.get("content", ""))
                }
                for chunk in chunks
            ]

            upsert_kwargs: Dict[str, Any] = {
                "ids": ids,
                "documents": documents,
                "metadatas": metadatas,
            }
            if embeddings is not None:
                upsert_kwargs["embeddings"] = embeddings

            self._collection.upsert(**upsert_kwargs)
            logger.info(f"ChromaDB: {len(ids)} chunks normativos indexados com persistência vetorial em {self.chroma_dir}.")
            return len(ids)
        except Exception as e:
            logger.error(f"Erro ao carregar chunks no ChromaDB: {e}")
            return 0

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 3,
        min_score: float = RAG_MIN_SCORE
    ) -> List[Dict[str, Any]]:
        """
        Realiza consulta vetorial por similaridade no ChromaDB com query_embeddings pré-calculados.
        Converte a distância de cosseno do Chroma (0 = idêntico, 2 = oposto)
        em score de similaridade (1.0 - distância) normalizado.
        """
        if not self._is_ready or self._collection is None or self.count == 0:
            return []

        try:
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )

            if not results or not results["ids"] or not results["ids"][0]:
                return []

            matched = []
            for doc_id, doc_text, meta, dist in zip(
                results["ids"][0],
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            ):
                score = round(max(0.0, 1.0 - float(dist)), 4)
                if score >= min_score:
                    conteudo_limpo = meta.get("content", doc_text) if meta else doc_text
                    matched.append({
                        "id": doc_id,
                        "source": meta.get("source", "chromadb_vector_store") if meta else "chromadb_vector_store",
                        "category": meta.get("category", "geral") if meta else "geral",
                        "title": meta.get("title", "") if meta else "",
                        "content": conteudo_limpo,
                        "similarity_score": score,
                        "vector_db": "ChromaDB"
                    })

            return matched
        except Exception as e:
            logger.error(f"Erro na busca vetorial no ChromaDB: {e}")
            return []

def get_vector_store() -> ChromaVectorStore:
    """Helper para obter o singleton do banco vetorial ChromaDB."""
    return ChromaVectorStore.get_instance()
