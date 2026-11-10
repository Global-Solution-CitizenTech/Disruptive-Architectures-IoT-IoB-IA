"""
Testes Unitários do Módulo de IA Generativa
"""

from src.genai.gemini_client import GeminiClient
from src.genai.prompt_templates import build_triagem_user_prompt

def test_prompt_builder_structure():
    prompt = build_triagem_user_prompt(
        titulo="Vazamento na sarjeta",
        descricao="Cano quebrado vertendo água limpa",
        categoria="Vazamento de Água",
        analise_visual={"categoriaDetectada": "Vazamento de Água", "confiancaScore": 0.92, "severidadeVisual": "Alta"},
        rag_context="Diretrizes Sabesp: Reparo em 24h",
        telemetria_iot={"sensorPresente": False},
        analise_iob={"socialUrgencyScore": 5.0}
    )
    assert "DADOS DO RELATO URBANO CIDADÃO:" in prompt
    assert "APROFUNDAMENTO TÉCNICO 1" in prompt
    assert "APROFUNDAMENTO TÉCNICO 2" in prompt
    assert "Vazamento de Água" in prompt

def test_gemini_client_fallback_opinion():
    client = GeminiClient(api_key="")  # Força fallback de alta fidelidade
    laudo, provider = client.generate_triagem_opinion(
        titulo="Semáforo apagado no cruzamento movimentado",
        descricao="Carros em alta velocidade sem sinalização, pedestres correndo perigo",
        categoria="Sinalização e Trânsito",
        analise_visual={"categoriaDetectada": "Sinalização e Trânsito", "confiancaScore": 0.88, "severidadeVisual": "Crítica"},
        rag_context="CTB e CET-SP",
        rag_metadata={"orgao_competente": "CET — Engenharia de Tráfego e Sinalização", "base_legal": "CTB / Normas CET", "sla_horas": 4},
        telemetria_iot={"sensorPresente": False, "anomaliaDetectada": False},
        analise_iob={"socialUrgencyScore": 9.0, "prioridade_sugerida_iob": "Crítica"}
    )
    assert laudo["prioridade"] == "Crítica"
    assert "CET" in laudo["orgaoResponsavel"]
    assert "Triagem IA" in laudo["parecerIa"]
    assert len(laudo["checklistVistoria"]) > 0
    assert "Heurístico" in provider

