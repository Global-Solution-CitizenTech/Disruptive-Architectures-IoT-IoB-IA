"""
Testes de Modos de Falha, Robustez e Tratamento de Exceções
Atende diretamente ao Critério 05 do Edital FIAP GS 2026/2
"""

from src.cv.classifier import UrbanCVClassifier
from src.services.triagem_service import TriagemService
from src.schemas.chamado_ia import TriagemRequestDTO
from src.iot.sensor_processor import UrbanSensorProcessor

def test_failure_mode_missing_image_and_empty_description():
    """Cenário de falha: usuário envia chamado sem foto e com descrição em branco."""
    service = TriagemService()
    req = TriagemRequestDTO(
        titulo="Buraco",
        categoria="Buraco na Rua",
        descricao="",
        fotoUrl=None,
        apoiosCount=0
    )
    res = service.processar_triagem(req)
    assert res.statusExecucao == "SUCESSO"
    assert res.prioridade in ["Baixa", "Média", "Alta", "Crítica"]
    assert res.analiseVisual.caracteristicasExtraidas["dominant_color_channel"] == "unknown"
    assert "Subprefeitura" in res.orgaoResponsavel

def test_failure_mode_corrupted_iot_telemetry():
    """Cenário de falha: dispositivo IoT envia payload com sensor desconhecido e dados nulos."""
    payload = {
        "device_id": "IOT-FAULTY-999",
        "device_type": "unknown_device_type_xyz",
        "data": {}
    }
    result = UrbanSensorProcessor.evaluate_telemetry(payload)
    assert result.anomaly_detected is False
    assert result.severity_level == "Normal"

def test_failure_mode_invalid_image_url_graceful_handling():
    """Cenário de falha: URL de imagem inexistente ou com erro 404."""
    classifier = UrbanCVClassifier()
    res = classifier.analyze_image(
        image_url="https://invalid-domain-does-not-exist-1234567.com/photo.jpg",
        categoria_declarada="Bueiro Entupido"
    )
    assert res.is_low_quality_warning is True
    assert "Não foi possível processar a imagem" in res.warning_message
    assert res.predicted_category == "Bueiro Entupido"

def test_failure_mode_unregistered_category_defaults_to_general():
    """Cenário de falha: categoria não padrão submetida."""
    service = TriagemService()
    req = TriagemRequestDTO(
        titulo="Problema não catalogado na praça",
        categoria="Outros",
        descricao="Algum problema qualquer",
        apoiosCount=1
    )
    res = service.processar_triagem(req)
    assert res.statusExecucao == "SUCESSO"
    assert "Central de Zeladoria" in res.orgaoResponsavel or "Subprefeitura" in res.orgaoResponsavel

