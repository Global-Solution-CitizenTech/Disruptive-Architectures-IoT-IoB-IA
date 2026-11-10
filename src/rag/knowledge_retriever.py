"""
Recuperador de Conhecimento e Enriquecedor de Contexto RAG
Prepara o contexto regulatório para injeção no prompt da IA Generativa
"""

from typing import List, Optional, Tuple, Dict, Any
from .vector_store import RagVectorStore
from ..schemas.rag_models import RagDocumentChunk, RagQueryResponse
from ..config import ORGAOS_COMPETENTES

class KnowledgeRetriever:
    """Orquestra a busca no RAG e formata o contexto legal para o LLM."""

    def __init__(self, vector_store: Optional[RagVectorStore] = None):
        self.vector_store = vector_store or RagVectorStore()

    def retrieve_context(
        self,
        titulo: str,
        descricao: str,
        categoria: Optional[str] = None,
        top_k: int = 3
    ) -> Tuple[str, List[RagDocumentChunk], Dict[str, Any]]:
        """
        Recupera os chunks regulatórios mais relevantes e extrai:
        - Texto formatado do contexto
        - Lista de chunks
        - Metadados consolidados (base legal primária, SLA e órgão sugerido)
        """
        query = f"{titulo}. {descricao}".strip()
        chunks = self.vector_store.search(query=query, category_hint=categoria, top_k=top_k)

        if not chunks:
            # Fallback se base de dados não tiver retornado
            default_agency = ORGAOS_COMPETENTES.get(categoria, "Central de Zeladoria Municipal 156") if categoria else "Central de Zeladoria Municipal 156"
            return (
                f"Diretriz Geral de Zeladoria Urbana da Cidade de São Paulo. Órgão Competente: {default_agency}.",
                [],
                {
                    "base_legal": "Decreto Municipal de Zeladoria Urbana e Código de Posturas",
                    "sla_horas": 48,
                    "orgao_competente": default_agency
                }
            )

        # Monta o contexto textual para o prompt
        context_parts = []
        primary_law = chunks[0].law_article or "Normas Técnicas de Zeladoria Urbana de São Paulo"
        primary_agency = chunks[0].competent_agency or (ORGAOS_COMPETENTES.get(categoria) if categoria else "Subprefeitura Local")
        primary_sla = chunks[0].sla_hours or 48

        for i, chk in enumerate(chunks, start=1):
            context_parts.append(
                f"[Documento {i}: {chk.title}]\n"
                f"Base Legal: {chk.law_article or 'PMSP'}\n"
                f"Órgão: {chk.competent_agency or primary_agency}\n"
                f"Conteúdo:\n{chk.content}\n"
            )
            # Atualiza SLA se encontrar algum chunk mais específico com prazo menor (urgência)
            if chk.sla_hours and chk.sla_hours < primary_sla:
                primary_sla = chk.sla_hours

        full_context = "\n---\n".join(context_parts)
        metadata = {
            "base_legal": primary_law,
            "sla_horas": primary_sla,
            "orgao_competente": primary_agency
        }

        return full_context, chunks, metadata

    def query(self, query_text: str, categoria: Optional[str] = None, top_k: int = 3) -> RagQueryResponse:
        """Executa consulta direta ao RAG e retorna DTO formatado."""
        context, chunks, _ = self.retrieve_context(
            titulo=query_text,
            descricao="",
            categoria=categoria,
            top_k=top_k
        )
        return RagQueryResponse(
            query=query_text,
            total_chunks_found=len(chunks),
            chunks=chunks,
            context_text=context
        )

