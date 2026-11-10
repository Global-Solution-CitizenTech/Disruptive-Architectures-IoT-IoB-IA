"""
Schemas Pydantic: Triagem Técnica de Ocorrências e Insights de Bairro — ZelaFix AI
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from src.schemas.chamado import ChamadoContextPayload

class TriagemRequest(BaseModel):
    chamado: ChamadoContextPayload = Field(..., description="Dados completos da ocorrência urbana para triagem técnica")
    sessionId: Optional[str] = Field(default=None, description="ID de sessão opcional para rastreabilidade")

class TriagemResponse(BaseModel):
    prioridade: str = Field(..., description="Prioridade calculada: 'BAIXA', 'MEDIA', 'ALTA' ou 'URGENTE'")
    orgao_responsavel: str = Field(..., description="Secretaria ou órgão municipal competente (Subprefeitura, CET, Ilumina SP, Defesa Civil, Sabesp, Limpeza Urbana)")
    parecer_ia: str = Field(..., description="Parecer técnico objetivo (máximo 150 caracteres para persistência no banco)")
    sla_sugerido_horas: int = Field(..., description="Prazo normativo regulamentar de atendimento em horas")
    enquadramento_legal: str = Field(..., description="Decreto municipal ou lei regulatória aplicável")
    risco_potencial: str = Field(..., description="Avaliação do impacto físico e risco à segurança coletiva")
    checklist_vistoria: List[str] = Field(default_factory=list, description="Checklist de ações técnicas recomendadas para a vistoria de campo")
    origem_triagem: str = Field(default="ZelaFix AI Triagem Multimodal + RAG", description="Mecanismo que emitiu o laudo")

class InsightItem(BaseModel):
    categoria: str = Field(..., description="Eixo do alerta: 'pavimentacao', 'drenagem', 'iluminacao', 'limpeza_urbana', 'seguranca'")
    titulo: str = Field(..., description="Título conciso do insight de zeladoria")
    descricao: str = Field(..., description="Recomendação ou alerta comunitário para o bairro")
    urgencia: str = Field(..., description="Nível de atenção: 'baixa', 'media' ou 'alta'")

class InsightsResponse(BaseModel):
    bairro: str = Field(..., description="Bairro ou região analisada")
    total_alertas: int = Field(..., description="Quantidade total de insights gerados")
    insights: List[InsightItem] = Field(..., description="Lista de insights preventivos de zeladoria urbana")
