"""
Base de Conhecimento RAG: Limpeza Urbana, Resíduos Sólidos, Ecopontos e Cata-Bagulho — PMSP
Fundamentação Legal: Lei Municipal nº 13.478/2002 (Código de Limpeza Urbana de São Paulo)
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
            "A Cidade de São Paulo disponibiliza mais de 120 Ecopontos operados pela Prefeitura de São Paulo onde qualquer munícipe pode entregar "
            "gratuitamente até 1 m³ (um metro cúbico) de resíduos por dia, o que equivale a aproximadamente uma caixa d'água de 1.000 litros ou cerca "
            "de 20 sacos de entulho de reforma residencial. São aceitos: sobras de construção civil (tijolos, concreto, argamassa), móveis velhos, "
            "madeiras, colchões, eletrodomésticos desmontados e sobras de podas de jardim. NÃO são aceitos lixo orgânico doméstico, resíduos industriais, "
            "pneus ou lixo hospitalar/químico. O serviço é 100% gratuito de segunda a sábado das 06h às 22h e domingos e feriados das 06h às 18h."
        ),
        "keywords": ["ecoponto", "jogar entulho", "onde jogar entulho", "descarte gratuito", "sobra de obra", "metro cubico", "moveis velhos", "1 metro cubico gratis"]
    },
    {
        "id": "limp_02",
        "source": _SOURCE,
        "urgency": "alta",
        "category": "limpeza_urbana",
        "title": "Descarte Clandestino de Entulho em Vias Públicas e Multas Previstas",
        "content": (
            "O descarte irregular de entulho, lixo ou terra em calçadas, canteiros centrais e praças públicas é infração gravíssima com base no artigo 161 "
            "da Lei Municipal nº 13.478/2002. A multa atualizada supera o valor de R$ 25.000,00, além da apreensão do veículo ou caçamba transportadora. "
            "Ao registrar denúncia no ZelaFix, a equipe de fiscalização de posturas da Subprefeitura é enviada ao local para autuação, e o consórcio de "
            "limpeza urbana (EcoUrbis ou Loga) realiza a remoção mecânica dos resíduos no prazo de 24 a 48 horas úteis."
        ),
        "keywords": ["entulho na calcada", "lixo jogado na rua", "descarte clandestino", "multa de entulho", "lei 13478", "fiscalizacao subprefeitura", "ecourbis", "loga"]
    },
    {
        "id": "limp_03",
        "source": _SOURCE,
        "urgency": "baixa",
        "category": "limpeza_urbana",
        "title": "Operação Cata-Bagulho e Coleta Agendada de Inservíveis",
        "content": (
            "A Operação Cata-Bagulho é realizada gratuitamente pelas Subprefeituras aos finais de semana, percorrendo roteiros pré-definidos de vias para "
            "recolher materiais inservíveis (sofás, armários, mesas, eletrodomésticos quebrados e madeiras). O morador deve colocar os itens na calçada até "
            "as 07h do dia divulgado no calendário municipal do portal da Prefeitura. O Cata-Bagulho não recolhe entulho de construção civil e lixo orgânico domiciliar."
        ),
        "keywords": ["cata-bagulho", "recolher sofa", "moveis velhos", "calendario cata-bagulho", "subprefeitura recolhe armario", "inserviveis"]
    },
    {
        "id": "limp_04",
        "source": _SOURCE,
        "urgency": "alta",
        "category": "limpeza_urbana",
        "title": "Terrenos Baldios com Acúmulo de Lixo e Foco de Dengue",
        "content": (
            "O acúmulo de lixo, entulho, pneus e garrafas com água parada em terrenos baldios particulares representa grave ameaça à saúde pública "
            "como criadouro do mosquito Aedes aegypti (transmissor de Dengue, Zika e Chikungunya). A Subprefeitura e a Vigilância Sanitária Municipal (COVAS) "
            "emitem intimação com prazo de 30 dias para que o proprietário efetue a limpeza completa, desratização e muramento do lote, sob aplicação de "
            "pesadas multas sucessivas previstas no Código de Posturas Urbanas."
        ),
        "keywords": ["terreno baldio", "foco de dengue", "lixo no terreno", "mato alto", "aedes aegypti", "vigilancia sanitaria", "intimacao proprietario"]
    }
]
