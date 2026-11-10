"""
Testes Unitários de Análise Comportamental Comunitária (IoB - Internet of Behaviors)
"""

from src.iob.behavior_analyzer import CitizenBehaviorAnalyzer

def test_community_mobilization_escalation_critical():
    # 35 apoios comunitários -> deve elevar para Crítica
    result = CitizenBehaviorAnalyzer.evaluate_behavior(
        community_supports=35,
        author_reputation=0.95,
        nearby_reports=3
    )
    assert result["ajuste_prioridade_comunitario"] is True
    assert result["prioridade_sugerida_iob"] == "Crítica"
    assert result["social_urgency_score"] >= 7.5

def test_community_mobilization_escalation_urgent():
    # 18 apoios comunitários -> deve elevar para Alta
    result = CitizenBehaviorAnalyzer.evaluate_behavior(
        community_supports=18,
        author_reputation=0.90,
        nearby_reports=1
    )
    assert result["ajuste_prioridade_comunitario"] is True
    assert result["prioridade_sugerida_iob"] == "Alta"

def test_low_engagement_single_report():
    # 1 apoio apenas
    result = CitizenBehaviorAnalyzer.evaluate_behavior(
        community_supports=1,
        author_reputation=0.85,
        nearby_reports=0
    )
    assert result["ajuste_prioridade_comunitario"] is False
    assert result["social_urgency_score"] < 4.0

