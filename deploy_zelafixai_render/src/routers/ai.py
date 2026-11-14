"""
Router de IA Generativa, Triagem Urbana e Persistência SQLite — ZelaFix AI
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)
"""
from typing import Optional
from fastapi import APIRouter, Query, HTTPException
from src.schemas.chat import (
    ChatRequest,
    ChatResponse,
    HistoricoResponse,
    AuditoriaResponse,
    MensagemBancoItem,
    AuditoriaBancoItem,
    SessaoItem,
    SessoesResponse
)
from src.schemas.insights import (
    TriagemRequest,
    TriagemResponse,
    InsightsResponse
)
from src.services.chat_service import ChatService
from src.services.triagem_service import TriagemService
from src.services.insights_service import InsightsService
from src.repositories.chat_repository import ChatRepository

ai_router = APIRouter(prefix="/ai", tags=["AI & Triagem Urbana"])

@ai_router.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """
    Processa interação conversacional no ZelaBot com contexto da ocorrência e histórico multi-turnos,
    persistindo automaticamente a conversa e a auditoria de zeladoria no SQLite.
    """
    return ChatService.processar_chat(request)

@ai_router.post("/triagem", response_model=TriagemResponse)
def triagem_endpoint(request: TriagemRequest) -> TriagemResponse:
    """
    Emite Laudo Técnico Oficial de Triagem Urbana fundamentado na legislação municipal de São Paulo,
    classificando prioridade (BAIXA a URGENTE), órgão competente, SLA regulamentar e checklist de vistoria.
    """
    return TriagemService.realizar_triagem(request)

@ai_router.post("/insights", response_model=InsightsResponse)
def insights_endpoint(
    bairro: Optional[str] = Query(None, description="Bairro ou região municipal para geração de alertas preventivos")
) -> InsightsResponse:
    """
    Gera diagnósticos e alertas preventivos comunitários para o bairro informado (ODS 11).
    """
    return InsightsService.gerar_insights_bairro(bairro)

@ai_router.get("/history", response_model=HistoricoResponse)
def buscar_historico_endpoint(
    session_id: Optional[str] = Query(None, description="Filtrar por ID da sessão"),
    chamado_id: Optional[int] = Query(None, description="Filtrar por ID do chamado"),
    limit: int = Query(50, ge=1, le=200, description="Limite máximo de mensagens")
) -> HistoricoResponse:
    """
    Consulta o histórico de mensagens gravadas no SQLite por sessão ou por chamado municipal.
    """
    dados = ChatRepository.buscar_historico(session_id=session_id, chamado_id=chamado_id, limit=limit)
    itens = [MensagemBancoItem(**row) for row in dados]
    return HistoricoResponse(total=len(itens), mensagens=itens)

@ai_router.get("/audit", response_model=AuditoriaResponse)
def listar_auditorias_endpoint(
    chamado_id: Optional[int] = Query(None, description="Filtrar por ID do chamado"),
    bairro: Optional[str] = Query(None, description="Filtrar por bairro"),
    limit: int = Query(20, ge=1, le=100, description="Limite máximo de auditorias")
) -> AuditoriaResponse:
    """
    Consulta os últimos laudos técnicos e triagens auditadas no banco de dados relacional SQLite.
    """
    dados = ChatRepository.listar_auditorias(chamado_id=chamado_id, bairro=bairro, limit=limit)
    itens = [AuditoriaBancoItem(**row) for row in dados]
    return AuditoriaResponse(total=len(itens), auditorias=itens)

@ai_router.get("/sessions", response_model=SessoesResponse)
def listar_sessoes_endpoint(
    limit: int = Query(30, ge=1, le=100, description="Limite de sessões retornadas")
) -> SessoesResponse:
    """
    Lista as conversas anteriores do munícipe agrupadas por sessão,
    com título da 1ª pergunta, total de mensagens e data da última interação.
    """
    dados = ChatRepository.listar_sessoes(limit=limit)
    itens = [SessaoItem(**row) for row in dados]
    return SessoesResponse(total=len(itens), sessoes=itens)

