"""
Serviço de Conhecimento: Motor RAG com Embeddings Vetoriais Locais e Similaridade de Cosseno — ZelaFix AI
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)
"""
import logging
import math
from typing import Optional, Dict, Any, List, Set
from collections import Counter
from src.core.config import RAG_MIN_SCORE
from src.knowledge import BASE_CHUNKS_RAG
from src.utils.text import normalizar_texto, tokenizar_com_ngrams, expansao_semantica_urbana
from src.utils.embeddings import LocalSemanticEmbedder, calcular_similaridade_cosseno
from src.database.vector_store import get_vector_store

logger = logging.getLogger("ZelaFixAI.KnowledgeService")

class KnowledgeService:
    """
    Serviço de Conhecimento ZelaFix AI:
    1. Pipeline RAG com representação vetorial em espaço denso contínuo (Embeddings densos 512D) e Similaridade de Cosseno.
    2. Indexação híbrida com persistência no ChromaDB e motor em memória resiliente.
    3. Suporte a consultas de triagem e orientação cívica fundamentada em decretos municipais de São Paulo.
    """

    _vocabulario_idf: Dict[str, float] = {}
    _embeddings_chunks: List[List[float]] = []
    _tokens_chunks: List[Set[str]] = []
    _tokens_chunks_map: Dict[str, Set[str]] = {}
    _raw_tokens_chunks_map: Dict[str, Set[str]] = {}
    _chunks_indexados: List[Dict[str, Any]] = []
    _indice_inicializado: bool = False

    @classmethod
    def inicializar_indice_rag(cls) -> None:
        """
        Calcula o vocabulário IDF e gera embeddings densos para
        todos os chunks normativos da Base de Conhecimento ZelaFix.
        Executado uma única vez na inicialização em memória (< 15 MB de RAM no Render).
        """
        if cls._indice_inicializado and cls._embeddings_chunks:
            return

        cls._chunks_indexados = list(BASE_CHUNKS_RAG)
        num_docs = len(cls._chunks_indexados)

        # 1. Contagem de frequência documental (DF) e indexação de tokens
        doc_freqs: Counter = Counter()
        cls._tokens_chunks = []
        cls._tokens_chunks_map = {}
        cls._raw_tokens_chunks_map = {}
        for chunk in cls._chunks_indexados:
            texto_completo = f"{chunk['title']} {chunk['content']} {' '.join(chunk.get('keywords', []))}"
            tokens = tokenizar_com_ngrams(texto_completo, n_max=2)
            tokens_expandidos = expansao_semantica_urbana(tokens)
            set_tokens = set(tokens_expandidos)
            cls._tokens_chunks.append(set_tokens)
            cls._tokens_chunks_map[chunk["id"]] = set_tokens
            cls._raw_tokens_chunks_map[chunk["id"]] = set(tokens)
            for t in set_tokens:
                doc_freqs[t] += 1

        # 2. IDF suavizado
        cls._vocabulario_idf = {}
        for termo, df in doc_freqs.items():
            cls._vocabulario_idf[termo] = math.log((num_docs + 1) / (df + 1)) + 1.0

        # 3. Geração dos Embeddings Vetoriais Densos
        cls._embeddings_chunks = []
        for chunk in cls._chunks_indexados:
            texto_chunk = f"{chunk['title']} {chunk['content']} {' '.join(chunk.get('keywords', []))}"
            embedding = LocalSemanticEmbedder.gerar_embedding(texto_chunk, idf_weights=cls._vocabulario_idf)
            cls._embeddings_chunks.append(embedding)

        cls._indice_inicializado = True

        # 4. Persistência e indexação no Banco de Dados Vetorial ChromaDB com os embeddings densos
        try:
            vector_store = get_vector_store()
            if vector_store.is_ready:
                vector_store.seed_knowledge_base(cls._chunks_indexados, embeddings=cls._embeddings_chunks)
        except Exception as e:
            logger.warning(f"ChromaDB indisponível, usando motor em memória: {e}")

    @classmethod
    def buscar_chunks_rag(
        cls,
        pergunta: str,
        top_k: int = 3,
        categoria_filtro: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executa a busca semântica vetorial dos trechos mais relevantes para a dúvida do cidadão:
        1. Consulta primária via Banco de Dados Vetorial ChromaDB (persistido em disco).
        2. Fallback integrado com produto escalar denso em memória (garantia de disponibilidade 100%).
        """
        cls.inicializar_indice_rag()

        if not pergunta or not pergunta.strip():
            return {"match_found": False, "chunks": []}

        # Gera o embedding denso da consulta utilizando o vocabulário e expansão semântica
        embedding_query = LocalSemanticEmbedder.gerar_embedding(pergunta, idf_weights=cls._vocabulario_idf)

        tokens_originais = set(tokenizar_com_ngrams(pergunta, n_max=2))
        tokens_query = set(expansao_semantica_urbana(list(tokens_originais)))

        # 1. Tenta consulta direta no ChromaDB com filtro nativo e re-ranking híbrido lexical
        try:
            vector_store = get_vector_store()
            if vector_store.is_ready and vector_store.count > 0:
                where_filter = {"category": categoria_filtro} if categoria_filtro else None
                resultados_chroma = vector_store.search(
                    embedding_query,
                    top_k=max(top_k * 3, 8),
                    min_score=RAG_MIN_SCORE,
                    where=where_filter,
                )
                if resultados_chroma:
                    if categoria_filtro:
                        resultados_chroma = [r for r in resultados_chroma if r.get("category") == categoria_filtro]
                    if resultados_chroma:
                        for item in resultados_chroma:
                            raw_chunk = cls._raw_tokens_chunks_map.get(item["id"], set())
                            overlap_exato = len(tokens_originais.intersection(raw_chunk))
                            tokens_chunk = cls._tokens_chunks_map.get(item["id"], set())
                            overlap_sem = len(tokens_query.intersection(tokens_chunk))
                            boost = (0.06 * min(overlap_exato, 4)) + (0.02 * min(overlap_sem, 3))
                            item["similarity_score"] = round(min(1.0, item["similarity_score"] + boost), 4)
                        resultados_chroma.sort(key=lambda x: x["similarity_score"], reverse=True)
                        return {"match_found": True, "chunks": resultados_chroma[:top_k]}
        except Exception as e:
            logger.warning(f"Falha na consulta ao ChromaDB, chaveando para motor vetorial em memória: {e}")

        # 2. Motor Vetorial Resiliente em Memória
        scores = []
        for i, chunk in enumerate(cls._chunks_indexados):
            if categoria_filtro and chunk["category"] != categoria_filtro:
                continue

            emb_chunk = cls._embeddings_chunks[i]
            sim_cosseno = calcular_similaridade_cosseno(embedding_query, emb_chunk)

            # Boost semântico por sobreposição de termos-chave específicos
            overlap = len(tokens_query.intersection(cls._tokens_chunks[i]))
            score_final = sim_cosseno + (0.05 * min(overlap, 4))

            if score_final >= RAG_MIN_SCORE:
                scores.append((score_final, chunk))

        scores.sort(key=lambda x: x[0], reverse=True)
        top_chunks = scores[:top_k]

        if not top_chunks:
            return {"match_found": False, "chunks": []}

        resultado_formatado = []
        for score, chunk in top_chunks:
            resultado_formatado.append({
                "id": chunk["id"],
                "source": chunk["source"],
                "category": chunk["category"],
                "title": chunk["title"],
                "content": chunk["content"],
                "urgency": chunk.get("urgency", "baixa"),
                "similarity_score": round(score, 4),
                "vector_db": "LocalInMem"
            })

        return {"match_found": True, "chunks": resultado_formatado}

    @classmethod
    def buscar_chunk_por_id(cls, chunk_id: str) -> Optional[Dict[str, Any]]:
        """Recupera diretamente um chunk pelo identificador único (ex: 'pav_01')."""
        cls.inicializar_indice_rag()
        for chunk in cls._chunks_indexados:
            if chunk["id"] == chunk_id:
                return chunk
        return None
