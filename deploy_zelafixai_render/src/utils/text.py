"""
Utilitários: Sanitização Textual para Mobile, Tokenização e Expansão Semântica Urbana — ZelaFix AI
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)
"""
import re
import unicodedata
from typing import List, Dict, Set

# Conjunto de stopwords em português para filtragem de ruído textual
STOPWORDS_PT: Set[str] = {
    "a", "o", "as", "os", "de", "da", "do", "das", "dos", "em", "no", "na", "nos", "nas",
    "por", "para", "com", "sem", "sob", "sobre", "um", "uma", "uns", "umas", "e", "ou",
    "mas", "que", "se", "como", "eu", "ele", "ela", "eles", "elas", "meu", "minha", "meus",
    "minhas", "seu", "sua", "seus", "suas", "esse", "essa", "esses", "essas", "este", "esta",
    "estes", "estas", "aquele", "aquela", "aquilo", "oque", "pra", "pro", "pras", "pros",
    "ta", "esta", "estao", "estava", "tem", "qual", "quais", "quem", "foi", "era", "ser",
    "ter", "ha", "muito", "pouco", "bem", "mais", "menos", "ja", "ainda", "so", "sozinha",
    "aqui", "ali", "la", "fazer", "faco", "faz", "fazem", "dar", "dou", "da", "dao"
}

