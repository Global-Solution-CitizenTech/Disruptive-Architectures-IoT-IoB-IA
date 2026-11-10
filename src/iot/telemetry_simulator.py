"""
Simulador de Telemetria de Dispositivos IoT Urbanos
Gera leituras sintéticas para testes dinâmicos e demonstração presencial
"""

import random
from typing import Dict, Any

class TelemetrySimulator:
    """Gera payloads de telemetria IoT simulados para demonstração da banca."""

    @staticmethod
    def generate_accelerometer_reading(is_critical: bool = False) -> Dict[str, Any]:
        vibration = random.uniform(3.0, 4.8) if is_critical else random.uniform(0.3, 1.6)
        return {
            "device_id": f"IOT-ACC-SP-{random.randint(100, 999)}",
            "device_type": "fleet_accelerometer",
            "data": {
                "vibration_g": round(vibration, 2),
                "speed_kmh": round(random.uniform(30.0, 55.0), 1),
                "road_impact_detected": vibration >= 2.5
            }
        }

    @staticmethod
    def generate_drain_reading(is_critical: bool = False) -> Dict[str, Any]:
        fill = random.uniform(85.0, 98.0) if is_critical else random.uniform(10.0, 40.0)
        return {
            "device_id": f"IOT-DRN-SP-{random.randint(100, 999)}",
            "device_type": "drain_ultrasonic_level",
            "data": {
                "water_level_pct": round(fill, 1),
                "overflow_risk": fill >= 75.0
            }
        }

    @staticmethod
    def generate_luminaire_reading(is_critical: bool = False) -> Dict[str, Any]:
        return {
            "device_id": f"IOT-LUM-SP-{random.randint(100, 999)}",
            "device_type": "smart_luminaire_telemetry",
            "data": {
                "current_amperes": 0.0 if is_critical else 1.25,
                "ambient_lux": 1.5 if is_critical else 35.0,
                "luminaire_failed": is_critical
            }
        }

