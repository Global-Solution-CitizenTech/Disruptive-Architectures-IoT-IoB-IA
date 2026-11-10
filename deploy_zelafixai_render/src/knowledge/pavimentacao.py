"""
Base de Conhecimento RAG: Pavimentação Asfáltica e Operação Tapa-Buraco — PMSP
Fundamentação Legal: Decreto Municipal nº 59.150/2019 e Manuais Técnicos da SMSUB
"""
from typing import Dict, Any, List

_SOURCE = "Decreto Municipal nº 59.150/2019 e Manual de Pavimentação PMSP"

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
        "keywords": ["tapa-buraco", "buraco na rua", "corte geometrico", "serra clipper", "cbuq", "asfalto quente", "compactacao", "subprefeitura"]
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
        "keywords": ["prazo tapa-buraco", "sla buraco", "tempo reparo asfalto", "24 horas", "48 horas", "corredor de onibus", "via arterial"]
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
            "a faixa afetada até a conclusão da estabilização da base e recapeamento."
        ),
        "keywords": ["cratera", "buraco fundo", "afundamento de pista", "solapamento", "colapso do asfalto", "perigo de acidente", "interdicao de faixa"]
    },
    {
        "id": "pav_04",
        "source": _SOURCE,
        "urgency": "media",
        "category": "pavimentacao",
        "title": "Recomposição de Valas Abertas por Concessionárias de Serviços Públicos",
        "content": (
            "Segundo o artigo 14 do Decreto Municipal nº 59.150/2019, toda intervenção no leito viário ou calçada executada por concessionárias "
            "de serviços públicos (Sabesp, Comgás, Enel ou operadoras de telecomunicações) exige autorização prévia (CONVIAS). A concessionária "
            "é legalmente responsável pela recomposição integral do pavimento no mesmo padrão original e detém garantia obrigatória de 5 anos sobre o "
            "trecho recuperado. Se a vala afundar ou abrir buraco, a concessionária é notificada pela Subprefeitura para refazer o serviço em 48 horas sob pena de multa diária."
        ),
        "keywords": ["vala aberta", "buraco de concessionaria", "sabesp", "comgas", "enel", "recomposicao de vala", "garantia de 5 anos", "convias"]
    },
    {
        "id": "pav_05",
        "source": _SOURCE,
        "urgency": "baixa",
        "category": "pavimentacao",
        "title": "Programa de Recapeamento Asfáltico Contínuo e Microrevestimento",
        "content": (
            "Em ruas com desgaste generalizado, trincamento em couro de jacaré (fadiga do revestimento) ou deformações plásticas contínuas, "
            "a operação tapa-buraco pontual torna-se ineficaz. Nesses casos, o trecho é cadastrado no Programa de Recapeamento da Prefeitura de São Paulo "
            "(SMSUB), onde é realizada a fresagem completa da camada asfáltica degradada e aplicação de nova camada de CBUQ ou SMA (Stone Matrix Asphalt) "
            "com polímero para alta durabilidade e drenabilidade."
        ),
        "keywords": ["recapeamento", "asfalto novo", "rua inteira esburacada", "fresagem", "desgaste asfalto", "programa recapeamento"]
    }
]
