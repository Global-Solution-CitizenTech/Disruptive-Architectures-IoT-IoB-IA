"""
Base de Conhecimento RAG: Limpeza Urbana, Ecopontos e Gestão de Resíduos Sólidos — PMSP
Fundamentação Legal: Lei Municipal nº 13.478/2002 (Código de Limpeza Urbana de São Paulo)
Órgão Competente: Autoridade Municipal de Limpeza Urbana (AMLURB) e Subprefeituras Regionais
"""
from typing import Dict, Any, List

_SOURCE = "Lei Municipal nº 13.478/2002 (Código de Limpeza Urbana PMSP) e AMLURB"

CHUNKS_LIMPEZA: List[Dict[str, Any]] = [
    {
        "id": "limp_01",
        "source": _SOURCE,
        "urgency": "baixa",
        "category": "limpeza_urbana",
        "title": "Regras de Descarte Gratuito em Ecopontos Municipais",
        "content": (
            "Conforme a Lei Municipal nº 13.478/2002 e as diretrizes da AMLURB, a Cidade de São Paulo disponibiliza mais de 120 unidades de Ecopontos "
            "abertas de segunda a sábado das 6h às 22h e domingos/feriados das 6h às 18h. Todo munícipe tem o direito de entregar GRATUITAMENTE até "
            "1 m³ (um metro cúbico — equivalente a cerca de 20 sacos de 50 litros ou 1 caçamba de caminhonete pequena) de resíduos por dia. "
            "São aceitos: entulho de pequenas reformas da construção civil, sobras de azulejo, cimento e tijolo, restos de poda de jardim, móveis velhos, "
            "madeiras, colchões e materiais recicláveis secos (papel, plástico, vidro, metal). Não são aceitos: lixo orgânico domiciliar, resíduos industriais, "
            "lixo hospitalar ou grandes volumes acima de 1 m³ (que exigem contratação de caçamba cadastrada)."
        ),
        "keywords": ["ecoponto", "jogar entulho", "descarte gratuito", "onde levar entulho", "onde descartar movel velho", "quanto custa ecoponto", "descarte de reforma", "resto de obra"]
    },
    {
        "id": "limp_02",
        "source": _SOURCE,
        "urgency": "alta",
        "category": "limpeza_urbana",
        "title": "Descarte Clandestino de Entulho em Vias Públicas e Penalidades Legais",
        "content": (
            "O descarte irregular de resíduos da construção civil, móveis, terra ou lixo em calçadas, sarjetas, praças e canteiros públicos é crime "
            "ambiental sujeito a apreensão do veículo transportador e aplicação de multa pesada superior a R$ 25.000,00 (vinte e cinco mil reais), "
            "conforme o artigo 161 da Lei nº 13.478/2002. A denúncia realizada no ZelaFix é encaminhada à fiscalização de posturas da Subprefeitura "
            "e à Guarda Civil Metropolitana (GCM) com prazo padrão para recolhimento e higienização mecânica em até 48 horas úteis."
        ),
        "keywords": ["entulho na calcada", "lixo jogado na rua", "descarte irregular", "entulho clandestino", "multa de lixo", "jogaram lixo na esquina", "sobra de obra na rua"]
    },
    {
        "id": "limp_03",
        "source": _SOURCE,
        "urgency": "baixa",
        "category": "limpeza_urbana",
        "title": "Operação Cata-Bagulho e Coleta Programada de Grandes Objetos",
        "content": (
            "A Operação Cata-Bagulho é um serviço gratuito municipal realizado periodicamente aos finais de semana pelas Subprefeituras para recolher "
            "móveis velhos, colchões, eletrodomésticos quebrados, madeiras e sobras de metal que não cabem na coleta domiciliar comum. "
            "Os munícipes devem colocar os materiais na calçada em frente às suas casas até as 7h da manhã do dia programado. O calendário por rua "
            "pode ser consultado no portal da Subprefeitura ou no ZelaFix. O Cata-Bagulho NÃO recolhe entulho de obra, terra ou lixo orgânico."
        ),
        "keywords": ["cata-bagulho", "caminhao cata bagulho", "recolher sofa velho", "pegar geladeira velha", "coleta de movel", "horario cata bagulho"]
    },
    {
        "id": "limp_04",
        "source": _SOURCE,
        "urgency": "media",
        "category": "limpeza_urbana",
        "title": "Limpeza, Capinação e Notificação de Terrenos Baldios Particulares",
        "content": (
            "Proprietários de imóveis não edificados (terrenos baldios) na Cidade de São Paulo são obrigados por lei a mantê-los limpos, capinados, "
            "drenados, fechados com muro de alvenaria e com calçada pavimentada. O acúmulo de mato alto e lixo clandestino gera proliferação de escorpiões, "
            "ratos e mosquitos da dengue (Aedes aegypti). Ao receber o relato, a Subprefeitura vistoria o local em até 5 dias úteis, notifica o proprietário "
            "com prazo de 60 dias para regularização e, em caso de descumprimento, aplica multa e executa limpeza compulsória com cobrança no IPTU."
        ),
        "keywords": ["terreno baldio", "mato alto", "terreno abandonado", "lixo no terreno", "foco de dengue terreno", "dono do terreno", "limpar terreno"]
    }
]
