"""
Rotas RESTful da API ZelaFix IA & IoT
Compatíveis com os endpoints consumidos pelo ZelaFix Mobile e Spring Boot
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from ..schemas.chamado_ia import (
    TriagemRequestDTO,
    TriagemResponseDTO,
    ChatCidadaoRequestDTO,
    ChatCidadaoResponseDTO
)
from ..schemas.cv_models import ImageAnalysisRequest, ImageAnalysisResponse
from ..schemas.rag_models import RagQueryRequest, RagQueryResponse
from ..schemas.iot_models import IotTelemetryPayload, IotAnalysisResult
from ..services.triagem_service import TriagemService
from ..services.chat_service import ChatCidadaoService
from ..cv.classifier import UrbanCVClassifier
from ..rag.knowledge_retriever import KnowledgeRetriever
from ..iot.sensor_processor import UrbanSensorProcessor
from ..iob.behavior_analyzer import CitizenBehaviorAnalyzer
from ..config import PROJECT_NAME, PROJECT_VERSION, ODS_TARGET

router = APIRouter()

# Instâncias singleton para reuso em memória
_triagem_service = TriagemService()
_cv_classifier = UrbanCVClassifier()
_rag_retriever = KnowledgeRetriever()
_chat_service = ChatCidadaoService(retriever=_rag_retriever)

def get_triagem_service() -> TriagemService:
    return _triagem_service

def get_chat_service() -> ChatCidadaoService:
    return _chat_service

def get_cv_classifier() -> UrbanCVClassifier:
    return _cv_classifier

def get_rag_retriever() -> KnowledgeRetriever:
    return _rag_retriever

@router.post(
    "/api/v1/triagem-ia/analisar",
    response_model=TriagemResponseDTO,
    summary="Triagem Inteligente Multimodal Completa (ZelaFix Mobile Endpoint)",
    tags=["Triagem IA"]
)
def analisar_chamado(
    request: TriagemRequestDTO,
    service: TriagemService = Depends(get_triagem_service)
):
    """
    Endpoint principal consumido pelo aplicativo ZelaFix Mobile.
    Realiza a fusão entre:
    1. Análise Visual da Evidência Fotográfica (Visão Computacional / Deep Learning)
    2. Base Normativa Municipal Oficial da Cidade de SP (RAG)
    3. Telemetria de Sensores Físicos Urbanos (IoT)
    4. Análise de Mobilização Social e Engajamento da Vizinhança (IoB)
    5. Geração de Laudo Técnico Circunstanciado (IA Generativa Google Gemini / Engine Local)
    """
    try:
        resultado = service.processar_triagem(request)
        return resultado
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Falha no processamento da Triagem Inteligente: {str(e)}"
        )

@router.post(
    "/api/v1/cv/analisar-imagem",
    response_model=ImageAnalysisResponse,
    summary="Análise Isolada de Imagem Urbana (Visão Computacional)",
    tags=["Aprofundamento 1: Visão Computacional"]
)
def analisar_imagem(
    request: ImageAnalysisRequest,
    cv: UrbanCVClassifier = Depends(get_cv_classifier)
):
    """Executa a extração de features espectrais e classificação supervisionada da imagem."""
    try:
        return cv.analyze_image(
            image_base64=request.image_base64,
            image_url=request.image_url,
            categoria_declarada=request.categoria_declarada
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao processar imagem: {str(e)}")

@router.post(
    "/api/v1/rag/consultar",
    response_model=RagQueryResponse,
    summary="Consulta Semântica à Base Regulatória Municipal (RAG)",
    tags=["Aprofundamento 2: RAG Básico"]
)
def consultar_rag(
    request: RagQueryRequest,
    rag: KnowledgeRetriever = Depends(get_rag_retriever)
):
    """Realiza busca vetorial nos decretos e manuais técnicos de zeladoria da Prefeitura de SP."""
    try:
        return rag.query(
            query_text=request.query,
            categoria=request.categoria,
            top_k=request.top_k
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na consulta RAG: {str(e)}")

@router.post(
    "/api/v1/iot/telemetria",
    response_model=IotAnalysisResult,
    summary="Ingestão de Telemetria de Sensores Urbanos Conectados (IoT)",
    tags=["Arquitetura Disruptiva: IoT"]
)
def processar_telemetria_iot(payload: IotTelemetryPayload):
    """Analisa telemetrias de acelerômetros viários, sensores de nível de bueiro ou luminárias LED."""
    try:
        return UrbanSensorProcessor.evaluate_telemetry(payload.model_dump())
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao analisar telemetria IoT: {str(e)}")

@router.post(
    "/api/v1/iob/analise-comportamental",
    summary="Análise de Urgência Social e Comportamento Comunitário (IoB)",
    tags=["Arquitetura Disruptiva: IoB"]
)
def calcular_iob(dados: Dict[str, Any]):
    """Calcula o Social Urgency Score (SUS) e reputação comunitária."""
    apoios = int(dados.get("apoiosCount", 0))
    reputacao = float(dados.get("authorReputation", 0.92))
    relatos_prox = int(dados.get("nearbyReports", 0))
    return CitizenBehaviorAnalyzer.evaluate_behavior(
        community_supports=apoios,
        author_reputation=reputacao,
        nearby_reports=relatos_prox
    )

@router.post(
    "/api/v1/chat-cidadao",
    response_model=ChatCidadaoResponseDTO,
    summary="Chat Cidadão Inteligente RAG (ZelaBot Mobile)",
    tags=["Chat Cidadão IA"]
)
def chat_cidadao(
    request: ChatCidadaoRequestDTO,
    chat_svc: ChatCidadaoService = Depends(get_chat_service)
):
    """
    Endpoint conversacional para o morador tirar dúvidas no app ZelaFix Mobile.
    Utiliza RAG sobre a legislação municipal e oferece auxílio na abertura de chamados.
    """
    try:
        return chat_svc.responder_cidadao(request)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar mensagem do cidadão: {str(e)}"
        )

@router.get("/health", tags=["Monitoramento"])
@router.get("/actuator/health", tags=["Monitoramento"])
def health_check():
    """Endpoint de verificação de integridade operacional compatível com Spring Boot Actuator."""
    return {
        "status": "UP",
        "service": PROJECT_NAME,
        "version": PROJECT_VERSION,
        "alignment": ODS_TARGET,
        "components": {
            "computerVision": "UP",
            "ragVectorStore": "UP",
            "genAiClient": "UP",
            "iotSensorProcessor": "UP",
            "iobBehaviorAnalyzer": "UP"
        }
    }

@router.get("/api/v1/meta", tags=["Metadados FIAP"])
def get_metadata():
    """Metadados de auditoria e identificação da equipe FIAP."""
    return {
        "projeto": "ZelaFix - Zeladoria Urbana Inteligente",
        "disciplina": "Disruptive Architectures: IoT, IoB & Generative IA",
        "edital": "FIAP Global Solution 2026/2 - CitizenTech",
        "turma": "2TDSPG",
        "equipe": [
            {"nome": "Enzo Okuizumi", "rm": "561432", "funcao": "Mobile Developer & Arquiteto React Native"},
            {"nome": "Gustavo Okada", "rm": "563428", "funcao": "Backend Developer & API Integration"},
            {"nome": "Lucas Barros Gouveia", "rm": "566422", "funcao": "Fullstack Developer & Database Architect"},
            {"nome": "Luna de Carvalho Guimarães", "rm": "562290", "funcao": "UI/UX Designer & Mobile Frontend Specialist"},
            {"nome": "Milton Marcelino", "rm": "564836", "funcao": "DevOps & Quality Assurance (QA)"}
        ]
    }

