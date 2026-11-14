"""
Serviço de Triagem Urbana Inteligente, Enquadramento Normativo e Parecer Técnico — ZelaFix AI
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)
"""
import uuid
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from src.core.config import AI_EMBEDDING_MODEL
from src.core.prompts import SYSTEM_TRIAGEM, formatar_prompt_triagem
from src.schemas.insights import TriagemRequest, TriagemResponse
from src.services.knowledge_service import KnowledgeService
from src.services.foundry_service import FoundryService
from src.database.oracle_client import OracleClient
from src.repositories.chat_repository import ChatRepository
from src.utils.guardrails import sanitizar_lgpd
from src.utils.text import limpar_texto_mobile

logger = logging.getLogger("ZelaFixAI.TriagemService")

_ORDEM_PRIORIDADE = {"BAIXA": 1, "MEDIA": 2, "ALTA": 3, "URGENTE": 4}
_SLA_TETO_PRIORIDADE = {"URGENTE": 12, "ALTA": 24, "MEDIA": 48, "BAIXA": 72}


class _TriagemIaSchema(BaseModel):
    prioridade: str = "MEDIA"
    orgao_responsavel: str = "Subprefeitura Regional"
    sla_sugerido_horas: int = 48
    parecer_ia: str = "Ocorrência urbana triada para vistoria técnica pelo órgão competente."
    enquadramento_legal: str = "Carta de Serviços ao Cidadão PMSP / SP156"
    risco_potencial: str = "Risco urbano em avaliação técnica."
    checklist_vistoria: List[str] = Field(default_factory=list)
    analise_visual: Optional[str] = None


def _truncar_parecer_150(texto: str) -> str:
    limpo = limpar_texto_mobile(sanitizar_lgpd(texto)).strip()
    if len(limpo) <= 150:
        return limpo
    corte = limpo[:147].rsplit(" ", 1)[0].rstrip(" ,;:-")
    return f"{corte or limpo[:147]}..."


