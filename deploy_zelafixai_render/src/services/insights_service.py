"""
Serviço de Insights Preventivos e Alertas Comunitários Urbanos — ZelaFix AI
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)
"""
import json
import logging
from typing import List, Optional
from pydantic import BaseModel, Field

from src.core.prompts import SYSTEM_INSIGHTS
from src.schemas.insights import InsightItem, InsightsResponse
from src.database.oracle_client import OracleClient
from src.repositories.chat_repository import ChatRepository
from src.services.knowledge_service import KnowledgeService
from src.services.foundry_service import FoundryService
from src.utils.guardrails import sanitizar_lgpd
from src.utils.text import limpar_texto_mobile

logger = logging.getLogger("ZelaFixAI.InsightsService")

_EIXOS_VALIDOS = {"pavimentacao", "drenagem", "iluminacao", "limpeza_urbana", "seguranca"}
_URGENCIAS_VALIDAS = {"baixa", "media", "alta"}


class _InsightsIaSchema(BaseModel):
    insights: List[InsightItem] = Field(default_factory=list)


class InsightsService:
    """
    Combina consultas em tempo real ao Oracle FIAP (somente SELECT), auditorias SQLite
    e RAG normativo PMSP para sintetizar alertas comunitários via Azure AI Foundry.
    """

    @classmethod
    def gerar_insights_bairro(cls, bairro: Optional[str] = None) -> InsightsResponse:
        bairro_filtro = bairro.strip() if bairro and bairro.strip() else None
        bairro_nome = bairro_filtro or "Geral / São Paulo"

        resumo = {}
        recentes = []
        auditorias = []

        try:
            resumo = OracleClient.resumo_estatistico_bairro(bairro=bairro_filtro)
            recentes = OracleClient.listar_chamados_recentes(limit=4, bairro=bairro_filtro)
        except Exception as err:
            logger.warning(f"InsightsService sem leitura Oracle: {err}")

        try:
            auditorias = ChatRepository.listar_auditorias(bairro=bairro_filtro, limit=4)
        except Exception as err_sql:
            logger.warning(f"InsightsService sem auditorias SQLite: {err_sql}")

        chunks_rag = KnowledgeService.buscar_chunks_rag(
            f"prevencao zeladoria urbana alagamento iluminacao ecoponto {bairro_nome}", top_k=2
        ).get("chunks", [])

        contexto = {
            "bairro": bairro_nome,
            "oracle_resumo": resumo,
            "chamados_recentes": [
                {k: c.get(k) for k in ("id", "titulo", "categoria", "status", "bairro", "votos")}
                for c in recentes
            ],
            "auditorias_recentes": [
                {k: a.get(k) for k in ("categoria", "urgencia", "bairro", "resposta")}
                for a in auditorias
            ],
            "normas_rag": [{"title": c["title"], "source": c["source"]} for c in chunks_rag],
        }

        prompt = sanitizar_lgpd(
            "Gere 3 a 4 insights preventivos objetivos para o cidadão e a gestão urbana "
            f"com base nos dados reais abaixo:\n{json.dumps(contexto, ensure_ascii=False)}"
        )

        ia_resp, _ = FoundryService.gerar_estruturado(
            schema_cls=_InsightsIaSchema,
            system_prompt=SYSTEM_INSIGHTS,
            user_prompt=prompt,
            max_tokens=1100,
        )

        insights: List[InsightItem] = []
        if ia_resp and ia_resp.insights:
            for item in ia_resp.insights[:4]:
                cat = item.categoria.strip().lower()
                urg = item.urgencia.strip().lower()
                insights.append(
                    InsightItem(
                        categoria=cat if cat in _EIXOS_VALIDOS else "seguranca",
                        titulo=limpar_texto_mobile(sanitizar_lgpd(item.titulo))[:90],
                        descricao=limpar_texto_mobile(sanitizar_lgpd(item.descricao)),
                        urgencia=urg if urg in _URGENCIAS_VALIDAS else "media",
                    )
                )

        # Fallback determinístico usando exclusivamente dados reais / base cidadã
        if not insights:
            if resumo.get("oracle_online") and resumo.get("total_chamados", 0) > 0:
                por_cat = resumo.get("por_categoria") or {}
                top_cat, top_qtd = next(iter(por_cat.items()), ("Zeladoria", 1))
                insights.append(
                    InsightItem(
                        categoria="seguranca",
                        titulo=f"Panorama Oracle: {resumo['total_chamados']} chamado(s) em {bairro_nome}",
                        descricao=f"Destaque para '{top_cat}' ({top_qtd} registro(s)), somando {resumo.get('total_votos', 0)} apoio(s) (+1).",
                        urgencia="alta" if resumo.get("total_votos", 0) >= 25 else "media",
                    )
                )
            for ch in recentes[:2]:
                insights.append(
                    InsightItem(
                        categoria="seguranca",
                        titulo=f"Chamado #{ch['id']} ({ch['status']}): {ch['categoria']}",
                        descricao=sanitizar_lgpd(f"'{ch['titulo']}' em {ch['bairro']} ({ch.get('votos', 0)} apoios)."),
                        urgencia="alta" if int(ch.get("votos") or 0) >= 25 else "media",
                    )
                )
            if len(insights) < 3:
                insights.extend([
                    InsightItem(
                        categoria="drenagem",
                        titulo="Prevenção de Alagamentos e Bocas de Lobo",
                        descricao=f"Em {bairro_nome}, registre bueiros obstruídos no ZelaFix para hidrojateamento preventivo (SLA até 48h).",
                        urgencia="media",
                    ),
                    InsightItem(
                        categoria="limpeza_urbana",
                        titulo="Descarte Gratuito em Ecopontos (Lei 13.478/02)",
                        descricao="Descarte até 1 m³/dia de entulho ou móveis gratuitamente nos Ecopontos municipais.",
                        urgencia="baixa",
                    ),
                    InsightItem(
                        categoria="iluminacao",
                        titulo="Pontos Escuros e Iluminação LED",
                        descricao="Postes apagados devem ser reportados para manutenção pela Ilumina SP em 24h a 48h.",
                        urgencia="baixa",
                    ),
                ])
                insights = insights[:4]

        return InsightsResponse(
            bairro=bairro_nome,
            total_alertas=len(insights),
            insights=insights,
        )
