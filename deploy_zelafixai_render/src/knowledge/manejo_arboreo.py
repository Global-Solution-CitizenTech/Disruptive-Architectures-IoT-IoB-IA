"""
Base de Conhecimento RAG: Manejo Arbóreo, Poda, Remoção de Árvores e Defesa Civil — PMSP
Fundamentação Legal: Lei Municipal nº 17.267/2020 e Portaria SVMA nº 28/2020
"""
from typing import Dict, Any, List

_SOURCE = "Lei Municipal nº 17.267/2020 e Manual de Arborização Urbana SVMA/PMSP"

CHUNKS_MANEJO_ARBOREO: List[Dict[str, Any]] = [
    {
        "id": "arb_01",
        "source": _SOURCE,
        "urgency": "media",
        "category": "manejo_arboreo",
        "title": "Procedimento para Poda Preventiva de Árvores em Logradouros Públicos",
        "content": (
            "A poda de galhos de árvores localizadas em calçadas, canteiros centrais e praças municipais é de competência exclusiva da Prefeitura de São Paulo "
            "(Subprefeituras), sendo terminantemente proibida a poda drástica ou corte por munícipes sem autorização sob pena de crime ambiental (Lei nº 9.605/1998). "
            "A solicitação via ZelaFix gera vistoria por Engenheiro Agrônomo ou Biólogo municipal, que emite laudo técnico fitossanitário no prazo de até 15 dias "
            "úteis, avaliando necessidade de levantamento de copa, desobstrução de luminárias ou remoção de galhos secos."
        ),
        "keywords": ["poda de arvore", "podar galho", "arvore na calcada", "subprefeitura poda", "laudo agronomo", "poda preventiva", "galho tapando luz"]
    },
    {
        "id": "arb_02",
        "source": _SOURCE,
        "urgency": "URGENTE",
        "category": "manejo_arboreo",
        "title": "Galhos em Conflito com a Rede Elétrica Primária (Competência Exclusiva ENEL)",
        "content": (
            "Quando galhos de árvores estão tocando ou próximos à fiação elétrica de média e alta tensão (cabos primários de 13,8 kV) emitindo faíscas, "
            "curto-circuitos ou estalos, o serviço de poda é de competência EXCLUSIVA da distribuidora de energia ENEL Distribuição São Paulo. Equipes da Prefeitura "
            "não podem intervir sem o desligamento técnico programado da rede elétrica devido ao perigo letal de arco voltaico e eletrocussão. "
            "O chamado é direcionado para a central prioritária da concessionária de energia em regime de urgência."
        ),
        "keywords": ["arvore na fiacao", "galho no fio eletrico", "galhos nos fios", "fios eletricos", "faisca no poste", "curto circuito arvore", "enel", "alta tensao arvore", "perigo choque arvore", "faisca"]
    },
    {
        "id": "arb_03",
        "source": _SOURCE,
        "urgency": "URGENTE",
        "category": "manejo_arboreo",
        "title": "Árvore com Risco Iminente de Queda ou Tombamento Sobre Vias e Residências",
        "content": (
            "Árvores de grande porte apresentando inclinação abrupta do tronco, levantamento visível do torrão de raízes, tronco oco com infestação severa "
            "de cupins, rachaduras longitudinais ou podridão fúngica na base configuram RISCO IMINENTE DE TOMBAMENTO. O chamado recebe prioridade URGENTE e "
            "mobiliza vistoria imediata da Coordenadoria Municipal de Defesa Civil (COMPDEC - Telefone 199) e Corpo de Bombeiros (193). As equipes efetuam o isolamento "
            "do perímetro e a remoção preventiva do exemplar arbóreo para proteger a vida dos cidadãos."
        ),
        "keywords": ["arvore caindo", "risco de queda arvore", "tronco oco", "arvore inclinada", "raiz levantada", "defesa civil", "bombeiros 193", "arvore perigosa"]
    },
    {
        "id": "arb_04",
        "source": _SOURCE,
        "urgency": "URGENTE",
        "category": "manejo_arboreo",
        "title": "Remoção Emergencial de Árvore Caída em Logradouro Público Após Temporal",
        "content": (
            "Após eventos climáticos severos e vendavais, árvores ou galhos de grande porte caídos bloqueando total ou parcialmente o tráfego viário, "
            "atingindo fiação ou obstruindo garagens e residências recebem despacho em comboio de emergência: Corpo de Bombeiros para desencarceramento e corte com motosserra, "
            "CET para desvio de trânsito, ENEL para restabelecimento elétrico e Subprefeitura para trituração e recolhimento dos troncos no menor tempo possível."
        ),
        "keywords": ["arvore caiu", "arvore bloqueando rua", "arvore na pista", "temporal arvore", "desobstrucao de via", "motosserra bombeiros"]
    }
]
