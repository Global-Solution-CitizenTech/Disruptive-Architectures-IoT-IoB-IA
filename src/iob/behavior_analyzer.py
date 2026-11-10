"""
Módulo de Análise Comportamental Cidadã (IoB - Internet of Behaviors)
Avalia padrões de engajamento social, histórico de confiabilidade e apoio comunitário
"""

from typing import Dict, Any, Tuple
from ..config import IOB_MIN_COMMUNITY_SUPPORTS_URGENT, IOB_MIN_COMMUNITY_SUPPORTS_CRITICAL

class CitizenBehaviorAnalyzer:
    """
    Analisa os comportamentos dos cidadãos e o engajamento comunitário no ZelaFix:
    - Apoios comunitários (+1)
    - Histórico de assertividade do relator (reputação)
    - Concentração de relatos no mesmo raio geográfico
    - Cálculo do Social Urgency Score (SUS) [0.0 a 10.0]
    """

    @classmethod
    def evaluate_behavior(
        cls,
        community_supports: int = 0,
        author_reputation: float = 0.90,
        nearby_reports: int = 0
    ) -> Dict[str, Any]:
        """Calcula o índice de urgência comportamental e o ajuste de prioridade."""
        # 1. Componente de Apoio Coletivo (Peso 50%)
        # Normaliza apoios entre 0 e 5 pontos
        support_points = min(5.0, (community_supports / 30.0) * 5.0)

        # 2. Componente de Reputação do Usuário (Peso 25%)
        # Confiabilidade histórica do autor (evita contas fakes ou spam)
        rep_points = max(0.0, min(2.5, author_reputation * 2.5))

        # 3. Componente de Agrupamento Espacial / Densidade (Peso 25%)
        # Mais de um cidadão reportando o mesmo transtorno no raio de 200m
        density_points = min(2.5, (nearby_reports / 5.0) * 2.5)

        # Score Social Consolidado [0 a 10]
        social_urgency_score = round(support_points + rep_points + density_points, 2)

        # Regra de Ajuste Dinâmico Comunitário de Prioridade
        ajuste_prioridade = False
        prioridade_sugerida = None

        if community_supports >= IOB_MIN_COMMUNITY_SUPPORTS_CRITICAL or social_urgency_score >= 8.5:
            ajuste_prioridade = True
            prioridade_sugerida = "Crítica"
            nivel_engajamento = "Mobilização Comunitária Massiva (Prioridade Máxima)"
        elif community_supports >= IOB_MIN_COMMUNITY_SUPPORTS_URGENT or social_urgency_score >= 6.5:
            ajuste_prioridade = True
            prioridade_sugerida = "Alta"
            nivel_engajamento = "Forte Engajamento Local da Vizinhança"
        elif community_supports > 5:
            nivel_engajamento = "Engajamento Comunitário Moderado"
        else:
            nivel_engajamento = "Relato Individual Recém-Aberto"

        return {
            "social_urgency_score": social_urgency_score,
            "nivel_engajamento": nivel_engajamento,
            "reputacao_cidadao": round(author_reputation, 2),
            "apoios_count": community_supports,
            "relatos_proximos_count": nearby_reports,
            "ajuste_prioridade_comunitario": ajuste_prioridade,
            "prioridade_sugerida_iob": prioridade_sugerida
        }

