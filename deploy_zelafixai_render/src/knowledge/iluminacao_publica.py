"""
Base de Conhecimento RAG: Iluminação Pública, Telegestão LED e Pontos Escuros — PMSP
Fundamentação Legal: Portaria SGM/SES nº 03/2021 e Contrato de Concessão PPP Ilumina SP
Órgão Competente: Departamento de Iluminação Pública (Ilumina SP) e Concessionária Ilumina SP
"""
from typing import Dict, Any, List

_SOURCE = "Portaria SGM/SES nº 03/2021 e Contrato de Concessão PPP Ilumina SP"

CHUNKS_ILUMINACAO: List[Dict[str, Any]] = [
    {
        "id": "ilum_01",
        "source": _SOURCE,
        "urgency": "alta",
        "category": "iluminacao",
        "title": "Substituição de Lâmpadas Queimadas e Reparo de Pontos Escuros em Vias Públicas",
        "content": (
            "A manutenção do parque de iluminação pública da capital paulista é operada pela concessionária Ilumina SP sob regulação do Departamento "
            "de Iluminação Pública (DIP/SGM). Chamados referentes a postes com lâmpadas apagadas à noite, luminárias piscando ou trechos de vias com "
            "iluminação intermitente possuem prazo contratual máximo de atendimento de até 48 horas úteis após a notificação formal no sistema. "
            "A equipe realiza a troca da lâmpada de vapor de sódio remanescente por luminária LED de alta eficiência com telegestão."
        ),
        "keywords": ["lampada queimada", "poste apagado", "ponto escuro", "luz da rua apagada", "luminaria led apagada", "trocar lampada do poste", "escuridao na rua"]
    },
    {
        "id": "ilum_02",
        "source": _SOURCE,
        "urgency": "URGENTE",
        "category": "iluminacao",
        "title": "Apagões Noturnos em Paradas de Ônibus, Escolas e Áreas de Tráfego Vulnerável",
        "content": (
            "Quando a falta de iluminação atinge locais com alta circulação de pedestres vulneráveis — tais como portas de escolas, creches, "
            "hospitais, estações de metrô/trem e pontos de parada de ônibus —, o chamado é elevado para prioridade URGENTE com prazo de atendimento "
            "reduzido para até 24 horas corridas. A ausência de luminosidade nesses pontos agrava a vulnerabilidade a crimes contra o patrimônio e atropelamentos."
        ),
        "keywords": ["postes apagados", "ponto de onibus", "escola", "poste apagado ponto de onibus", "escuridao na escola", "apagao no ponto", "ponto escuro hospital", "falta de luz ponto de onibus", "rua escura escola"]
    },
    {
        "id": "ilum_03",
        "source": _SOURCE,
        "urgency": "baixa",
        "category": "iluminacao",
        "title": "Luminárias Acesas Durante o Dia por Falha no Relé Fotoelétrico",
        "content": (
            "Lâmpadas ou luminárias LED que permanecem constantemente acesas durante o período diurno com luz solar plena indicam defeito de contato "
            "ou queima do sensor de relé fotoelétrico instalado na base superior da carcaça. Embora não comprometa a segurança viária imediata, o defeito "
            "gera desperdício de energia elétrica e redução prematura da vida útil do equipamento. O prazo normativo para correção é de 48 horas úteis."
        ),
        "keywords": ["lampada acesa de dia", "poste aceso de dia", "rele fotoeletrico", "luz acesa de dia", "desperdicio de energia poste"]
    },
    {
        "id": "ilum_04",
        "source": _SOURCE,
        "urgency": "URGENTE",
        "category": "iluminacao",
        "title": "Postes Metálicos de Iluminação Danificados por Abalroamento e Fiação Exposta",
        "content": (
            "Postes metálicos de iluminação pública ou semafóricos atingidos por colisão de veículos (abalroamento), inclinados com risco de queda "
            "ou com tampa de inspeção aberta na base expondo fios elétricos secundários devem ser atendidos em caráter emergencial em até 4 a 12 horas. "
            "A Ilumina SP realiza o desenergizamento preventivo do circuito secundário, isolamento da base e substituição do braço ou poste avariado."
        ),
        "keywords": ["poste batido", "carro bateu no poste", "poste inclinado", "tampa do poste aberta", "poste de luz quebrado", "poste amassado"]
    }
]
