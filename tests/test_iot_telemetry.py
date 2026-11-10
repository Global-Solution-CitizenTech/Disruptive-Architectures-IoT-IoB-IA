"""
Testes Unitários de Sensores Urbanos Conectados (IoT)
"""

from src.iot.sensor_processor import UrbanSensorProcessor
from src.iot.telemetry_simulator import TelemetrySimulator

def test_accelerometer_critical_anomaly():
    payload = {
        "device_id": "ACC-TEST-01",
        "device_type": "fleet_accelerometer",
        "data": {"vibration_g": 3.8, "speed_kmh": 40.0}
    }
    result = UrbanSensorProcessor.evaluate_telemetry(payload)
    assert result.anomaly_detected is True
    assert result.severity_level == "Crítico"
    assert result.inferred_category == "Buraco na Rua"

def test_accelerometer_normal_reading():
    payload = {
        "device_id": "ACC-TEST-02",
        "device_type": "fleet_accelerometer",
        "data": {"vibration_g": 1.2, "speed_kmh": 45.0}
    }
    result = UrbanSensorProcessor.evaluate_telemetry(payload)
    assert result.anomaly_detected is False
    assert result.severity_level == "Normal"

def test_drain_level_flood_alert():
    payload = {
        "device_id": "DRN-TEST-01",
        "device_type": "drain_ultrasonic_level",
        "data": {"water_level_pct": 94.5}
    }
    result = UrbanSensorProcessor.evaluate_telemetry(payload)
    assert result.anomaly_detected is True
    assert result.severity_level == "Crítico"
    assert result.inferred_category == "Bueiro Entupido"

def test_luminaire_blackout():
    payload = {
        "device_id": "LUM-TEST-01",
        "device_type": "smart_luminaire_ldr",
        "data": {"current_amperes": 0.0, "ambient_lux": 0.5, "luminaire_failed": True}
    }
    result = UrbanSensorProcessor.evaluate_telemetry(payload)
    assert result.anomaly_detected is True
    assert result.severity_level == "Crítico"
    assert result.inferred_category == "Iluminação Pública"

def test_telemetry_simulator_outputs():
    acc = TelemetrySimulator.generate_accelerometer_reading(is_critical=True)
    assert acc["data"]["vibration_g"] >= 2.5
    drn = TelemetrySimulator.generate_drain_reading(is_critical=False)
    assert drn["data"]["water_level_pct"] < 75.0

