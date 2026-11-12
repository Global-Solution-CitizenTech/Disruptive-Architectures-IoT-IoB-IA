"""
Base de Conhecimento RAG: Direitos do Cidadão, Ouvidoria, Calçadas e FAQ ZelaFix — PMSP
Fundamentação Legal: Carta de Serviços PMSP, Decreto Municipal nº 58.611/2019 e Portal SP156
Órgão Competente: Ouvidoria Geral do Município de São Paulo e Subprefeituras Regionais
"""
from typing import Dict, Any, List

_SOURCE = "Carta de Serviços ao Cidadão PMSP, Decreto nº 58.611/2019 e Ouvidoria Geral"

CHUNKS_DIREITOS_CIDADAO: List[Dict[str, Any]] = [
    {
        "id": "faq_01",
        "source": _SOURCE,
        "urgency": "baixa",
        "category": "direitos_cidadao",
        "title": "Como Funciona o ZelaFix e o Acompanhamento de Protocolos",
        "content": (
            "O ZelaFix é uma plataforma colaborativa CitizenTech (ODS 11) que conecta os relatos dos cidadãos diretamente aos órgãos públicos "
            "municipais competentes (Subprefeituras, Ilumina SP, CET, Defesa Civil e Sabesp). Ao cadastrar uma ocorrência com fotos, categoria e localização "
            "GPS, a IA Generativa do ZelaFix realiza a triagem técnica imediata, analisa o enquadramento regulatório com base nos decretos de São Paulo e "
            "atribui um número único de protocolo oficial. O cidadão acompanha em tempo real cada mudança de status (Aberto, Em Vistoria, Executado e Concluído)."
        ),
        "keywords": ["como funciona o zelafix", "acompanhar protocolo", "abrir chamado", "status do chamado", "citizentech", "zeladoria colaborativa", "como abrir ocorrencia"]
    },
    {
        "id": "faq_02",
        "source": _SOURCE,
        "urgency": "baixa",
        "category": "direitos_cidadao",
        "title": "Mobilização Comunitária e Priorização Coletiva por Apoios (+1)",
        "content": (
            "No ZelaFix, outros moradores e transeuntes do mesmo bairro podem confirmar ocorrências já relatadas através do botão de apoio comunitário '+1'. "
            "Quanto mais cidadãos apoiarem o chamado, maior se torna o índice de gravidade coletiva (Social Urgency Score). Chamados com mais de 25 apoios "
            "comunitários são automaticamente promovidos para a fila de alta prioridade técnica da Subprefeitura, evidenciando o impacto no bem-estar da comunidade."
        ),
        "keywords": ["apoio da vizinhanca", "apoio comunitario", "voto no chamado", "prioridade coletiva", "social urgency", "mais pessoas reclamando", "apoios vizinhos"]
    },
    {
        "id": "faq_03",
        "source": _SOURCE,
        "urgency": "media",
        "category": "direitos_cidadao",
        "title": "Regras de Calçadas Acessíveis e Responsabilidade de Manutenção (Passeio Livre)",
        "content": (
            "Conforme a Lei Municipal nº 15.442/2011 e o Decreto Municipal nº 58.611/2019 (Passeio Livre), a conservação e reforma da calçada em frente a "
            "imóveis particulares é de responsabilidade primária do proprietário do imóvel. A calçada deve possuir faixa livre de circulação contínua e "
            "desimpedida de no mínimo 1,20 metro de largura, sem degraus, com piso antiderrapante e inclinação transversal máxima de 2% para garantir "
            "a acessibilidade de cadeirantes, idosos e carrinhos de bebê. Calçadas de praças, canteiros e prédios públicos municipais são de manutenção direta da Subprefeitura."
        ),
        "keywords": ["calcada quebrada", "reforma de calcada", "calcada acessivel", "decreto 58611", "passeio livre", "cadeirante calcada", "responsabilidade calcada", "consertar calcada"]
    },
    {
        "id": "faq_04",
        "source": _SOURCE,
        "urgency": "media",
        "category": "direitos_cidadao",
        "title": "Descumprimento de Prazos (SLA) e Recurso à Ouvidoria Geral do Município",
        "content": (
            "Caso a solicitação de serviço municipal (como tapa-buraco, limpeza de bueiro ou poda) ultrapasse o prazo regulamentar fixado em decreto "
            "sem justificativa técnica fundamentada no sistema, o cidadão tem o direito cívico de registrar recurso formal na Ouvidoria Geral do Município de "
            "São Paulo (canal SP156). A Ouvidoria instaura processo de apuração com prazo peremptório de 10 dias úteis para resposta circunstanciada da Subprefeitura."
        ),
        "keywords": ["ouvidoria sp156", "prefeitura nao cumpriu prazo", "reclamar da subprefeitura", "recurso atraso", "ouvidoria geral", "chamado vencido", "prazo estourado"]
    }
]
