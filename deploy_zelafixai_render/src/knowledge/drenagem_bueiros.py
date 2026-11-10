"""
Base de Conhecimento RAG: Drenagem Urbana, Bueiros, Bocas de Lobo e Galerias Pluviais — PMSP
Fundamentação Legal: Decreto Municipal nº 57.545/2016 e Diretrizes Técnicas da SIURB
"""
from typing import Dict, Any, List

_SOURCE = "Decreto Municipal nº 57.545/2016 e Manual de Drenagem Urbana SIURB"

CHUNKS_DRENAGEM: List[Dict[str, Any]] = [
    {
        "id": "dren_01",
        "source": _SOURCE,
        "urgency": "alta",
        "category": "drenagem",
        "title": "Desobstrução e Limpeza Preventiva de Bocas de Lobo e Bueiros",
        "content": (
            "De acordo com o Decreto Municipal nº 57.545/2016 e as diretrizes da Secretaria Municipal de Infraestrutura Urbana e Obras (SIURB), "
            "as bocas de lobo e bueiros de captação de águas pluviais passam por limpeza periódica e corretiva. A intervenção envolve a retirada de "
            "terra, folhas e resíduos sólidos que obstruem a grelha e a caixa de retenção. Em casos de entupimento severo com acúmulo de sedimentos "
            "endurecidos, utiliza-se caminhão combinado equipado com bomba de hidrojateamento de alta pressão e sucção a vácuo para liberar os ramais de ligação até a galeria principal."
        ),
        "keywords": ["bueiro entupido", "boca de lobo entupida", "limpeza de bueiro", "desobstrucao", "hidrojateamento", "ramal de drenagem", "lixo no bueiro"]
    },
    {
        "id": "dren_02",
        "source": _SOURCE,
        "urgency": "URGENTE",
        "category": "drenagem",
        "title": "Bueiro Entupido em Ponto Crítico Sujeito a Alagamento e Enchente",
        "content": (
            "Quando um bueiro ou boca de leão está completamente entupido em vias mapeadas pelo Centro de Gerenciamento de Emergências (CGE) "
            "como pontos críticos de alagamento, a prioridade é classificada como URGENTE. O atendimento da Subprefeitura deve ocorrer em até 24 horas "
            "para restabelecer a capacidade de escoamento hidráulico antes da ocorrência de chuvas fortes, prevenindo retenção de veículos, transbordamento "
            "de pistas e inundação de residências no entorno."
        ),
        "keywords": ["risco de alagamento", "ponto de enchente", "chuva forte", "bueiro transbordando", "alagamento da rua", "cge sp", "prioridade drenagem"]
    },
    {
        "id": "dren_03",
        "source": _SOURCE,
        "urgency": "URGENTE",
        "category": "drenagem",
        "title": "Tampa de Bueiro Furtada ou Grelha Quebrada com Risco de Queda",
        "content": (
            "A ausência ou quebra de tampas de ferro fundido e grelhas de bocas de lobo representa risco gravíssimo de morte ou lesão corporal severa "
            "para pedestres, pessoas com deficiência, ciclistas e motociclistas. A equipe de plantão da Subprefeitura deve instalar sinalização de proteção "
            "imediata com cerquilhas e cavaletes refletores no local em até 4 horas após o registro do chamado. A reposição definitiva da tampa ou "
            "grelha antivandalismo deve ser concluída no prazo máximo regulamentar de 12 a 24 horas."
        ),
        "keywords": ["tampa de bueiro furtada", "grelha de bueiro quebrada", "bueiro aberto", "buraco sem tampa", "risco de queda", "ferro fundido", "perigo pedestre"]
    },
    {
        "id": "dren_04",
        "source": _SOURCE,
        "urgency": "alta",
        "category": "drenagem",
        "title": "Inspeção e Manutenção Estrutural de Galerias de Águas Pluviais",
        "content": (
            "Quando a água da chuva causa afundamento contínuo da calçada ou do asfalto sem que o bueiro visível esteja cheio, suspeita-se de "
            "ruptura de galeria pluvial subterrânea ou colapso da tubulação de concreto. A engenharia da SIURB executa inspeção com câmera de vídeo "
            "robotizada (inspeção periscópica/CCTV subterrânea) para localizar a fratura estrutural da galeria e planejar obras de drenagem pesada e escoramento."
        ),
        "keywords": ["galeria pluvial", "tubulacao de drenagem rompida", "afundamento de bueiro", "infiltracao subterranea", "siurb", "engenharia de drenagem"]
    }
]
