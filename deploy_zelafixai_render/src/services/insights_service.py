"""
Serviço de Insights Preventivos e Alertas Comunitários Urbanos — ZelaFix AI
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)
"""
import logging
from typing import List, Optional
from src.schemas.insights import InsightItem, InsightsResponse
from src.database.oracle_client import OracleClient
from src.repositories.chat_repository import ChatRepository
from src.utils.text import normalizar_texto

logger = logging.getLogger("ZelaFixAI.InsightsService")


class InsightsService:
    """
    Gera diagnósticos vivos combinando dados reais (somente leitura) do Oracle FIAP,
    triagens recentes do SQLite e alertas preventivos de zeladoria (ODS 11).
    """

    @staticmethod
    def _normalizar_eixo(categoria_raw: str) -> str:
        norm = normalizar_texto(categoria_raw)
        if any(k in norm for k in ["iluminacao", "poste", "luz"]):
            return "iluminacao"
        if any(k in norm for k in ["drenagem", "bueiro", "enchente", "alagamento"]):
            return "drenagem"
        if any(k in norm for k in ["paviment", "buraco", "via", "asfalto"]):
            return "pavimentacao"
        if any(k in norm for k in ["limpeza", "lixo", "entulho", "ecoponto"]):
            return "limpeza_urbana"
        return "seguranca"

    @classmethod
    def gerar_insights_bairro(cls, bairro: Optional[str] = None) -> InsightsResponse:
        bairro_filtro = bairro.strip() if bairro and bairro.strip() else None
        bairro_nome = bairro_filtro or "Geral / São Paulo"
        insights: List[InsightItem] = []
        eixos_usados = set()

        # 1. Consulta em tempo real (somente SELECT) ao banco Oracle FIAP
        try:
            resumo = OracleClient.resumo_estatistico_bairro(bairro=bairro_filtro)
            recentes = OracleClient.listar_chamados_recentes(limit=4, bairro=bairro_filtro)

            if resumo.get("oracle_online") and resumo.get("total_chamados", 0) > 0:
                por_cat = resumo.get("por_categoria") or {}
                top_cat, top_qtd = next(iter(por_cat.items()), ("Zeladoria", 1))
                eixo_top = cls._normalizar_eixo(top_cat)
                eixos_usados.add(eixo_top)
                total_ch = resumo["total_chamados"]
                total_vt = resumo.get("total_votos", 0)

                insights.append(InsightItem(
                    categoria=eixo_top,
                    titulo=f"Panorama Oracle: {total_ch} chamado(s) ativo(s) em {bairro_nome}",
                    descricao=(
                        f"Na base oficial FIAP há {total_ch} ocorrência(s) em {bairro_nome} somando {total_vt} apoio(s) (+1), "
                        f"com destaque para '{top_cat}' ({top_qtd} registro(s))."
                    ),
                    urgencia="alta" if (top_qtd >= 3 or total_vt >= 25) else "media",
                ))

            for ch in recentes[:2]:
                eixo = cls._normalizar_eixo(ch.get("categoria", ""))
                eixos_usados.add(eixo)
                votos = int(ch.get("votos") or 0)
                insights.append(InsightItem(
                    categoria=eixo,
                    titulo=f"Chamado #{ch['id']} ({ch['status']}): {ch['categoria']}",
                    descricao=(
                        f"'{ch['titulo']}' em {ch['bairro']} "
                        f"(aberto em {ch.get('dt_abertura') or 'data recente'}, {votos} apoio(s) comunitário(s))."
                    ),
                    urgencia="alta" if votos >= 25 else "media",
                ))
        except Exception as err:
            logger.warning(f"InsightsService operando sem leitura Oracle: {err}")

        # 2. Auditorias urgentes/altas recentes do SQLite local
        try:
            auditorias = ChatRepository.listar_auditorias(bairro=bairro_filtro, limit=4)
            for aud in auditorias:
                urg = str(aud.get("urgencia") or "").upper()
                if urg in {"URGENTE", "ALTA"} and len(insights) < 4:
                    eixo = cls._normalizar_eixo(aud.get("categoria", ""))
                    if eixo not in eixos_usados:
                        eixos_usados.add(eixo)
                        insights.append(InsightItem(
                            categoria=eixo,
                            titulo=f"Alerta de Triagem ({urg}): {aud.get('categoria')}",
                            descricao=f"Monitoramento recente em {aud.get('bairro') or bairro_nome}: {aud.get('resposta')}",
                            urgencia="alta" if urg == "URGENTE" else "media",
                        ))
        except Exception as err_sql:
            logger.warning(f"Erro ao ler auditorias no InsightsService: {err_sql}")

        # 3. Recomendações preventivas complementares (garante sempre base cidadã ODS 11)
        preventivos = [
            InsightItem(
                categoria="drenagem",
                titulo="Prevenção de Alagamentos e Limpeza de Bocas de Lobo",
                descricao=f"Em períodos de chuva em {bairro_nome}, evite varrer folhas para sarjetas e registre bueiros obstruídos no ZelaFix para hidrojateamento preventivo.",
                urgencia="media",
            ),
            InsightItem(
                categoria="limpeza_urbana",
                titulo="Descarte Consciente e Ecoponto Gratuito",
                descricao="Munícipes podem descartar gratuitamente até 1 m³/dia de entulho e móveis nos Ecopontos (Lei nº 13.478/2002), evitando multas por descarte irregular.",
                urgencia="baixa",
            ),
            InsightItem(
                categoria="iluminacao",
                titulo="Ronda Noturna e Pontos Escuros (Ilumina SP)",
                descricao=f"Postes apagados em {bairro_nome} possuem prazo regulamentar de substituição de 24h a 48h pelo consórcio Ilumina SP.",
                urgencia="baixa",
            ),
            InsightItem(
                categoria="seguranca",
                titulo="Mobilização Comunitária (+1 Morador)",
                descricao="Chamados com 25 ou mais apoios comunitários sobem automaticamente para alta prioridade técnica na Subprefeitura.",
                urgencia="baixa",
            ),
        ]

        for item in preventivos:
            if len(insights) >= 4:
                break
            if item.categoria not in eixos_usados:
                eixos_usados.add(item.categoria)
                insights.append(item)

        return InsightsResponse(
            bairro=bairro_nome,
            total_alertas=len(insights),
            insights=insights,
        )