@ai_router.delete("/sessions/{session_id}")
def excluir_sessao_endpoint(session_id: str) -> dict:
    """
    Exclui permanentemente uma sessão de conversa do histórico e da auditoria SQLite.
    """
    sucesso = ChatRepository.excluir_sessao(session_id)
    return {"status": "ok" if sucesso else "error", "session_id": session_id}

@ai_router.get("/vector-store/status")
def vector_store_status_endpoint() -> dict:
    """
    Retorna o status do Banco de Dados Vetorial ChromaDB (persistência, coleção e chunks indexados).
    """
    from src.database.vector_store import get_vector_store, CHROMA_DIR, COLLECTION_NAME
    from src.core.config import AI_EMBEDDING_DIMENSIONS, AI_EMBEDDING_MODEL
    vs = get_vector_store()
    return {
        "status": "online" if vs.is_ready else "fallback_mode",
        "database": "ChromaDB (HNSW)",
        "embedding_model": AI_EMBEDDING_MODEL,
        "storage_path": CHROMA_DIR,
        "collection_name": COLLECTION_NAME,
        "indexed_chunks": vs.count,
        "vector_dimensions": AI_EMBEDDING_DIMENSIONS,
        "distance_metric": "cosine"
    }

@ai_router.get("/oracle/status")
def oracle_status_endpoint() -> dict:
    """
    Retorna o status de conexão em tempo real com o banco de dados Oracle FIAP (Modo Thin nativo).
    """
    from src.database.oracle_client import OracleClient
    return OracleClient.verificar_conexao()

@ai_router.get("/chamados")
def listar_chamados_oracle_endpoint(
    limit: int = Query(10, ge=1, le=25, description="Quantidade máxima de chamados (limitado a 25)"),
    bairro: Optional[str] = Query(None, description="Filtrar por bairro")
) -> dict:
    """
    Lista os chamados mais recentes cadastrados no banco de dados Oracle da FIAP (somente leitura).
    """
    from src.database.oracle_client import OracleClient
    chamados = OracleClient.listar_chamados_recentes(limit=limit, bairro=bairro)
    return {
        "total": len(chamados),
        "chamados": chamados
    }

@ai_router.get("/chamados/{id_chamado}")
def consultar_chamado_oracle_endpoint(id_chamado: int) -> dict:
    """
    Consulta (somente leitura) um chamado no banco Oracle FIAP sem baixar BLOBs,
    retornando 404 se inexistente ou 503 se o Oracle estiver indisponível.
    """
    from src.database.oracle_client import OracleClient
    from src.services.triagem_service import TriagemService
    from src.schemas.chamado import ChamadoContextPayload
    from src.schemas.insights import TriagemRequest

    dados, status_db = OracleClient.consultar_chamado_com_status(id_chamado, incluir_foto=False)
    if status_db in ("oracle_offline", "erro"):
        raise HTTPException(
            status_code=503,
            detail=f"Banco Oracle FIAP indisponível ao consultar o chamado {id_chamado}."
        )
    if not dados or status_db == "nao_encontrado":
        raise HTTPException(
            status_code=404,
            detail=f"Chamado de ID {id_chamado} não foi localizado na base Oracle FIAP."
        )

    payload_chamado = ChamadoContextPayload(
        id=dados["id"],
        titulo=dados["titulo"],
        categoria=dados["categoria"],
        descricao=dados["descricao"],
        bairro=dados["bairro"],
        logradouro=dados["logradouro"],
        cep=dados["cep"],
        apoios_comunitarios=dados["apoios_comunitarios"]
    )
    triagem = TriagemService.realizar_triagem(TriagemRequest(chamado=payload_chamado))
    dados_resposta = {k: v for k, v in dados.items() if k != "foto_bytes"}

    return {
        "status": "sucesso",
        "chamado": dados_resposta,
        "parecer_tecnico": triagem.model_dump()
    }