class TriagemService:
    """
    Motor de Triagem Urbana da ZelaFix:
    - Enriquece opcionalmente com Oracle FIAP (`SELECT` somente leitura).
    - Recupera legislação municipal via RAG Semântico (Azure AI Foundry Embeddings).
    - Emite laudo técnico estruturado (Structured Output + Visão Computacional).
    - Aplica invariantes IoB (+1 >= 25 apoios), telemetria IoT e limite de 150 chars.
    """

    @classmethod
    def _fallback_contingencia(
        cls,
        categoria: str,
        apoios: int,
        anomalia_iot: bool,
        chunks: List[Dict[str, Any]],
    ) -> _TriagemIaSchema:
        topo = chunks[0] if chunks else {}
        urg_rag = str(topo.get("urgency", "media")).upper()
        prioridade = urg_rag if urg_rag in _ORDEM_PRIORIDADE else "MEDIA"
        if (anomalia_iot or apoios >= 25) and _ORDEM_PRIORIDADE[prioridade] < 3:
            prioridade = "ALTA"

        sla_map = {"URGENTE": 12, "ALTA": 24, "MEDIA": 48, "BAIXA": 72}
        return _TriagemIaSchema(
            prioridade=prioridade,
            orgao_responsavel="Subprefeitura Regional / Órgão Municipal Competente",
            sla_sugerido_horas=sla_map[prioridade],
            parecer_ia=f"Ocorrência de {categoria} triada em contingência normativa ({apoios} apoios).",
            enquadramento_legal=f"{topo.get('source', 'PMSP / SP156')} — {topo.get('title', categoria)}".strip(" —"),
            risco_potencial="Necessita vistoria técnica presencial para confirmação em campo.",
            checklist_vistoria=[
                "Confirmar localização e segurança do perímetro urbano",
                "Registrar evidência fotográfica complementar para despacho",
                "Executar atendimento conforme SLA municipal aplicável",
            ],
            analise_visual=None,
        )

    @classmethod
    def realizar_triagem(cls, request: TriagemRequest) -> TriagemResponse:
        chamado = request.chamado
        session_id = request.sessionId or f"tria_{uuid.uuid4().hex[:12]}"

        try:
            dados_oracle = None
            if chamado.id:
                try:
                    dados_oracle = OracleClient.obter_chamado_completo(
                        chamado.id,
                        incluir_foto=not bool(chamado.foto_base64),
                    )
                except Exception as err_ora:
                    logger.warning(f"Consulta ao Oracle para chamado {chamado.id} falhou: {err_ora}")

            categoria_raw = sanitizar_lgpd(chamado.categoria or "Geral")
            titulo_raw = sanitizar_lgpd(chamado.titulo or "Relato de Zeladoria")
            descricao_raw = sanitizar_lgpd(chamado.descricao or "")
            bairro_raw = sanitizar_lgpd(chamado.bairro or "São Paulo - SP")
            apoios = max(0, chamado.apoios_comunitarios or 0)

            if dados_oracle:
                if (categoria_raw == "Geral" or not categoria_raw) and dados_oracle.get("categoria"):
                    categoria_raw = dados_oracle["categoria"]
                if (titulo_raw == "Relato de Zeladoria" or not titulo_raw) and dados_oracle.get("titulo"):
                    titulo_raw = dados_oracle["titulo"]
                if not descricao_raw and dados_oracle.get("descricao"):
                    descricao_raw = sanitizar_lgpd(dados_oracle["descricao"])
                if (bairro_raw == "São Paulo - SP" or not bairro_raw) and dados_oracle.get("bairro"):
                    bairro_raw = dados_oracle["bairro"]
                if apoios == 0 and dados_oracle.get("apoios_comunitarios"):
                    apoios = dados_oracle["apoios_comunitarios"]

            telemetria = chamado.telemetria_iot
            anomalia_iot = bool(telemetria and telemetria.anomalia_detectada)
            telemetria_str = ""
            if telemetria:
                telemetria_str = (
                    f"Sensor {telemetria.device_id or 'IoT'} ({telemetria.tipo_sensor or 'urbano'}): "
                    f"{telemetria.valor_medido if telemetria.valor_medido is not None else 'N/D'} "
                    f"{telemetria.unidade or ''} | Anomalia na borda: {'SIM' if anomalia_iot else 'NÃO'}"
                ).strip()

            # 1. RAG Semântico (Azure AI Foundry Embeddings + ChromaDB)
            texto_busca = f"{categoria_raw} {titulo_raw} {descricao_raw}".strip()
            chunks = KnowledgeService.buscar_chunks_rag(texto_busca, top_k=3).get("chunks", [])

            # 2. Inferência Estruturada Multimodal via Azure AI Foundry
            foto_input = chamado.foto_base64 or (dados_oracle.get("foto_bytes") if dados_oracle else None)
            prompt_triagem = formatar_prompt_triagem(
                categoria=categoria_raw,
                titulo=titulo_raw,
                descricao=descricao_raw,
                bairro=bairro_raw,
                apoios=apoios,
                chunks_recuperados=chunks,
                telemetria_str=telemetria_str,
                possui_imagem=bool(foto_input),
            )

            laudo, modelo_usado = FoundryService.gerar_estruturado(
                schema_cls=_TriagemIaSchema,
                system_prompt=SYSTEM_TRIAGEM,
                user_prompt=prompt_triagem,
                imagem_base64=foto_input,
            )

            if laudo is not None:
                origem_triagem = f"ZelaFix AI Triagem Multimodal (Azure AI Foundry: {modelo_usado} + {AI_EMBEDDING_MODEL})"
            else:
                laudo = cls._fallback_contingencia(categoria_raw, apoios, anomalia_iot, chunks)
                origem_triagem = "ZelaFix AI Triagem (Contingência Normativa)"

            # 3. Invariantes operacionais (Piso normativo RAG / IoB / IoT / limite 150 chars / LGPD)
            prioridade = laudo.prioridade.upper().strip()
            if prioridade not in _ORDEM_PRIORIDADE:
                prioridade = "MEDIA"
            if chunks and float(chunks[0].get("similarity_score", 0.0)) >= 0.45:
                urg_norma = str(chunks[0].get("urgency", "")).upper().strip()
                if urg_norma in _ORDEM_PRIORIDADE and _ORDEM_PRIORIDADE[prioridade] < _ORDEM_PRIORIDADE[urg_norma]:
                    prioridade = urg_norma
            if (anomalia_iot or apoios >= 25) and _ORDEM_PRIORIDADE[prioridade] < 3:
                prioridade = "ALTA"

            sla_raw = int(laudo.sla_sugerido_horas or _SLA_TETO_PRIORIDADE[prioridade])
            sla_horas = max(1, min(sla_raw, _SLA_TETO_PRIORIDADE[prioridade]))
            parecer_ia = _truncar_parecer_150(laudo.parecer_ia)
            orgao = sanitizar_lgpd(limpar_texto_mobile(laudo.orgao_responsavel)) or "Subprefeitura Regional"
            enquadramento = sanitizar_lgpd(limpar_texto_mobile(laudo.enquadramento_legal))
            risco = sanitizar_lgpd(limpar_texto_mobile(laudo.risco_potencial))
            checklist = [
                limpar_texto_mobile(sanitizar_lgpd(item))
                for item in laudo.checklist_vistoria
                if item and item.strip()
            ][:3]

            analise_visual: Optional[str] = None
            if foto_input and laudo.analise_visual and laudo.analise_visual.strip().lower() != "null":
                analise_visual = limpar_texto_mobile(sanitizar_lgpd(laudo.analise_visual))

            ChatRepository.salvar_triagem_audit(
                session_id=session_id,
                chamado_id=chamado.id,
                bairro=bairro_raw,
                titulo=titulo_raw,
                parecer_ia=parecer_ia,
                categoria=categoria_raw,
                prioridade=prioridade,
                orgao_responsavel=orgao,
                sla_horas=sla_horas,
                origem_triagem=origem_triagem,
            )

            return TriagemResponse(
                prioridade=prioridade,
                orgao_responsavel=orgao,
                parecer_ia=parecer_ia,
                sla_sugerido_horas=sla_horas,
                enquadramento_legal=enquadramento,
                risco_potencial=risco,
                checklist_vistoria=checklist,
                analise_visual=analise_visual,
                origem_triagem=origem_triagem,
            )
        except Exception as err:
            logger.error(f"Erro na TriagemService: {err}")
            return TriagemResponse(
                prioridade="MEDIA",
                orgao_responsavel="Subprefeitura Regional / PMSP",
                parecer_ia="Ocorrência encaminhada para vistoria técnica da Subprefeitura.",
                sla_sugerido_horas=48,
                enquadramento_legal="Carta de Serviços PMSP / SP156",
                risco_potencial="Impacto moderado em avaliação técnica.",
                checklist_vistoria=["Vistoriar local", "Confirmar competência", "Registrar conclusão"],
                origem_triagem="ZelaFix AI Triagem (Contingência)",
            )
