"""
Base de Conhecimento RAG: Sinalização Viária, Semáforos e Engenharia de Tráfego — CET-SP
Fundamentação Legal: Código de Trânsito Brasileiro (Lei nº 9.503/1997) e Manuais Técnicos da CET-SP
Órgão Competente: Companhia de Engenharia de Tráfego (CET-SP / SMT)
"""
from typing import Dict, Any, List

_SOURCE = "Código de Trânsito Brasileiro e Procedimentos Operacionais CET-SP"

CHUNKS_SINALIZACAO: List[Dict[str, Any]] = [
    {
        "id": "cet_01",
        "source": _SOURCE,
        "urgency": "URGENTE",
        "category": "sinalizacao_transito",
        "title": "Falha Semafórica, Foco Queimado e Semáforo Apagado em Cruzamento Viário",
        "content": (
            "A manutenção e operação dos semáforos na Cidade de São Paulo é de competência exclusiva da Companhia de Engenharia de Tráfego (CET). "
            "A ocorrência de cruzamento com semáforo totalmente apagado, piscando em amarelo contínuo, em curto-circuito ou com queima de foco vermelho "
            "constitui risco extremo de colisões transversais e atropelamentos de pedestres. A central da CET despacha operadores de trânsito em até "
            "2 horas para ordenação manual do fluxo e técnicos de manutenção eletroeletrônica com SLA máximo de reparo definitivo em até 4 horas corridas."
        ),
        "keywords": ["semaforo apagado", "farol quebrado", "farol apagado", "semaforo quebrado", "cruzamento sem farol", "foco do semaforo queimado", "farol amarelo piscando", "cet semaforo"]
    },
    {
        "id": "cet_02",
        "source": _SOURCE,
        "urgency": "alta",
        "category": "sinalizacao_transito",
        "title": "Reposição de Placas de Regulamentação Furtadas ou Danificadas (Placa PARE)",
        "content": (
            "A sinalização vertical de regulamentação (especialmente placas R-1 'PARE', R-2 'Dê a Preferência' e sinalização de sentido proibido) "
            "é vital para a segurança viária em cruzamentos sem semáforo. Placas furtadas, pichadas, retorcidas por vandalismo ou encobertas por vegetação "
            "provocam desorientação de condutores e colisões graves. A CET realiza a reposição física e fixação de nova chapa refletiva no suporte "
            "metálico no prazo regulamentar de até 24 horas úteis."
        ),
        "keywords": ["placa de pare", "placa roubada", "placa arrancada", "placa de transito", "placa pare quebrada", "placa de esquina", "placa de regulamentacao"]
    },
    {
        "id": "cet_03",
        "source": _SOURCE,
        "urgency": "media",
        "category": "sinalizacao_transito",
        "title": "Revitalização e Pintura de Faixas de Pedestres e Sinalização Horizontal",
        "content": (
            "A sinalização horizontal de trânsito, que inclui a demarcação e pintura de faixas de travessia de pedestres (padrão zebrado), "
            "linhas de retenção e faixas de pedestre em frente a escolas, creches e hospitais, compete à Divisão de Sinalização Horizontal da CET. "
            "A repintura com tinta termoplástica refletiva de alta durabilidade e microesferas de vidro é programada para execução em horário "
            "noturno para minimizar impactos no tráfego, com prazo de atendimento de até 72 horas úteis."
        ),
        "keywords": ["faixa de pedestres", "faixa de pedestre", "faixa apagada", "pintura de faixa de pedestre", "faixa zebrada", "travessia de pedestre", "faixa de pedestre apagada", "sinalizacao horizontal"]
    }
]
