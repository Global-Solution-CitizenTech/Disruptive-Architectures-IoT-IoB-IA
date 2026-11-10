"""
Serviço Central de Triagem Inteligente de Zeladoria Urbana (Orquestrador)
Integra Visão Computacional, RAG Normativo, Sensores IoT, Análise IoB e GenAI
"""

from typing import Optional, Dict, Any
from ..cv.classifier import UrbanCVClassifier
from ..rag.knowledge_retriever import KnowledgeRetriever
from ..iot.sensor_processor import UrbanSensorProcessor
from ..iob.behavior_analyzer import CitizenBehaviorAnalyzer
from ..genai.gemini_client import GeminiClient
from ..schemas.chamado_ia import (
    TriagemRequestDTO,
    TriagemResponseDTO,
    AnaliseVisualResumo,
    RagEvidenciaResumo,
    IotResumo,
    IobResumo
)

class TriagemService:
    """Orquestrador de ponta a ponta da solução de IA e IoT para Zeladoria Urbana."""

    def __init__(
        self,
        cv_classifier: Optional[UrbanCVClassifier] = None,
        knowledge_retriever: Optional[KnowledgeRetriever] = None,
        sensor_processor: Optional[UrbanSensorProcessor] = None,
        behavior_analyzer: Optional[CitizenBehaviorAnalyzer] = None,
        gemini_client: Optional[GeminiClient] = None
    ):
        self.cv = cv_classifier or UrbanCVClassifier()
        self.rag = knowledge_retriever or KnowledgeRetriever()
        self.iot = sensor_processor or UrbanSensorProcessor()
        self.iob = behavior_analyzer or CitizenBehaviorAnalyzer()
        self.genai = gemini_client or GeminiClient()

    def processar_triagem(self, req: TriagemRequestDTO) -> TriagemResponseDTO:
        """Executa a triagem completa multimodal com fusão sensorial e análise comportamental."""
        
        # 1. Etapa de Visão Computacional (Deep Learning / Feature Extraction)
        cv_result = self.cv.analyze_image(
            image_base64=req.imageBase64,
            image_url=req.fotoUrl,
            categoria_declarada=req.categoria
        )
        
        analise_visual_dto = AnaliseVisualResumo(
            categoriaDetectada=cv_result.predicted_category,
            confiancaScore=cv_result.confidence,
            severidadeVisual=cv_result.visual_severity,
            caracteristicasExtraidas=cv_result.features.model_dump()
        )

        # Categoria de trabalho consolidada (pondera a visão com o relato)
        categoria_efetiva = req.categoria
        if cv_result.confidence > 0.85 and cv_result.predicted_category != "Outros":
            categoria_efetiva = cv_result.predicted_category

        # 2. Etapa de Recuperação Aumentada por Geração (RAG Básico)
        rag_context, rag_chunks, rag_meta = self.rag.retrieve_context(
            titulo=req.titulo,
            descricao=req.descricao,
            categoria=categoria_efetiva,
            top_k=3
        )

        evidencias_rag_dto = [
            RagEvidenciaResumo(
                documentoFonte=chk.source_file,
                trechoRelevante=chk.content[:250] + ("..." if len(chk.content) > 250 else ""),
                artigoOuNorma=chk.law_article or "Norma Municipal PMSP",
                similaridadeScore=chk.similarity_score
            )
            for chk in rag_chunks
        ]

        # 3. Etapa de Sensores Urbanos Inteligentes (IoT)
        iot_dto = None
        iot_dict = {"sensorPresente": False, "anomaliaDetectada": False}
        if req.telemetriaIot:
            iot_analysis = self.iot.evaluate_telemetry(req.telemetriaIot)
            iot_dict = {
                "sensorPresente": True,
                "tipoSensor": req.telemetriaIot.get("device_type", "urban_sensor"),
                "anomaliaDetectada": iot_analysis.anomaly_detected,
                "detalhesLeitura": iot_analysis.details
            }
            iot_dto = IotResumo(
                sensorPresente=True,
                tipoSensor=req.telemetriaIot.get("device_type"),
                anomaliaDetectada=iot_analysis.anomaly_detected,
                detalhesLeitura=iot_analysis.details
            )
        else:
            iot_dto = IotResumo(
                sensorPresente=False,
                tipoSensor=None,
                anomaliaDetectada=False,
                detalhesLeitura={"status": "Sensor não instalado nesta coordenada"}
            )

        # 4. Etapa de Análise Comportamental e Engajamento Social (IoB)
        iob_data = self.iob.evaluate_behavior(
            community_supports=req.apoiosCount or 0,
            author_reputation=0.92,
            nearby_reports=1 if req.apoiosCount and req.apoiosCount > 10 else 0
        )
        iob_dto = IobResumo(
            socialUrgencyScore=iob_data["social_urgency_score"],
            nivelEngajamento=iob_data["nivel_engajamento"],
            reputacaoCidadao=iob_data["reputacao_cidadao"],
            ajustePrioridadeComunitario=iob_data["ajuste_prioridade_comunitario"]
        )

        # 5. Etapa de Síntese por IA Generativa (Google Gemini ou Motor Heurístico de Alta Fidelidade)
        laudo_genai, provider_name = self.genai.generate_triagem_opinion(
            titulo=req.titulo,
            descricao=req.descricao,
            categoria=categoria_efetiva,
            analise_visual=analise_visual_dto.model_dump(),
            rag_context=rag_context,
            rag_metadata=rag_meta,
            telemetria_iot=iot_dict,
            analise_iob=iob_data,
            localizacao=req.localizacao.model_dump() if req.localizacao else None
        )

        # 6. Consolidação Final com Garantia de Contrato para o App Mobile
        prioridade_final = laudo_genai.get("prioridade", "Alta")
        if iob_data.get("ajuste_prioridade_comunitario") and iob_data.get("prioridade_sugerida_iob") == "Crítica":
            prioridade_final = "Crítica"

        orgao_final = laudo_genai.get("orgaoResponsavel") or rag_meta.get("orgao_competente") or "Subprefeitura Local"
        parecer_final = laudo_genai.get("parecerIa") or "Parecer de Triagem Concluído com Sucesso."

        return TriagemResponseDTO(
            prioridade=prioridade_final,
            orgaoResponsavel=orgao_final,
            parecerIa=parecer_final,
            slaSugeridoHoras=int(laudo_genai.get("slaSugeridoHoras", 48)),
            enquadramentoLegal=laudo_genai.get("enquadramentoLegal", rag_meta.get("base_legal", "Decreto Municipal de Zeladoria")),
            riscoPotencial=laudo_genai.get("riscoPotencial", "Risco viário e urbano avaliado"),
            checklistVistoria=laudo_genai.get("checklistVistoria", ["Vistoria técnica de campo"]),
            analiseVisual=analise_visual_dto,
            evidenciasRag=evidencias_rag_dto,
            telemetriaIot=iot_dto,
            analiseIob=iob_dto,
            provedorGenAi=provider_name,
            statusExecucao="SUCESSO"
        )