# Dicionário de expansão semântica urbana de zeladoria municipal da Cidade de São Paulo
MAPA_EXPANSAO_SEMANTICA: Dict[str, List[str]] = {
    # Pavimentação, Asfalto e Buracos
    "buraco": ["asfalto", "cratera", "pavimento", "tapa-buraco", "pista", "faixa", "reparo", "via", "pavimentacao"],
    "buracos": ["asfalto", "cratera", "pavimento", "tapa-buraco", "pista", "faixa", "reparo", "via", "pavimentacao"],
    "cratera": ["buraco", "asfalto", "pavimento", "afundamento", "via", "veicular", "acidente", "urgente"],
    "asfalto": ["pavimento", "buraco", "cratera", "recapeamento", "tapa-buraco", "cbuq", "subprefeitura"],
    "pavimento": ["asfalto", "buraco", "cratera", "recapeamento", "tapa-buraco", "cbuq", "subprefeitura"],
    "recapeamento": ["asfalto", "pavimentacao", "tapa-buraco", "subprefeitura", "cbuq", "via"],
    "tapa-buraco": ["buraco", "asfalto", "pavimentacao", "decreto", "subprefeitura", "cbuq"],

    # Iluminação Pública e Rede Elétrica
    "fio": ["fiacao", "eletrica", "enel", "curto", "faisca", "poste", "alta tensao", "choque"],
    "fios": ["fiacao", "eletrica", "enel", "curto", "faisca", "poste", "alta tensao", "choque"],
    "fiacao": ["fio", "fios", "eletrica", "enel", "curto", "faisca", "alta tensao", "rede eletrica"],
    "eletrico": ["energia", "enel", "fiacao", "fio", "alta tensao", "choque"],
    "eletricos": ["energia", "enel", "fiacao", "fio", "alta tensao", "choque"],
    "faisca": ["curto", "circuito", "fio", "eletrico", "enel", "fogo"],
    "faiscas": ["curto", "circuito", "fio", "eletrico", "enel", "fogo"],
    "poste": ["iluminacao", "lampada", "apagado", "escuro", "led", "luz", "ilumina sp", "fiacao"],
    "postes": ["iluminacao", "lampada", "apagado", "escuro", "led", "luz", "ilumina sp", "fiacao"],
    "iluminacao": ["poste", "lampada", "apagada", "escuro", "led", "ilumina sp", "seguranca"],
    "lampada": ["poste", "iluminacao", "queimada", "apagada", "led", "ilumina sp", "luminaria"],
    "luminaria": ["poste", "iluminacao", "lampada", "led", "ilumina sp", "fotocelula"],
    "escuro": ["iluminacao", "poste", "lampada", "ponto escuro", "apagado", "noite", "seguranca"],
    "apagado": ["iluminacao", "poste", "lampada", "queimada", "ponto escuro", "semaforo"],
    "led": ["iluminacao", "lampada", "luminaria", "ilumina sp", "modernizacao"],

    # Drenagem, Bueiros e Enchentes
    "bueiro": ["boca de lobo", "alagamento", "enchente", "drenagem", "galeria", "entupido", "tampa"],
    "bueiros": ["boca de lobo", "alagamento", "enchente", "drenagem", "galeria", "entupido", "tampa"],
    "boca de lobo": ["bueiro", "alagamento", "enchente", "drenagem", "hidrojateamento", "entupido"],
    "alagamento": ["enchente", "bueiro", "boca de lobo", "drenagem", "chuva", "inundacao", "risco"],
    "enchente": ["alagamento", "bueiro", "drenagem", "chuva", "defesa civil", "inundacao"],
    "entupido": ["bueiro", "boca de lobo", "desobstrucao", "hidrojateamento", "limpeza", "sedimentos"],
    "tampa": ["bueiro", "boca de lobo", "quebrada", "furtada", "ferro fundido", "risco", "queda"],

    # Limpeza Urbana, Resíduos e Ecopontos
    "lixo": ["entulho", "descarte", "residuo", "ecoponto", "cata-bagulho", "limpeza", "cacamba"],
    "entulho": ["lixo", "descarte", "obra", "reforma", "ecoponto", "residuos", "cacamba", "metro cubico"],
    "ecoponto": ["entulho", "descarte", "gratuito", "entulho", "sobras", "madeira", "moveis", "amlurb"],
    "ecopontos": ["entulho", "descarte", "gratuito", "entulho", "sobras", "madeira", "moveis", "amlurb"],
    "descarte": ["lixo", "entulho", "ecoponto", "clandestino", "multa", "irregular", "cata-bagulho"],
    "cata-bagulho": ["moveis", "colchao", "eletrodomesticos", "subprefeitura", "calendario", "coleta"],
    "terreno": ["baldio", "lixo", "dengue", "mato", "notificacao", "fiscalizacao", "proprietario"],

    # Manejo Arbóreo e Vegetação
    "arvore": ["poda", "galho", "queda", "arborizacao", "enel", "fiacao", "raiz", "tombamento"],
    "arvores": ["poda", "galho", "queda", "arborizacao", "enel", "fiacao", "raiz", "tombamento"],
    "poda": ["arvore", "galho", "subprefeitura", "enel", "fiacao", "laudo", "agronomo"],
    "galho": ["arvore", "poda", "fiacao", "eletrica", "enel", "queda", "risco"],
    "galhos": ["arvore", "poda", "fiacao", "eletrica", "enel", "queda", "risco"],
    "tombamento": ["arvore", "queda", "defesa civil", "bombeiros", "risco", "tronco"],

    # Sinalização e Trânsito (CET)
    "semaforo": ["sinal", "transito", "cet", "cruzamento", "amarelo", "apagado", "farol", "defeito"],
    "semaforos": ["sinal", "transito", "cet", "cruzamento", "amarelo", "apagado", "farol", "defeito"],
    "farol": ["semaforo", "sinal", "transito", "cet", "cruzamento", "amarelo"],
    "sinal": ["semaforo", "farol", "transito", "cet", "placa", "faixa"],
    "placa": ["sinalizacao", "transito", "cet", "pare", "sentido", "vandalizada", "derrubada"],
    "faixa": ["pedestres", "pintura", "cet", "escola", "hospital", "atropelamento", "sinalizacao"],

    # Saneamento e Abastecimento (Sabesp)
    "vazamento": ["agua", "esgoto", "sabesp", "adutora", "cano", "infiltracao", "hidrometro", "195"],
    "agua": ["vazamento", "sabesp", "adutora", "cano", "cavalete", "pressao", "falta"],
    "esgoto": ["vazamento", "sabesp", "extravasamento", "coletora", "mau cheiro", "risco biologico"],
    "adutora": ["vazamento", "rompimento", "sabesp", "solapamento", "cratera", "emergencia"],

    # Calçadas e Acessibilidade
    "calcada": ["acessibilidade", "pedestre", "degrau", "piso tatil", "rampa", "cadeirante", "buraco"],
    "calcadas": ["acessibilidade", "pedestre", "degrau", "piso tatil", "rampa", "cadeirante", "buraco"],
    "acessibilidade": ["calcada", "cadeirante", "piso tatil", "rampa", "pcd", "idoso", "mobilidade"],

    # Urgência e Risco
    "urgente": ["risco", "perigo", "acidente", "emergencia", "grave", "queda", "morte"],
    "perigo": ["urgente", "risco", "acidente", "emergencia", "grave", "choque"],
    "choque": ["fio", "eletrico", "energizado", "alta tensao", "bombeiros", "enel", "morte"]
}

