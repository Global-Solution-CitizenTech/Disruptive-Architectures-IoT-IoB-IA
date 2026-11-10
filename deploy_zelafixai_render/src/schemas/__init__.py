"""
Módulo de Schemas Pydantic: ZelaFix AI
"""
from src.schemas.chamado import ChamadoContextPayload, TelemetriaIotPayload
from src.schemas.chat import (
    MensagemHistorico,
    RetrievedSource,
    ChatRequest,
    ChatResponse,
    MensagemBancoItem,
    AuditoriaBancoItem,
    HistoricoResponse,
    AuditoriaResponse,
    SessaoItem,
    SessoesResponse,
)
from src.schemas.insights import (
    TriagemRequest,
    TriagemResponse,
    InsightItem,
    InsightsResponse,
)

__all__ = [
    "ChamadoContextPayload",
    "TelemetriaIotPayload",
    "MensagemHistorico",
    "RetrievedSource",
    "ChatRequest",
    "ChatResponse",
    "MensagemBancoItem",
    "AuditoriaBancoItem",
    "HistoricoResponse",
    "AuditoriaResponse",
    "SessaoItem",
    "SessoesResponse",
    "TriagemRequest",
    "TriagemResponse",
    "InsightItem",
    "InsightsResponse",
]
