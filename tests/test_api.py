"""
Testes Unitários e de Integração dos Endpoints da API FastAPI
"""

import pytest
from fastapi.testclient import TestClient
from src.api.app import app

client = TestClient(app)

def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UP"
    assert "components" in data
    assert data["components"]["computerVision"] == "UP"
    assert data["components"]["ragVectorStore"] == "UP"

def test_actuator_health_endpoint():
    response = client.get("/actuator/health")
    assert response.status_code == 200
    assert response.json()["status"] == "UP"

def test_metadata_endpoint():
    response = client.get("/api/v1/meta")
    assert response.status_code == 200
    data = response.json()
    assert data["turma"] == "2TDSPG"
    assert len(data["equipe"]) == 5

def test_triagem_analisar_endpoint_buraco():
    payload = {
        "titulo": "Buraco na pista expressa",
        "categoria": "Buraco na Rua",
        "descricao": "Cratera funda no asfalto com risco de queda de moto.",
        "apoiosCount": 35,
        "telemetriaIot": {
            "device_id": "IOT-VIB-01",
            "device_type": "fleet_accelerometer",
            "data": {"vibration_g": 3.6, "speed_kmh": 45.0}
        }
    }
    response = client.post("/api/v1/triagem-ia/analisar", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["prioridade"] in ["Alta", "Crítica"]
    assert "Subprefeitura" in data["orgaoResponsavel"]
    assert len(data["parecerIa"]) > 20
    assert data["analiseVisual"] is not None
    assert data["evidenciasRag"] is not None
    assert data["telemetriaIot"]["anomaliaDetectada"] is True
    assert data["analiseIob"]["socialUrgencyScore"] > 7.0

def test_cv_analisar_imagem_endpoint():
    payload = {
        "categoria_declarada": "Buraco na Rua"
    }
    response = client.post("/api/v1/cv/analisar-imagem", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "predicted_category" in data
    assert "confidence" in data
    assert "visual_severity" in data

def test_rag_consultar_endpoint():
    payload = {
        "query": "Como desobstruir bueiro entupido com hidrojato e qual o prazo de atendimento?",
        "categoria": "Bueiro Entupido",
        "top_k": 2
    }
    response = client.post("/api/v1/rag/consultar", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_chunks_found"] > 0
    assert len(data["chunks"]) > 0
    assert "Drenagem" in data["chunks"][0]["title"] or "Bueiro" in data["chunks"][0]["title"]

def test_iot_telemetria_endpoint():
    payload = {
        "device_id": "TEST-DRAIN-01",
        "device_type": "drain_ultrasonic_level",
        "latitude": -23.55,
        "longitude": -46.63,
        "data": {"water_level_pct": 94.0}
    }
    response = client.post("/api/v1/iot/telemetria", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["anomaly_detected"] is True
    assert data["severity_level"] == "Crítico"
    assert data["inferred_category"] == "Bueiro Entupido"

def test_iob_analise_comportamental_endpoint():
    payload = {
        "apoiosCount": 30,
        "authorReputation": 0.95,
        "nearbyReports": 4
    }
    response = client.post("/api/v1/iob/analise-comportamental", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["social_urgency_score"] >= 8.0
    assert data["ajuste_prioridade_comunitario"] is True

