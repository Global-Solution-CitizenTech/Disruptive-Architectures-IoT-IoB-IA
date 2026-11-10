"""
Testes Unitários do Módulo de Recuperação Aumentada por Geração (RAG - Aprofundamento 2)
"""

from src.rag.vector_store import RagVectorStore
from src.rag.knowledge_retriever import KnowledgeRetriever

def test_vector_store_indexing():
    store = RagVectorStore()
    assert len(store.chunks) > 5
    assert store.tfidf_matrix is not None

def test_rag_search_relevance():
    store = RagVectorStore()
    results = store.search(
        query="Buraco na via com profundidade maior que cinco centímetros e tráfego pesado",
        category_hint="Buraco na Rua",
        top_k=2
    )
    assert len(results) > 0
    top_chunk = results[0]
    assert "Pavimentação" in top_chunk.title or "Buraco" in top_chunk.title
    assert top_chunk.similarity_score > 0.1

def test_knowledge_retriever_context_building():
    retriever = KnowledgeRetriever()
    context, chunks, meta = retriever.retrieve_context(
        titulo="Árvore tombando em cima da fiação elétrica",
        descricao="Faíscas saindo dos fios após tempestade forte",
        categoria="Poda de Árvore",
        top_k=2
    )
    assert len(chunks) > 0
    assert "Base Legal:" in context
    assert "Órgão:" in context
    assert meta["sla_horas"] in [12, 24, 48]
    assert "Defesa Civil" in meta["orgao_competente"] or "Manejo" in meta["orgao_competente"]

