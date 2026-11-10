"""
DTOs para o módulo de Sensores Urbanos IoT
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class IotTelemetryPayload(BaseModel):
    device_id: str = Field(..., example="IOT-VIB-SP-042")
    device_type: str = Field(..., example="fleet_accelerometer")
    latitude: float = Field(-23.5629, example=-23.5629)
    longitude: float = Field(-46.6544, example=-46.6544)
    timestamp: Optional[str] = None
    data: Dict[str, Any] = Field(..., example={"vibration_g": 3.8, "speed_kmh": 40.0})

class IotAnalysisResult(BaseModel):
    device_id: str
    anomaly_detected: bool
    severity_level: str = Field("Normal", description="Normal | Alerta | Crítico")
    inferred_category: Optional[str] = None
    trigger_automatic_ticket: bool = False
    details: Dict[str, Any]

