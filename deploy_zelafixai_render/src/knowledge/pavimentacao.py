"""
Base de Conhecimento RAG: Pavimentação Asfáltica e Operação Tapa-Buraco — PMSP
Fundamentação Legal: Decreto Municipal nº 59.150/2019 e Manuais Técnicos da SMSUB
Órgão Competente: Secretaria Municipal das Subprefeituras (SMSUB) e Subprefeituras Regionais
"""
from typing import Dict, Any, List

_SOURCE = "Decreto Municipal nº 59.150/2019 (Regulamento de Pavimentação PMSP) e SMSUB"

CHUNKS_PAVIMENTACAO: List[Dict[str, Any]] = [
    {
        "id": "pav_01",
        "source": _SOURCE,
        "urgency": "alta",
        "category": "pavimentacao",
        "title": "Procedimento Técnico Padrão de Tapa-Buraco com Recorte Geométrico",
        "content": (
            "Conforme o Decreto Municipal nº 59.150/2019 e as normas técnicas da Secretaria Municipal das Subprefeituras (SMSUB), "
            "o reparo de buracos no pavimento asfáltico deve seguir rigorosamente a metodologia de recorte geométrico retangular ou "
            "quadrado com serra clipper ao redor do defeito. O material desagregado deve ser totalmente removido com ar comprimido ou varrição. "
            "Em seguida, aplica-se a pintura de ligação com emulsão asfáltica catiônica e o enchimento com Concreto Betuminoso Usinado a Quente (CBUQ). "
            "A compactação deve ser realizada com placa vibratória ou rolo compactador tandem vibratório para garantir nivelamento perfeito com a pista existente."
        ),
        "keywords": ["tapa-buraco", "buraco na rua", "corte geometrico", "serra clipper", "cbuq", "asfalto quente", "compactacao", "subprefeitura", "reparo asfalto"]
    },
    {
        "id": "pav_02",
        "source": _SOURCE,
        "urgency": "alta",
        "category": "pavimentacao",
        "title": "Prazos Normativos de SLA para Reparo de Pavimento Viário",
        "content": (
            "Os chamados de tapa-buraco em vias locais e secundárias possuem prazo padrão regulamentar de atendimento de 24 a 48 horas úteis "
            "após a vistoria técnica da Subprefeitura regional competente. Para vias estruturais de tráfego intenso, corredores e faixas exclusivas "
            "de transporte coletivo (ônibus), o atendimento deve ser priorizado em regime de urgência operacional em até 24 horas, visando evitar "
            "acidentes com motociclistas, ciclistas e danos à frota municipal."
        ),
        "keywords": ["prazo tapa-buraco", "sla buraco", "tempo reparo asfalto", "prazo asfalto", "24 horas", "48 horas", "corredor de onibus", "via arterial"]
    },
    {
        "id": "pav_03",
        "source": _SOURCE,
        "urgency": "URGENTE",
        "category": "pavimentacao",
        "title": "Crateras Viárias com Risco Iminente de Colapso e Danos Estruturais",
        "content": (
            "Quando a ocorrência envolve buraco de grande dimensão (cratera com profundidade superior a 10 cm, afundamento súbito do leito ou "
            "solapamento decorrente de fuga de solo subterrânea), o caso é categorizado com severidade URGENTE. A equipe técnica da Subprefeitura "
            "deve realizar sinalização de emergência com cavaletes e cones em conjunto com a CET em até 4 horas, interditando parcialmente ou totalmente "
            "a faixa afetada até a conclusão da estabilização da base de bica corrida e recapeamento asfáltico."
        ),
        "keywords": ["cratera", "buraco fundo", "afundamento de pista", "solapamento", "colapso do asfalto", "perigo de acidente", "interdicao de faixa"]
    },
    {
        "id": "pav_04",
        "source": _SOURCE,
        "urgency": "media",
        "category": "pavimentacao",
        "title": "Fiscalização de Valas de Concessionárias de Serviços Públicos e Garantia",
        "content": (
            "Segundo o artigo 14 do Decreto Municipal nº 59.150/2019, toda intervenção no leito viário ou calçada executada por concessionárias "
            "(energia, gás, telecomunicações) deve ser recomposta com o mesmo padrão asfáltico pré-existente pela própria empresa executora. "
            "A concessionária é responsável pela garantia e manutenção da vala recomposta pelo período de 5 (cinco) anos. Caso o asfalto ceda ou "
            "apresente depressão, a Subprefeitura notifica a concessionária com imposição de multa e prazo de 48 horas para correção imediata."
        ),
        "keywords": ["vala na rua", "obra na rua", "concessionaria asfalto", "recomposicao de vala", "garantia do asfalto", "afundamento vala"]
    },
    {
        "id": "pav_05",
        "source": _SOURCE,
        "urgency": "media",
        "category": "pavimentacao",
        "title": "Programa de Recapeamento Asfáltico Contínuo de Vias Estruturais",
        "content": (
            "Quando um logradouro público apresenta degradação generalizada da capa asfáltica (múltiplas trincas tipo couro de jacaré, panelas "
            "sucessivas e desgaste da vida útil do pavimento), a solução não é a operação tapa-buraco pontual, mas a inclusão no Programa de "
            "Recapeamento Contínuo da Cidade de São Paulo. O processo envolve fresagem a frio da camada superficial desgastada (3 a 5 cm) e "
            "aplicação de novo CBUQ polimerizado com nivelamento das tampas de poços de visita."
        ),
        "keywords": ["recapeamento", "fresagem", "asfalto novo", "rua esburacada inteira", "asfalto todo quebrado", "recapear"]
    }
]
