"""
Serviço de Insights Preventivos e Alertas Comunitários Urbanos — ZelaFix AI
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)
"""
import logging
from typing import List, Optional
from src.schemas.insights import InsightItem, InsightsResponse

logger = logging.getLogger("ZelaFixAI.InsightsService")

class InsightsService:
    """
    Gera diagnósticos e recomendações preventivas de zeladoria para munícipes e bairros,
    estimulando a cidadania ativa e prevenção de desastres urbanos (ODS 11).
    """

    @classmethod
    def gerar_insights_bairro(cls, bairro: Optional[str] = None) -> InsightsResponse:
        bairro_nome = (bairro or "Geral / São Paulo").strip()

        insights: List[InsightItem] = [
            InsightItem(
                categoria="drenagem",
                titulo="Prevenção de Alagamentos e Limpeza de Bocas de Lobo",
                descricao=f"No período chuvoso em {bairro_nome}, evite varrer folhas ou sacos plásticos para sarjetas. Caso note bueiros com água estagnada ou grelhas tampadas por entulho, abra um chamado no ZelaFix para acionamento de hidrojateamento preventivo.",
                urgencia="media"
            ),
            InsightItem(
                categoria="limpeza_urbana",
                titulo="Descarte Consciente e Ecoponto Gratuito",
                descricao="Munícipes podem descartar gratuitamente até 1 m³ de sobras de obras e madeiras por dia nos Ecopontos da região. Lembre-se que o descarte clandestino em calçadas gera multa municipal gravíssima superior a R$ 25.000,00.",
                urgencia="baixa"
            ),
            InsightItem(
                categoria="iluminacao",
                titulo="Ronda Noturna e Segurança Pública em Pontos de Ônibus",
                descricao=f"Luminárias LED com oscilação ou postes apagados em vias de pedestres em {bairro_nome} têm prioridade regulamentar de substituição pelo consórcio Ilumina SP em até 24h a 48h.",
                urgencia="baixa"
            ),
            InsightItem(
                categoria="seguranca",
                titulo="Mobilização Comunitária (+1 Morador)",
                descricao="Ocorrências com mais de 25 apoios da vizinhança são promovidas para a fila de alta prioridade técnica da Subprefeitura. Compartilhe os chamados do seu bairro com os vizinhos no ZelaFix!",
                urgencia="baixa"
            )
        ]

        return InsightsResponse(
            bairro=bairro_nome,
            total_alertas=len(insights),
            insights=insights
        )
