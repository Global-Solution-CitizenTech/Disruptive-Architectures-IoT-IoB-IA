"""
Base de Conhecimento RAG: Sinalização Viária, Semáforos e Engenharia de Tráfego — CET-SP
Fundamentação Legal: Código de Trânsito Brasileiro (CTB - Lei Federal nº 9.503/1997) e Manuais CET
"""
from typing import Dict, Any, List

_SOURCE = "Manuais Técnicos da CET-SP e Código de Trânsito Brasileiro (CTB)"

CHUNKS_SINALIZACAO: List[Dict[str, Any]] = [
    {
        "id": "cet_01",
        "source": _SOURCE,
        "urgency": "URGENTE",
        "category": "sinalizacao_transito",
        "title": "Semáforo Apagado, Quebrado ou em Amarelo Piscante em Cruzamento",
        "content": (
            "A falha no funcionamento de conjunto semafórico (lâmpadas apagadas, foco verde e vermelho queimados, lentes desalinhadas ou oscilando "
            "em amarelo intermitente) em cruzamentos de vias públicas é tratada como EMERGÊNCIA OPERACIONAL DE TRÂNSITO pela Companhia de Engenharia "
            "de Tráfego (CET-SP). O defeito acarreta perigo iminente de abalroamento transversal entre veículos e atropelamento de pedestres. "
            "O chamado dispara envio de agente de trânsito em motocicleta para orientação manual do fluxo e equipe de manutenção semafórica com "
            "SLA de atendimento prioritário entre 2 a 4 horas (Central CET 156 / 1188)."
        ),
        "keywords": ["semaforo quebrado", "semaforo apagado", "farol quebrado", "sinal quebrado", "semaforo piscando amarelo", "cruzamento perigoso", "cet", "transito sp"]
    },
    {
        "id": "cet_02",
        "source": _SOURCE,
        "urgency": "alta",
        "category": "sinalizacao_transito",
        "title": "Placa de Trânsito Derrubada, Danificada ou Vandalizada (Regulamentação)",
        "content": (
            "A ausência, torção ou vandalismo em placas de trânsito de regulamentação obrigatória — tais como Placa R-1 (Parada Obrigatória - PARE), "
            "R-2 (Dê a Preferência), R-3 (Sentido Proibido) ou restrição de velocidade máxima — compromete a segurança viária e a legalidade das autuações "
            "de trânsito. A CET programa a reposição ou desamassamento do poste e refletivo no prazo regulamentar de 24 a 48 horas úteis."
        ),
        "keywords": ["placa de transito quebrada", "placa pare derrubada", "placa arrancada", "placa vandalizada", "sinalizacao vertical", "cet placas"]
    },
    {
        "id": "cet_03",
        "source": _SOURCE,
        "urgency": "media",
        "category": "sinalizacao_transito",
        "title": "Repintura de Faixa de Pedestres e Sinalização Horizontal Próxima a Escolas",
        "content": (
            "A sinalização horizontal viária, em especial a faixa zebrada de pedestres e as inscrições de 'DEVAGAR - ESCOLA' e 'ÁREA HOSPITALAR', "
            "sofre desgaste natural por abrasão dos pneus veiculares e intempéries. Chamados solicitando reforço na pintura são encaminhados para a gerência "
            "de sinalização da CET para inclusão no cronograma de pintura noturna com tinta termoplástica refletiva de alta resistência no prazo de 10 a 15 dias."
        ),
        "keywords": ["faixa de pedestres apagada", "pintura de faixa", "escola sinalizacao", "atravessar a rua", "cet faixa", "sinalizacao horizontal"]
    }
]
