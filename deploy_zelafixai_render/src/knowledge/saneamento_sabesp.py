"""
Base de Conhecimento RAG: Saneamento Básico, Vazamento de Água e Esgoto — Sabesp / ARSESP
Fundamentação Legal: Regulamento Geral da ARSESP e Contrato de Programa Sabesp
"""
from typing import Dict, Any, List

_SOURCE = "Regulamento Geral ARSESP e Central de Operações Sabesp (195)"

CHUNKS_SANEAMENTO: List[Dict[str, Any]] = [
    {
        "id": "sab_01",
        "source": _SOURCE,
        "urgency": "URGENTE",
        "category": "saneamento",
        "title": "Rompimento de Adutora e Vazamento de Água Potável Limpa na Via Pública",
        "content": (
            "Vazamentos de água potável no leito carroçável ou passeio público causados por rompimento de adutoras, tubulações mestras ou ramais prediais "
            "provocam perda inaceitável de recurso hídrico tratado e causam o solapamento invisível do subleito asfáltico, gerando risco iminente de abertura "
            "de crateras súbitas que tragam veículos. O chamado é classificado com severidade URGENTE e aciona a Central de Emergências da Companhia de "
            "Saneamento Básico do Estado de São Paulo (Sabesp - Telefone 195) com prazo regulatório para contenção de vazamento entre 4 a 12 horas."
        ),
        "keywords": ["vazamento de agua", "cano quebrado", "agua jorrando na rua", "adutora rompida", "sabesp 195", "vazamento de agua limpa", "agua potavel rua"]
    },
    {
        "id": "sab_02",
        "source": _SOURCE,
        "urgency": "alta",
        "category": "saneamento",
        "title": "Extravasamento de Esgoto Sanitário a Céu Aberto e Risco Biológico",
        "content": (
            "O retorno ou extravasamento de efluentes de esgoto cloacal em vias públicas, galerias ou caixas de inspeção exala odores fétidos intensos e "
            "representa grave risco biológico de transmissão de patógenos (leptospirose, hepatite, cólera e gastroenterites). A concessionária Sabesp "
            "mobiliza caminhão de desobstrução e sucção a vácuo para desentupir a rede coletora no prazo máximo regulamentar de até 24 horas úteis."
        ),
        "keywords": ["esgoto a ceu aberto", "vazamento de esgoto", "mau cheiro na rua", "poco de visita esgoto", "sabesp esgoto", "risco biologico esgoto"]
    },
    {
        "id": "sab_03",
        "source": _SOURCE,
        "urgency": "media",
        "category": "saneamento",
        "title": "Cavalete do Hidrômetro com Vazamento ou Danificado",
        "content": (
            "Danos estruturais, fissuras ou vazamentos no cavalete de ligação de água situado no alinhamento predial do imóvel exigem intervenção técnica "
            "da Sabesp. Se o vazamento estiver localizado antes do medidor (hidrômetro), a responsabilidade da manutenção e conserto é integral e gratuita da "
            "concessionária. O prazo padrão para agendamento de vistoria e substituição do conjunto de conexão é de 24 a 48 horas úteis."
        ),
        "keywords": ["vazamento no hidrometro", "cavalete quebrado", "relogio de agua vazando", "vazamento no cavalete", "sabesp hidrometro"]
    }
]
