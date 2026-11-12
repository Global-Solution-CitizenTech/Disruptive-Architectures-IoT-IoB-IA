"""
Base de Conhecimento RAG: Manejo Arbóreo, Poda, Queda e Remoção de Árvores — PMSP
Fundamentação Legal: Lei Municipal nº 17.267/2020 e Portaria SVMA nº 28/2020
Órgãos Competentes: Subprefeituras Regionais (SVMA), ENEL Distribuição SP e Defesa Civil (199)
"""
from typing import Dict, Any, List

_SOURCE = "Lei Municipal nº 17.267/2020 (Manejo Arbóreo PMSP) e SVMA"

CHUNKS_MANEJO_ARBOREO: List[Dict[str, Any]] = [
    {
        "id": "arb_01",
        "source": _SOURCE,
        "urgency": "media",
        "category": "manejo_arboreo",
        "title": "Solicitação de Poda Preventiva e Equilíbrio de Copa em Logradouros Públicos",
        "content": (
            "Conforme a Lei Municipal nº 17.267/2020, o manejo e a poda de árvores situadas em passeios públicos, calçadas, praças e canteiros "
            "centrais competem exclusivamente à Subprefeitura Regional, mediante vistoria agronômica e emissão de laudo técnico fitossanitário. "
            "É expressamente proibido ao munícipe realizar a poda por conta própria, sob pena de autuação por crime ambiental. O serviço contempla "
            "poda de desobstrução de luminárias, limpeza de galhos secos e equilíbrio de copa, com prazo de atendimento de até 72 horas após a vistoria."
        ),
        "keywords": ["poda de arvore", "podar arvore", "galhos altos", "cortar galho", "arvore na calcada", "limpeza de copa", "arvore grande na rua"]
    },
    {
        "id": "arb_02",
        "source": _SOURCE,
        "urgency": "URGENTE",
        "category": "manejo_arboreo",
        "title": "Galhos em Contato com Fiação da Rede Elétrica Primária (Competência ENEL)",
        "content": (
            "Quando os galhos ou a copa da árvore estão em contato direto com a rede elétrica aérea de média ou alta tensão, provocando faíscas, "
            "curto-circuito, oscilação de energia ou rompimento de cabos condutores, a competência é EXCLUSIVA da concessionária ENEL Distribuição São Paulo. "
            "Equipes da Subprefeitura não podem podar árvores energizadas por risco fatal de eletrocussão. A ENEL tem prazo regulamentar emergencial "
            "de até 12 horas para desligamento da rede no circuito e execução do corte dos galhos em conflito com a fiação."
        ),
        "keywords": ["arvore na fiacao", "galho no fio", "arvore encostando no fio eletrico", "fios com faisca", "galho dando curto", "enel poda", "fio eletrico arvore"]
    },
    {
        "id": "arb_03",
        "source": _SOURCE,
        "urgency": "URGENTE",
        "category": "manejo_arboreo",
        "title": "Árvore com Risco Iminente de Tombamento, Tronco Oco ou Raízes Expostas",
        "content": (
            "Árvores de grande porte com inclinação acentuada do fuste superior a 15 graus, raízes arrancadas pelo vento, tronco oco com infestação severa "
            "por cupins/fungos ou rachaduras estruturais na base configuram situação de emergência pública por perigo iminente de queda sobre veículos ou imóveis. "
            "A Defesa Civil Municipal (Central 199) e os engenheiros agrônomos da Subprefeitura realizam vistoria imediata, isolamento do perímetro e autorização "
            "expressa para supressão (remoção total) preventiva do espécime vegetal."
        ),
        "keywords": ["arvore inclinada", "arvore caindo", "tronco oco", "raiz arrancada", "arvore podre", "risco de queda arvore", "defesa civil arvore"]
    },
    {
        "id": "arb_04",
        "source": _SOURCE,
        "urgency": "URGENTE",
        "category": "manejo_arboreo",
        "title": "Remoção Emergencial de Árvore Tombada com Bloqueio de Via Pública",
        "content": (
            "Após temporais e vendavais, a ocorrência de árvore tombada bloqueando totalmente a pista de rolamento ou atingindo veículos/redes exige "
            "operação conjunta imediata do Corpo de Bombeiros (193), CET para desvio do tráfego e equipe de poda da Subprefeitura para seccionamento com motosserra, "
            "desobstrução da via em até 4 a 12 horas e recolhimento dos resíduos lenhosos triturados para compostagem."
        ),
        "keywords": ["arvore caiu na rua", "arvore tombada", "arvore bloqueando a rua", "arvore caiu no carro", "arvore cada na tempestade", "desobstruir rua arvore"]
    }
]
