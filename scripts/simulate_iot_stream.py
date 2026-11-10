"""
Simulador de Fluxo de Telemetria IoT em Tempo Real
FIAP Global Solution 2026/2 - Disruptive Architectures: IoT, IoB & Generative IA

Simula múltiplos nós de sensores urbanos conectados enviando dados para a API ZelaFix:
- Nó 1: Acelerômetro Triaxial em Frota de Ônibus (SPTrans)
- Nó 2: Sensor Ultrassônico de Nível em Boca de Lobo (Drenagem Urbana)
- Nó 3: Sensor Fotométrico em Luminária Pública LED (Central Ilumina SP)
"""

import sys
import time
import json
import random
from pathlib import Path

# Adiciona o diretório raiz ao sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.iot.sensor_processor import UrbanSensorProcessor
from src.schemas.iot_models import IotTelemetryPayload

# Cores ANSI para o terminal
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

DEVICES = [
    {
        "id": "IOT-BUS-875A-01",
        "type": "fleet_accelerometer",
        "name": "Ônibus Municipal - Linha 875A (Perdizes/Paulista)",
        "coords": (-23.5629, -46.6544)
    },
    {
        "id": "IOT-DRAIN-CENTRO-108",
        "type": "drain_ultrasonic_level",
        "name": "Boca de Lobo Sarjeta - Rua 25 de Março",
        "coords": (-23.5505, -46.6333)
    },
    {
        "id": "IOT-LUM-PINHEIROS-789",
        "type": "smart_luminaire_ldr",
        "name": "Poste Metálico P-12 - Av. Brigadeiro Faria Lima",
        "coords": (-23.5921, -46.6854)
    }
]

def simulate_reading(device: dict, cycle: int) -> dict:
    dev_type = device["type"]

    # No terceiro ciclo simula impacto/anomalia para demonstrar a reação da IA
    is_anomaly = (cycle % 3 == 0)

    if dev_type == "fleet_accelerometer":
        vibration = round(random.uniform(3.2, 4.6), 2) if is_anomaly else round(random.uniform(0.4, 1.5), 2)
        speed = round(random.uniform(35.0, 50.0), 1)
        data = {
            "vibration_g": vibration,
            "speed_kmh": speed,
            "road_anomaly_flag": vibration >= 2.5
        }
    elif dev_type == "drain_ultrasonic_level":
        fill = round(random.uniform(88.0, 96.0), 1) if is_anomaly else round(random.uniform(15.0, 45.0), 1)
        data = {
            "water_level_pct": fill,
            "overflow_risk": fill >= 80.0
        }
    else:  # smart_luminaire_ldr
        current = 0.0 if is_anomaly else 1.25
        lux = 0.8 if is_anomaly else 45.0
        data = {
            "current_amperes": current,
            "ambient_lux": lux,
            "luminaire_failed": is_anomaly
        }

    return {
        "device_id": device["id"],
        "device_type": device["type"],
        "latitude": device["coords"][0],
        "longitude": device["coords"][1],
        "data": data
    }

def main():
    print(f"\n{BOLD}{CYAN}================================================================================{RESET}")
    print(f"{BOLD}{GREEN}  ZELAFIX IoT STREAM SIMULATOR — TELEMETRIA URBANA CONECTADA EM TEMPO REAL      {RESET}")
    print(f"{BOLD}{CYAN}  FIAP Global Solution 2026/2 — Disruptive Architectures: IoT, IoB & GenAI     {RESET}")
    print(f"{BOLD}{CYAN}================================================================================{RESET}\n")

    print(f"{YELLOW}Iniciando transmissão de sensores simulados... (Pressione Ctrl+C para encerrar){RESET}\n")

    cycle = 1
    try:
        while cycle <= 6:
            print(f"{BOLD}--- Ciclo de Transmissão #{cycle} ({time.strftime('%H:%M:%S')}) ---{RESET}")

            for dev in DEVICES:
                payload_dict = simulate_reading(dev, cycle)
                result = UrbanSensorProcessor.evaluate_telemetry(payload_dict)

                status_color = RED if result.anomaly_detected else GREEN
                status_icon = "🚨 CRÍTICO" if result.anomaly_detected else "✓ NORMAL"

                print(f"[{dev['name']}]")
                print(f"  ID: {dev['id']} | Tipo: {dev['type']}")
                print(f"  Status: {status_color}{status_icon}{RESET} | Severidade: {status_color}{result.severity_level}{RESET}")
                print(f"  Leitura Física: {payload_dict['data']}")
                print(f"  Diagnóstico de Borda: {result.details.get('impact_diagnosis', 'OK')}")

                if result.anomaly_detected:
                    print(f"  {RED}↳ Disparo Automático de Alerta de Zeladoria para Triagem IA!{RESET}")
                print()

            cycle += 1
            time.sleep(2)

        print(f"\n{GREEN}[✓] Simulação de fluxo contínuo IoT concluída com 100% de sucesso!{RESET}\n")
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Simulador encerrado pelo usuário.{RESET}\n")

if __name__ == "__main__":
    main()
