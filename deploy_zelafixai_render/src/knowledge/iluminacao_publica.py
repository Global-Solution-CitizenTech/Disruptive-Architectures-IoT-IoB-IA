"""
Base de Conhecimento RAG: Iluminação Pública, Postes e Rede Noturna — PMSP
Fundamentação Legal: PPP Ilumina SP, Portaria SGM/SES nº 03/2021 e Resolução Normativa ANEEL
"""
from typing import Dict, Any, List

_SOURCE = "Contrato PPP Ilumina SP e Portaria SGM/SES nº 03/2021"

CHUNKS_ILUMINACAO: List[Dict[str, Any]] = [
    {
        "id": "ilum_01",
        "source": _SOURCE,
        "urgency": "alta",
        "category": "iluminacao",
        "title": "Substituição de Lâmpadas Apagadas e Modernização para LED (Ilumina SP)",
        "content": (
            "A manutenção do parque de iluminação pública da Cidade de São Paulo é operada pelo consórcio Ilumina SP através de Parceria Público-Privada (PPP). "
            "Chamados informando lâmpadas queimadas, luminárias apagadas ou oscilando (piscando) devem ser atendidos no prazo de 24 a 48 horas úteis. "
            "A substituição utiliza exclusivamente luminárias de tecnologia LED de alta eficiência energética, que oferecem maior fluxo luminoso, "
            "índice de reprodução de cor superior e durabilidade de até 50.000 horas, contribuindo para a sustentabilidade da cidade (ODS 11)."
        ),
        "keywords": ["poste apagado", "lampada queimada", "luz da rua apagada", "ilumina sp", "luminaria led", "escuridao na rua", "trocar lampada do poste"]
    },
    {
        "id": "ilum_02",
        "source": _SOURCE,
        "urgency": "URGENTE",
        "category": "iluminacao",
        "title": "Apagão em Vias Escolares, Pontos de Ônibus e Locais de Vulnerabilidade",
        "content": (
            "Quando a falta de iluminação atinge múltiplos postes consecutivos (circuito em blackout) ou ocorre em frente a escolas, creches, "
            "hospitais, unidades básicas de saúde ou pontos de ônibus com grande circulação de passageiros, a ocorrência recebe prioridade URGENTE "
            "devido ao elevado risco à segurança pessoal e vulnerabilidade contra assaltos e assédios no período noturno. O prazo normativo para "
            "restabelecimento do circuito de iluminação é de 12 a 24 horas."
        ),
        "keywords": ["rua inteira no escuro", "ponto de onibus escuro", "porta de escola apagada", "varios postes apagados", "apagao noturno", "seguranca publica", "ilumina sp"]
    },
    {
        "id": "ilum_03",
        "source": _SOURCE,
        "urgency": "baixa",
        "category": "iluminacao",
        "title": "Luminária Pública Acesa Durante o Dia (Defeito no Relé Fotoelétrico)",
        "content": (
            "Lâmpadas de postes que permanecem continuamente acesas durante a luz do dia caracterizam falha mecânica ou eletrônica no relé "
            "fotoelétrico (fotocélula) responsável por acionar o circuito no entardecer e desligar ao amanhecer. Embora não represente risco físico "
            "imediato ao cidadão, acarreta desperdício de energia elétrica e redução da vida útil do equipamento. O reparo é classificado com urgência "
            "BAIXA e prazo de regularização de até 72 horas úteis."
        ),
        "keywords": ["poste aceso de dia", "lampada acesa de dia", "rele fotoeletrico quebrado", "fotocelula defeituosa", "desperdicio de luz"]
    },
    {
        "id": "ilum_04",
        "source": _SOURCE,
        "urgency": "URGENTE",
        "category": "iluminacao",
        "title": "Poste Abalroado, Fiação Energizada Exposta e Risco de Eletrocussão",
        "content": (
            "Situações em que postes de iluminação ou de distribuição de energia foram abalroados por colisões veiculares, encontram-se inclinados com "
            "risco de queda ou possuem cabos elétricos caídos em calçadas/vias públicas (especialmente em dias de chuva e poças d'água) configuram "
            "EMERGÊNCIA VITAL com risco imediato de choque elétrico fatal. O ZelaFix aciona em regime de urgência máxima a concessionária ENEL (0800 72 72 196), "
            "a Ilumina SP e a CET para isolamento perimetral imediato e desligamento emergencial da rede pelo Centro de Operações."
        ),
        "keywords": ["poste caido", "fio solto", "fio no chao", "fio dando choque", "choque eletrico", "fio desencapado", "poste batido", "enel", "bombeiros"]
    }
]
