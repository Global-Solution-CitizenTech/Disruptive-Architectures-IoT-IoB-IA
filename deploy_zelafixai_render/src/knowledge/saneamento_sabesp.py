"""
Base de Conhecimento RAG: Saneamento Básico, Vazamentos e Redes de Distribuição — Sabesp
Fundamentação Legal: Regulamento Geral da ARSESP e Contrato de Concessão de Serviços Sabesp
Órgão Competente: Companhia de Saneamento Básico do Estado de São Paulo (Central 195)
"""
from typing import Dict, Any, List

_SOURCE = "Regulamento Geral ARSESP e Contrato de Programa Sabesp (Central 195)"

CHUNKS_SANEAMENTO: List[Dict[str, Any]] = [
    {
        "id": "sab_01",
        "source": _SOURCE,
        "urgency": "URGENTE",
        "category": "saneamento",
        "title": "Vazamento de Água Potável na Rua com Risco de Solapamento do Subleito",
        "content": (
            "Vazamentos em redes distribuidoras e adutoras de água tratada no leito viário ou passeio público são de competência exclusiva da Sabesp. "
            "A fuga contínua de água sob alta pressão carrega o solo fino da base viária (efeito 'piping'), provocando solapamento oculto do asfalto "
            "e abertura súbita de grandes crateras. Conforme norma da ARSESP, vazamentos visíveis na via pública devem ser contidos em até 12 horas corridas "
            "após a notificação pelo canal Sabesp 195 ou encaminhamento direto via ZelaFix."
        ),
        "keywords": ["cano estourado", "cano quebrado", "vazamento de agua", "adutora rompida", "agua jorrando", "agua limpa na rua", "sabesp vazamento", "cano furado"]
    },
    {
        "id": "sab_02",
        "source": _SOURCE,
        "urgency": "URGENTE",
        "category": "saneamento",
        "title": "Vazamento de Esgoto Sanitário a Céu Aberto e Risco à Saúde Pública",
        "content": (
            "O vazamento, extravasamento ou refluxo de esgoto sanitário bruto em via pública, sarjeta ou calçada configura grave risco à saúde pública "
            "e contaminação biológica por vetores (leptospirose, cólera, hepatite e coliformes fecais). A Sabesp tem a obrigação regulamentar de enviar "
            "equipe técnica de desobstrução e saneamento em até 24 horas para reparo da rede coletora e aplicação de cal/desinfetante clorado no leito contaminado."
        ),
        "keywords": ["esgoto vazando", "esgoto a ceu aberto", "cheiro de esgoto", "cano de esgoto", "poco de esgoto transbordando", "fezes na rua", "mau cheiro na rua"]
    },
    {
        "id": "sab_03",
        "source": _SOURCE,
        "urgency": "alta",
        "category": "saneamento",
        "title": "Vazamento no Cavalete e Ramal Predial de Ligação de Água",
        "content": (
            "A responsabilidade da Sabesp estende-se desde a tubulação distribuidora central da rua até a saída do hidrômetro localizado no cavalete "
            "predial do imóvel. Vazamentos identificados no cavalete, no registro de entrada ou na calçada antes do hidrômetro geram desperdício de recurso "
            "hídrico sem faturamento para o munícipe. O atendimento para substituição do hidrômetro ou estancamento do ramal tem SLA padrão de 24 horas úteis."
        ),
        "keywords": ["cavalete vazando", "hidrometro quebrado", "relogio de agua", "ramal de agua", "vazamento no hidrometro", "registro de agua da rua"]
    }
]
