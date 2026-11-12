"""
Base de Conhecimento RAG: Drenagem Urbana, Bueiros e Prevenção de Alagamentos — PMSP
Fundamentação Legal: Decreto Municipal nº 57.545/2016 e Diretrizes Técnicas SIURB
Órgão Competente: Secretaria Municipal de Infraestrutura Urbana e Obras (SIURB) e Subprefeituras
"""
from typing import Dict, Any, List

_SOURCE = "Decreto Municipal nº 57.545/2016 (Drenagem Urbana PMSP) e SIURB"

CHUNKS_DRENAGEM: List[Dict[str, Any]] = [
    {
        "id": "dren_01",
        "source": _SOURCE,
        "urgency": "alta",
        "category": "drenagem",
        "title": "Limpeza, Desobstrução Manual e Hidrojateamento de Bocas de Lobo",
        "content": (
            "De acordo com o Decreto Municipal nº 57.545/2016, a conservação das bocas de lobo e bueiros para drenagem pluvial compete às "
            "Subprefeituras Regionais. O serviço consiste na abertura da tampa ou grelha, remoção mecânica e manual de detritos sólidos, lixo e folhas "
            "acumulados na caixa de retenção, seguida de sucção e hidrojateamento com caminhão de alta pressão para desobstrução do ramal de ligação "
            "até a galeria principal. O prazo padrão para limpeza de rotina é de até 48 horas úteis após a solicitação."
        ),
        "keywords": ["bueiro entupido", "limpeza de bueiro", "boca de lobo entupida", "desobstruir bueiro", "hidrojateamento", "terra no bueiro", "folhas no bueiro"]
    },
    {
        "id": "dren_02",
        "source": _SOURCE,
        "urgency": "URGENTE",
        "category": "drenagem",
        "title": "Bocas de Leão e Pontos Críticos com Risco Iminente de Alagamento",
        "content": (
            "Em logradouros mapeados pelo Plano de Contingência para Chuvas de Verão da PMSP e em pontos com histórico crônico de alagamento viário, "
            "a ocorrência de boca de lobo ou boca de leão transbordando água pluvial é tratada com severidade URGENTE (SLA máximo de 24 horas). "
            "A retenção inadequada de águas pluviais gera bolsões d'água na pista de rolamento, riscos de aquaplanagem veicular e refluxo para calçadas e imóveis lindeiros."
        ),
        "keywords": ["bueiro transbordando", "alagamento na rua", "enchente", "boca de leao", "ponto de alagamento", "agua empossada", "agua de chuva"]
    },
    {
        "id": "dren_03",
        "source": _SOURCE,
        "urgency": "URGENTE",
        "category": "drenagem",
        "title": "Reposição Imediata de Tampas e Grelhas de Bueiro Furtadas ou Quebradas",
        "content": (
            "A ausência, quebra ou furto de tampas de concreto e grelhas de ferro fundido em bocas de lobo configura risco iminente de acidente grave, "
            "queda fatal de pedestres e danos estruturais a rodas e pneus de veículos. O protocolo municipal determina que a Subprefeitura deve efetuar "
            "a sinalização e isolamento do perímetro em até 4 horas e a reposição física da tampa/grelha em no máximo 12 a 24 horas corridas."
        ),
        "keywords": ["tampa de bueiro", "roubo de tampa", "bueiro aberto", "tampa quebrada", "grelha de ferro", "queda pedestre bueiro", "buraco de bueiro"]
    },
    {
        "id": "dren_04",
        "source": _SOURCE,
        "urgency": "alta",
        "category": "drenagem",
        "title": "Manutenção Estrutural de Galerias de Águas Pluviais e Poços de Visita",
        "content": (
            "Danos estruturais profundos, tais como abatimento de solo sobre a rede de microdrenagem, trincas nas paredes de alvenaria das caixas "
            "de captação ou colapso de tubos de concreto subterrâneos, exigem intervenção de engenharia pesada pela SIURB/Subprefeitura. "
            "A equipe realiza inspeção com câmara de vídeo subterrânea e escavação para reconstrução da galeria com recomposição de bica corrida e pavimento."
        ),
        "keywords": ["galeria pluvial", "galeria de agua", "galeria de agua pluvial", "calcada afundando", "afundando perto da galeria", "poco de visita", "tubulacao pluvial", "colapso drenagem"]
    }
]
