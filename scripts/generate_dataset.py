import json
from pathlib import Path
import random

CATEGORIAS = [
    "Buraco na Rua",
    "Bueiro Entupido",
    "Iluminação Pública",
    "Entulho e Descarte Irregular",
    "Poda de Árvore",
    "Sinalização e Trânsito",
    "Vazamento de Água",
    "Outros"
]

SEVERIDADES = ["Baixa", "Média", "Alta", "Crítica"]

ORGAOS = {
    "Buraco na Rua": "Subprefeitura — Equipe de Pavimentação e Tapa-Buraco",
    "Bueiro Entupido": "Subprefeitura — Drenagem Urbana e Hidrojateamento",
    "Iluminação Pública": "Central Ilumina SP — Manutenção de Rede LED",
    "Entulho e Descarte Irregular": "Subprefeitura — Limpeza Pública e Fiscalização Ambiental",
    "Poda de Árvore": "Defesa Civil & Equipe de Manejo Arbóreo",
    "Sinalização e Trânsito": "CET — Engenharia de Tráfego e Sinalização",
    "Vazamento de Água": "Concessionária de Saneamento (Sabesp) & Fiscalização Municipal",
    "Outros": "Central de Zeladoria Municipal 156"
}

def generate_sample_cases():
    cases = [
        # --- Buraco na Rua ---
        {
            "id": "SMP-001",
            "categoria": "Buraco na Rua",
            "titulo": "Cratera profunda na faixa de rolamento da Avenida Paulista",
            "descricao": "Buraco com mais de 10cm de profundidade no asfalto bem em frente ao MASP. Risco grave de queda para motociclistas e danos nos veículos.",
            "prioridade_esperada": "Crítica",
            "orgao_esperado": ORGAOS["Buraco na Rua"],
            "visual_features": {
                "brightness": 128.5,
                "contrast": 74.2,
                "edge_density": 0.45,
                "texture_roughness": 0.82,
                "water_specularity": 0.05,
                "dominant_color": "gray_asphalt"
            },
            "iot_telemetry": {
                "sensor_type": "accelerometer_fleet",
                "vibration_g": 3.8,
                "road_impact_detected": True
            },
            "iob_metrics": {
                "community_supports": 38,
                "author_reputation_score": 0.94,
                "nearby_reports_count": 5
            },
            "is_failure_case": False
        },
        {
            "id": "SMP-002",
            "categoria": "Buraco na Rua",
            "titulo": "Asfalto trincado na Rua Frei Caneca",
            "descricao": "Pequena depressão e trincas no asfalto próximo ao meio fio, sem perda de controle de veículos no momento.",
            "prioridade_esperada": "Média",
            "orgao_esperado": ORGAOS["Buraco na Rua"],
            "visual_features": {
                "brightness": 140.1,
                "contrast": 45.0,
                "edge_density": 0.22,
                "texture_roughness": 0.40,
                "water_specularity": 0.0,
                "dominant_color": "gray_asphalt"
            },
            "iot_telemetry": {
                "sensor_type": "accelerometer_fleet",
                "vibration_g": 1.2,
                "road_impact_detected": False
            },
            "iob_metrics": {
                "community_supports": 4,
                "author_reputation_score": 0.85,
                "nearby_reports_count": 0
            },
            "is_failure_case": False
        },
        # --- Bueiro Entupido ---
        {
            "id": "SMP-003",
            "categoria": "Bueiro Entupido",
            "titulo": "Boca de lobo completamente bloqueada por folhas e garrafas plásticas",
            "descricao": "Água da chuva subindo rapidamente na sarjeta, risco imediato de alagamento na entrada da escola municipal.",
            "prioridade_esperada": "Crítica",
            "orgao_esperado": ORGAOS["Bueiro Entupido"],
            "visual_features": {
                "brightness": 95.0,
                "contrast": 62.1,
                "edge_density": 0.58,
                "texture_roughness": 0.70,
                "water_specularity": 0.75,
                "dominant_color": "dark_debris"
            },
            "iot_telemetry": {
                "sensor_type": "drain_ultrasonic_level",
                "water_level_pct": 92.0,
                "overflow_risk": True
            },
            "iob_metrics": {
                "community_supports": 29,
                "author_reputation_score": 0.98,
                "nearby_reports_count": 3
            },
            "is_failure_case": False
        },
        {
            "id": "SMP-004",
            "categoria": "Bueiro Entupido",
            "titulo": "Grelha com algumas folhas secas acumuladas",
            "descricao": "Acúmulo leve na grelha metálica, água continua escoando normalmente.",
            "prioridade_esperada": "Baixa",
            "orgao_esperado": ORGAOS["Bueiro Entupido"],
            "visual_features": {
                "brightness": 135.0,
                "contrast": 38.0,
                "edge_density": 0.20,
                "texture_roughness": 0.35,
                "water_specularity": 0.10,
                "dominant_color": "brown_leaves"
            },
            "iot_telemetry": {
                "sensor_type": "drain_ultrasonic_level",
                "water_level_pct": 18.0,
                "overflow_risk": False
            },
            "iob_metrics": {
                "community_supports": 2,
                "author_reputation_score": 0.90,
                "nearby_reports_count": 0
            },
            "is_failure_case": False
        },
        # --- Iluminação Pública ---
        {
            "id": "SMP-005",
            "categoria": "Iluminação Pública",
            "titulo": "Quatro postes consecutivos apagados na passarela de pedestres",
            "descricao": "Breu total na saída do metrô. Região escura com assaltos frequentes e risco à segurança pública dos pedestres e estudantes à noite.",
            "prioridade_esperada": "Crítica",
            "orgao_esperado": ORGAOS["Iluminação Pública"],
            "visual_features": {
                "brightness": 24.3,
                "contrast": 18.5,
                "edge_density": 0.15,
                "texture_roughness": 0.20,
                "water_specularity": 0.0,
                "dominant_color": "pitch_black"
            },
            "iot_telemetry": {
                "sensor_type": "smart_luminaire_ldr",
                "current_amperes": 0.0,
                "ambient_lux": 1.2,
                "luminaire_failed": True
            },
            "iob_metrics": {
                "community_supports": 45,
                "author_reputation_score": 0.96,
                "nearby_reports_count": 7
            },
            "is_failure_case": False
        },
        {
            "id": "SMP-006",
            "categoria": "Iluminação Pública",
            "titulo": "Poste com lâmpada piscando intermitente",
            "descricao": "Luminária pisca durante a noite na calçada residencial, iluminação da rua não foi totalmente comprometida.",
            "prioridade_esperada": "Média",
            "orgao_esperado": ORGAOS["Iluminação Pública"],
            "visual_features": {
                "brightness": 85.0,
                "contrast": 55.0,
                "edge_density": 0.30,
                "texture_roughness": 0.25,
                "water_specularity": 0.0,
                "dominant_color": "yellow_light"
            },
            "iot_telemetry": {
                "sensor_type": "smart_luminaire_ldr",
                "current_amperes": 0.4,
                "ambient_lux": 18.0,
                "luminaire_failed": False
            },
            "iob_metrics": {
                "community_supports": 6,
                "author_reputation_score": 0.88,
                "nearby_reports_count": 1
            },
            "is_failure_case": False
        },
        # --- Entulho e Descarte Irregular ---
        {
            "id": "SMP-007",
            "categoria": "Entulho e Descarte Irregular",
            "titulo": "Calçada bloqueada por montanha de entulho e sofás velhos",
            "descricao": "Pedestres e cadeirantes obrigados a andar pelo meio da rua disputando espaço com ônibus e carros. Risco de atropelamento e criadouro de escorpiões.",
            "prioridade_esperada": "Crítica",
            "orgao_esperado": ORGAOS["Entulho e Descarte Irregular"],
            "visual_features": {
                "brightness": 115.0,
                "contrast": 78.4,
                "edge_density": 0.65,
                "texture_roughness": 0.88,
                "water_specularity": 0.0,
                "dominant_color": "mixed_rubble"
            },
            "iot_telemetry": {
                "sensor_type": "smart_camera_surveillance",
                "sidewalk_occupancy_pct": 95.0,
                "pedestrian_flow_impeded": True
            },
            "iob_metrics": {
                "community_supports": 31,
                "author_reputation_score": 0.92,
                "nearby_reports_count": 4
            },
            "is_failure_case": False
        },
        {
            "id": "SMP-008",
            "categoria": "Entulho e Descarte Irregular",
            "titulo": "Restos de poda e sacos de folhagem encostados no muro",
            "descricao": "Morador colocou sacos de grama cortada na calçada, sem obstruir totalmente a passagem.",
            "prioridade_esperada": "Baixa",
            "orgao_esperado": ORGAOS["Entulho e Descarte Irregular"],
            "visual_features": {
                "brightness": 125.0,
                "contrast": 42.0,
                "edge_density": 0.28,
                "texture_roughness": 0.45,
                "water_specularity": 0.0,
                "dominant_color": "green_leaves"
            },
            "iot_telemetry": {
                "sensor_type": "smart_camera_surveillance",
                "sidewalk_occupancy_pct": 15.0,
                "pedestrian_flow_impeded": False
            },
            "iob_metrics": {
                "community_supports": 3,
                "author_reputation_score": 0.87,
                "nearby_reports_count": 0
            },
            "is_failure_case": False
        },
        # --- Poda de Árvore ---
        {
            "id": "SMP-009",
            "categoria": "Poda de Árvore",
            "titulo": "Galho gigante rachado em curto-circuito com fios de alta tensão",
            "descricao": "Árvore centenária estalando após o temporal com faíscas visíveis na fiação elétrica. Risco de incêndio e eletrocussão na calçada.",
            "prioridade_esperada": "Crítica",
            "orgao_esperado": ORGAOS["Poda de Árvore"],
            "visual_features": {
                "brightness": 88.0,
                "contrast": 71.0,
                "edge_density": 0.62,
                "texture_roughness": 0.79,
                "water_specularity": 0.12,
                "dominant_color": "wood_branches"
            },
            "iot_telemetry": {
                "sensor_type": "grid_power_monitor",
                "voltage_surge_detected": True,
                "line_short_circuit_alert": True
            },
            "iob_metrics": {
                "community_supports": 52,
                "author_reputation_score": 0.99,
                "nearby_reports_count": 8
            },
            "is_failure_case": False
        },
        {
            "id": "SMP-010",
            "categoria": "Poda de Árvore",
            "titulo": "Galho baixo cobrindo parte do nome da rua",
            "descricao": "Folhagem cresceu e dificulta leitura da placa de identificação da esquina.",
            "prioridade_esperada": "Baixa",
            "orgao_esperado": ORGAOS["Poda de Árvore"],
            "visual_features": {
                "brightness": 130.0,
                "contrast": 39.0,
                "edge_density": 0.35,
                "texture_roughness": 0.50,
                "water_specularity": 0.0,
                "dominant_color": "green_leaves"
            },
            "iot_telemetry": {
                "sensor_type": "grid_power_monitor",
                "voltage_surge_detected": False,
                "line_short_circuit_alert": False
            },
            "iob_metrics": {
                "community_supports": 2,
                "author_reputation_score": 0.89,
                "nearby_reports_count": 0
            },
            "is_failure_case": False
        },
        # --- Vazamento de Água ---
        {
            "id": "SMP-011",
            "categoria": "Vazamento de Água",
            "titulo": "Rompimento de adutora com enxurrada e asfalto cedendo",
            "descricao": "Jato de água de alta pressão brotando da via, solapando asfalto e ameaçando engolir carros estacionados. Desperdício imenso.",
            "prioridade_esperada": "Crítica",
            "orgao_esperado": ORGAOS["Vazamento de Água"],
            "visual_features": {
                "brightness": 145.0,
                "contrast": 82.0,
                "edge_density": 0.68,
                "texture_roughness": 0.75,
                "water_specularity": 0.92,
                "dominant_color": "reflective_water"
            },
            "iot_telemetry": {
                "sensor_type": "water_pipe_pressure",
                "pressure_drop_pct": 78.5,
                "flow_abnormality_alert": True
            },
            "iob_metrics": {
                "community_supports": 41,
                "author_reputation_score": 0.97,
                "nearby_reports_count": 6
            },
            "is_failure_case": False
        },
        {
            "id": "SMP-012",
            "categoria": "Vazamento de Água",
            "titulo": "Gotejamento persistente no hidrômetro da calçada",
            "descricao": "Pequena umidade escorrendo pela sarjeta, sem cratera no solo.",
            "prioridade_esperada": "Média",
            "orgao_esperado": ORGAOS["Vazamento de Água"],
            "visual_features": {
                "brightness": 120.0,
                "contrast": 48.0,
                "edge_density": 0.25,
                "texture_roughness": 0.32,
                "water_specularity": 0.35,
                "dominant_color": "damp_concrete"
            },
            "iot_telemetry": {
                "sensor_type": "water_pipe_pressure",
                "pressure_drop_pct": 5.0,
                "flow_abnormality_alert": False
            },
            "iob_metrics": {
                "community_supports": 5,
                "author_reputation_score": 0.91,
                "nearby_reports_count": 0
            },
            "is_failure_case": False
        },
        # --- Sinalização e Trânsito ---
        {
            "id": "SMP-013",
            "categoria": "Sinalização e Trânsito",
            "titulo": "Semáforo principal inoperante em cruzamento de avenida rápida",
            "descricao": "Semáforo apagado no cruzamento com a Radial Leste. Quase colisões a cada minuto, motoristas desesperados e travessia perigosa de pedestres.",
            "prioridade_esperada": "Crítica",
            "orgao_esperado": ORGAOS["Sinalização e Trânsito"],
            "visual_features": {
                "brightness": 98.0,
                "contrast": 64.0,
                "edge_density": 0.52,
                "texture_roughness": 0.45,
                "water_specularity": 0.05,
                "dominant_color": "traffic_lights"
            },
            "iot_telemetry": {
                "sensor_type": "traffic_controller_status",
                "power_supply_ok": False,
                "controller_heartbeat_failed": True
            },
            "iob_metrics": {
                "community_supports": 58,
                "author_reputation_score": 0.99,
                "nearby_reports_count": 9
            },
            "is_failure_case": False
        },
        {
            "id": "SMP-014",
            "categoria": "Sinalização e Trânsito",
            "titulo": "Pintura de faixa de pedestres gasta na rua local",
            "descricao": "Tinta branca desgastada pelo tempo em via de bairro residencial com pouco fluxo.",
            "prioridade_esperada": "Baixa",
            "orgao_esperado": ORGAOS["Sinalização e Trânsito"],
            "visual_features": {
                "brightness": 138.0,
                "contrast": 41.0,
                "edge_density": 0.30,
                "texture_roughness": 0.38,
                "water_specularity": 0.0,
                "dominant_color": "faded_stripes"
            },
            "iot_telemetry": {
                "sensor_type": "traffic_controller_status",
                "power_supply_ok": True,
                "controller_heartbeat_failed": False
            },
            "iob_metrics": {
                "community_supports": 3,
                "author_reputation_score": 0.86,
                "nearby_reports_count": 0
            },
            "is_failure_case": False
        },
        # --- CASOS DE FALHA E TESTES DE ROBUSTEZ (CRITÉRIO 05) ---
        {
            "id": "SMP-FAIL-01",
            "categoria": "Outros",
            "titulo": "rua ruim",
            "descricao": "ta muito ruim aqui arruma pfvr",
            "prioridade_esperada": "Baixa",
            "orgao_esperado": ORGAOS["Outros"],
            "visual_features": {
                "brightness": 3.0,
                "contrast": 2.1,
                "edge_density": 0.02,
                "texture_roughness": 0.05,
                "water_specularity": 0.0,
                "dominant_color": "sensor_noise_black"
            },
            "iot_telemetry": {
                "sensor_type": "unknown",
                "vibration_g": 0.0,
                "telemetry_corrupted": True
            },
            "iob_metrics": {
                "community_supports": 0,
                "author_reputation_score": 0.20,
                "nearby_reports_count": 0
            },
            "is_failure_case": True,
            "failure_reason": "Texto extremamente vago sem detalhes e imagem totalmente escura com ruído de sensor."
        },
        {
            "id": "SMP-FAIL-02",
            "categoria": "Buraco na Rua",
            "titulo": "Buraco",
            "descricao": "",
            "prioridade_esperada": "Média",
            "orgao_esperado": ORGAOS["Buraco na Rua"],
            "visual_features": {
                "brightness": 250.0,
                "contrast": 5.0,
                "edge_density": 0.03,
                "texture_roughness": 0.02,
                "water_specularity": 0.0,
                "dominant_color": "overexposed_white"
            },
            "iot_telemetry": {
                "sensor_type": "accelerometer_fleet",
                "vibration_g": -999.0, # valor anômalo de telemetria
                "telemetry_corrupted": True
            },
            "iob_metrics": {
                "community_supports": 1,
                "author_reputation_score": 0.50,
                "nearby_reports_count": 0
            },
            "is_failure_case": True,
            "failure_reason": "Descrição textual vazia, foto superexposta e sensor IoT com valor de leitura ruidoso/corrompido."
        }
    ]

    # Gera mais casos sintéticos balanceados para ter mais de 80 amostras para machine learning
    random.seed(42)
    categories_keys = list(ORGAOS.keys())
    for idx in range(15, 85):
        cat = random.choice(categories_keys)
        prio = random.choice(["Baixa", "Média", "Alta", "Crítica"])
        
        is_crit = prio == "Crítica"
        is_alta = prio == "Alta"
        is_baixa = prio == "Baixa"

        if is_crit:
            supports = random.randint(26, 60)
            desc = f"Risco grave de acidente iminente e perigo aos transeuntes. Ocorrência de {cat} com urgência máxima."
            vibr_g = random.uniform(2.8, 5.0) if cat == "Buraco na Rua" else random.uniform(0.5, 1.5)
            water_lvl = random.uniform(88.0, 98.0) if cat == "Bueiro Entupido" else 15.0
            roughness = random.uniform(0.70, 0.95)
        elif is_alta:
            supports = random.randint(15, 24)
            desc = f"Situação com impacto e risco potencial considerável em via movimentada. Ocorrência de {cat} requer atenção prioritária."
            vibr_g = random.uniform(1.8, 2.4)
            water_lvl = random.uniform(70.0, 85.0) if cat == "Bueiro Entupido" else 12.0
            roughness = random.uniform(0.50, 0.70)
        elif is_baixa:
            supports = random.randint(0, 4)
            desc = f"Pequeno desgaste leve de rotina, sem risco imediato. Manutenção preventiva de {cat}."
            vibr_g = random.uniform(0.1, 0.8)
            water_lvl = random.uniform(5.0, 25.0)
            roughness = random.uniform(0.10, 0.35)
        else: # Média
            supports = random.randint(5, 14)
            desc = f"Demanda de zeladoria urbana padrão de {cat} para vistoria programada no bairro."
            vibr_g = random.uniform(1.0, 1.7)
            water_lvl = random.uniform(30.0, 60.0)
            roughness = random.uniform(0.35, 0.50)
        
        cases.append({
            "id": f"SMP-{idx:03d}",
            "categoria": cat,
            "titulo": f"Ocorrência de {cat} reportada na região urbana #{idx}",
            "descricao": desc,
            "prioridade_esperada": prio,
            "orgao_esperado": ORGAOS[cat],
            "visual_features": {
                "brightness": random.uniform(50.0, 180.0),
                "contrast": random.uniform(30.0, 90.0),
                "edge_density": random.uniform(0.15, 0.75),
                "texture_roughness": round(roughness, 4),
                "water_specularity": random.uniform(0.6, 0.95) if cat in ["Vazamento de Água", "Bueiro Entupido"] else random.uniform(0.0, 0.2),
                "dominant_color": "urban_texture"
            },
            "iot_telemetry": {
                "sensor_type": "urban_multisensor",
                "vibration_g": round(vibr_g, 2),
                "water_level_pct": round(water_lvl, 1),
                "road_impact_detected": vibr_g >= 2.5
            },
            "iob_metrics": {
                "community_supports": supports,
                "author_reputation_score": round(random.uniform(0.80, 0.99), 2),
                "nearby_reports_count": random.randint(0, 4)
            },
            "is_failure_case": False
        })

    return cases

if __name__ == "__main__":
    dataset_dir = Path("data/dataset_urban")
    dataset_dir.mkdir(parents=True, exist_ok=True)
    samples = generate_sample_cases()
    with open(dataset_dir / "samples.json", "w", encoding="utf-8") as f:
        json.dump(samples, f, indent=2, ensure_ascii=False)
    print(f"Dataset gerado com sucesso: {len(samples)} casos salvos em {dataset_dir / 'samples.json'}")