def normalizar_texto(texto: str) -> str:
    """
    Remove acentuações, converte para minúsculas e remove caracteres especiais
    para correspondência uniforme. Limita defensivamente a 10.000 caracteres.
    """
    if not texto:
        return ""
    texto_seguro = texto[:10000]
    texto_sem_acento = unicodedata.normalize("NFKD", texto_seguro).encode("ASCII", "ignore").decode("utf-8")
    return re.sub(r'[^a-zA-Z0-9\s]', ' ', texto_sem_acento).lower().strip()

def tokenizar_com_ngrams(texto: str, n_max: int = 2) -> List[str]:
    """
    Tokeniza o texto em palavras e gera n-grams (unigramas e bigramas),
    removendo pontuações e stopwords.
    """
    if not texto:
        return []
    
    texto_norm = normalizar_texto(texto)
    palavras = [p for p in texto_norm.split() if p not in STOPWORDS_PT and len(p) > 2]
    
    tokens = list(palavras)
    if n_max >= 2 and len(palavras) >= 2:
        for i in range(len(palavras) - 1):
            tokens.append(f"{palavras[i]}_{palavras[i+1]}")
            
    return tokens

def expansao_semantica_urbana(tokens: List[str]) -> List[str]:
    """
    Aplica o dicionário de sinônimos e termos técnicos municipais para enriquecer a query.
    """
    expandidos = list(tokens)
    for t in tokens:
        raiz = t.split("_")[0]
        if raiz in MAPA_EXPANSAO_SEMANTICA:
            expandidos.extend(MAPA_EXPANSAO_SEMANTICA[raiz])
    return expandidos

def limpar_texto_mobile(texto: str) -> str:
    """
    Higieniza a saída gerada por LLM para renderização limpa no app Mobile React Native:
    - Limite de segurança de 50.000 caracteres.
    - Remove asteriscos brutos de negrito/itálico Markdown (** ou *).
    - Converte tabelas Markdown com pipes (|) em listas com marcadores simples ('• ').
    - Remove delimitadores desnecessários de blocos de código.
    """
    if not texto:
        return ""
    texto = texto[:50000]

    # Converte linhas de tabelas com | para itens de lista
    linhas = texto.split("\n")
    linhas_tratadas = []
    em_tabela = False
    
    for linha in linhas:
        l_strip = linha.strip()
        # Se for divisor de tabela Markdown (|---|---|)
        if re.match(r"^\|?[\s\-:]+(\|[\s\-:]+)+\|?$", l_strip):
            em_tabela = True
            continue
        
        # Se for linha de dados de tabela (| col1 | col2 |)
        if l_strip.startswith("|") and l_strip.endswith("|"):
            em_tabela = True
            celulas = [c.strip() for c in l_strip.split("|") if c.strip()]
            if celulas:
                if len(celulas) >= 2:
                    linhas_tratadas.append(f"• {celulas[0]}: {celulas[1]}")
                else:
                    linhas_tratadas.append(f"• {celulas[0]}")
            continue
        
        linhas_tratadas.append(linha)

    texto_ajustado = "\n".join(linhas_tratadas)

    # Remove asteriscos de markdown
    texto_ajustado = re.sub(r"\*\*([^*]+)\*\*", r"\1", texto_ajustado)
    texto_ajustado = re.sub(r"\*([^*]+)\*", r"\1", texto_ajustado)
    
    # Remove blocos de código ``` se restarem
    texto_ajustado = re.sub(r"```[a-zA-Z]*\n?", "", texto_ajustado)
    texto_ajustado = texto_ajustado.replace("```", "")

    # Normaliza múltiplas linhas vazias consecutivas
    texto_ajustado = re.sub(r"\n{3,}", "\n\n", texto_ajustado)

    return texto_ajustado.strip()
