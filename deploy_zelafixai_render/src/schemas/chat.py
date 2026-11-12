"""
Schemas Pydantic: Conversação, Chat, RAG e Auditoria de Zeladoria — ZelaFix AI
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from src.schemas.chamado import ChamadoContextPayload

class MensagemHistorico(BaseModel):
    sender: str = Field(..., description="Remetente da mensagem: 'user' ou 'model'/'assistant'")
    text: str = Field(..., description="Conteúdo textual da mensagem")

class RetrievedSource(BaseModel):
    id: str = Field(..., description="Identificador único do trecho normativo (chunk) recuperado")
    source: str = Field(..., description="Nome formal da legislação ou manual consultado para citação")
    category: str = Field(..., description="Categoria temática: 'pavimentacao', 'drenagem', 'iluminacao', 'limpeza_urbana', 'manejo_arboreo', 'sinalizacao_transito', 'saneamento', 'direitos_cidadao'")
    title: str = Field(..., description="Título do tópico consultado")
    similarity_score: float = Field(..., description="Score de similaridade de cosseno (arredondado em 4 casas)")

class ChatRequest(BaseModel):
    pergunta: str = Field(..., description="Dúvida, relato ou consulta enviada pelo munícipe")
    chamadoContext: Optional[ChamadoContextPayload] = Field(default=None, description="Contexto do chamado ou ocorrência urbana ativa")
    foto_base64: Optional[str] = Field(default=None, description="Foto da ocorrência em formato Base64 para análise visual multimodal")
    historico: Optional[List[MensagemHistorico]] = Field(default=None, description="Histórico de mensagens recentes para memória conversacional")
    sessionId: Optional[str] = Field(default=None, description="Identificador único da sessão de chat")

class ChatResponse(BaseModel):
    resposta: str = Field(..., description="Resposta processada e sanitizada para visualização mobile no app")
    categoria: str = Field(default="zeladoria", description="Categoria urbana identificada")
    urgencia: str = Field(default="baixa", description="Classificação de urgência: 'baixa', 'media', 'alta', 'URGENTE'")
    acoes_recomendadas: Optional[List[str]] = Field(default=None, description="Orientações cívicas e procedimentos recomendados")
    origem_resposta: str = Field(default="ZelaBot (ZelaFix AI)", description="Identificador do mecanismo responsável pela geração da resposta")
    sessionId: Optional[str] = Field(default=None, description="Identificador da sessão ativa no banco de dados")
    sources_used: List[RetrievedSource] = Field(default_factory=list, description="Lista de trechos legais da base RAG utilizados")
    rag_grounded: bool = Field(default=False, description="Indica se a resposta foi fundamentada em decretos municipais via RAG")

class MensagemBancoItem(BaseModel):
    id: int = Field(..., description="ID sequencial da mensagem no SQLite")
    session_id: str = Field(..., description="ID da sessão")
    chamado_id: Optional[int] = Field(default=None, description="ID do chamado associado")
    sender: str = Field(..., description="Remetente: 'user' ou 'model'")
    text: str = Field(..., description="Conteúdo da mensagem")
    timestamp: Optional[str] = Field(default=None, description="Data/hora do registro")

class AuditoriaBancoItem(BaseModel):
    id: int = Field(..., description="ID sequencial da auditoria no SQLite")
    session_id: str = Field(..., description="ID da sessão")
    chamado_id: Optional[int] = Field(default=None, description="ID do chamado")
    bairro: Optional[str] = Field(default=None, description="Bairro da ocorrência")
    pergunta: str = Field(..., description="Pergunta ou relato de entrada")
    resposta: str = Field(..., description="Parecer técnico ou resposta gerada")
    categoria: str = Field(..., description="Categoria de zeladoria")
    urgencia: str = Field(..., description="Nível de urgência/prioridade")
    orgao_responsavel: Optional[str] = Field(default=None, description="Órgão municipal responsável")
    sla_horas: Optional[int] = Field(default=None, description="SLA regulamentar previsto em horas")
    origem_resposta: str = Field(..., description="Origem da resposta")
    timestamp: Optional[str] = Field(default=None, description="Data/hora do registro")

class HistoricoResponse(BaseModel):
    total: int = Field(..., description="Total de mensagens retornadas")
    mensagens: List[MensagemBancoItem] = Field(..., description="Lista de mensagens da sessão ou chamado")

class AuditoriaResponse(BaseModel):
    total: int = Field(..., description="Total de registros de auditoria retornados")
    auditorias: List[AuditoriaBancoItem] = Field(..., description="Lista de pareceres de triagem auditados")

class SessaoItem(BaseModel):
    session_id: str = Field(..., description="Identificador único da sessão de chat")
    titulo: str = Field(..., description="Título resumido da conversa (primeira pergunta do cidadão)")
    total_mensagens: int = Field(default=0, description="Total de mensagens trocadas na conversa")
    last_activity: Optional[str] = Field(default=None, description="Data e hora da última interação")

class SessoesResponse(BaseModel):
    total: int = Field(..., description="Total de sessões encontradas")
    sessoes: List[SessaoItem] = Field(..., description="Lista de sessões de conversas anteriores")
