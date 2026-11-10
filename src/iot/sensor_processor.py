"""
Processador de Telemetria de Sensores Urbanos Inteligentes (IoT)
Conecta dados de sensores físicos de cidade inteligente à triagem de zeladoria
"""

from typing import Dict, Any, Optional
from ..config import IOT_ANOMALY_THRESHOLD_G
from ..schemas.iot_models import IotAnalysisResult, IotTelemetryPayload

class UrbanSensorProcessor:
    """Processa sinais e telemetrias de sensores IoT espalhados pelo espaço urbano."""

    @classmethod
    def evaluate_telemetry(cls, payload: Dict[str, Any]) -> IotAnalysisResult:
        """
        Analisa o payload de um sensor IoT (acelerômetro, hidrômetro ou fotocélula).
        Retorna o diagnóstico de anomalia e inferência para o chamado.
        """
        device_id = payload.get("device_id", "IOT-UNKNOWN")
        dev_type = payload.get("device_type", "generic_sensor").lower()
        data = payload.get("readings") or payload.get("data") or {}

        # 1. Sensor Acelerômetro em Frotas Municipais (Tapa-buraco / Impacto viário)
        if "accelerometer" in dev_type or "vibration" in dev_type or "fleet" in dev_type:
            vibration_g = float(data.get("vibration_g", data.get("acceleration_z_g", 0.0)))
            anomaly = vibration_g >= IOT_ANOMALY_THRESHOLD_G

            severity = "Crítico" if vibration_g > 3.5 else ("Alerta" if anomaly else "Normal")
            return IotAnalysisResult(
                device_id=device_id,
                anomaly_detected=anomaly,
                severity_level=severity,
                inferred_category="Buraco na Rua",
                trigger_automatic_ticket=anomaly,
                details={
                    "sensor_category": "Vibração Viária / Acelerômetro",
                    "vibration_detected_g": vibration_g,
                    "threshold_limit_g": IOT_ANOMALY_THRESHOLD_G,
                    "impact_diagnosis": "Solavanco mecânico crítico detectado em eixo veicular" if anomaly else "Leitura dentro do padrão de rodagem suave"
                }
            )

        # 2. Sensor Ultrassônico de Nível d'Água em Boca de Lobo / Bueiro
        if "drain" in dev_type or "water_level" in dev_type or "bueiro" in dev_type:
            water_level_pct = float(data.get("water_level_pct", data.get("calculated_fill_percentage", 0.0)))
            anomaly = water_level_pct >= 75.0
            severity = "Crítico" if water_level_pct >= 90.0 else ("Alerta" if anomaly else "Normal")

            return IotAnalysisResult(
                device_id=device_id,
                anomaly_detected=anomaly,
                severity_level=severity,
                inferred_category="Bueiro Entupido",
                trigger_automatic_ticket=anomaly,
                details={
                    "sensor_category": "Nível Hidrométrico de Boca de Lobo",
                    "fill_percentage": water_level_pct,
                    "overflow_risk": anomaly,
                    "impact_diagnosis": "Obstrução severa com risco iminente de bolsão de alagamento" if anomaly else "Drenagem com fluxo hídrico livre"
                }
            )

        # 3. Sensor LDR / Corrente em Luminária Pública LED
        if "luminaire" in dev_type or "ldr" in dev_type or "ilumina" in dev_type:
            current_amps = float(data.get("current_amperes", data.get("lamp_current_amperes", 1.0)))
            lux = float(data.get("ambient_lux", data.get("ambient_illuminance_lux", 50.0)))
            failed = bool(data.get("luminaire_failed", data.get("lamp_failure_flag", False)))

            anomaly = failed or (current_amps < 0.1 and lux < 5.0)
            severity = "Crítico" if anomaly else "Normal"

            return IotAnalysisResult(
                device_id=device_id,
                anomaly_detected=anomaly,
                severity_level=severity,
                inferred_category="Iluminação Pública",
                trigger_automatic_ticket=anomaly,
                details={
                    "sensor_category": "Fotometria e Corrente Elétrica em Luminária LED",
                    "current_amperes": current_amps,
                    "ambient_lux": lux,
                    "impact_diagnosis": "Circuito inoperante e escuridão detectada no período noturno" if anomaly else "Luminária operando nos parâmetros nominais"
                }
            )

        # 4. Sensor Genérico / Fallback
        return IotAnalysisResult(
            device_id=device_id,
            anomaly_detected=False,
            severity_level="Normal",
            inferred_category=None,
            trigger_automatic_ticket=False,
            details={"message": "Sensor lido sem anomalias críticas registradas."}
        )

