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
    "buraco": ["asfalto", "cratera", "pavimento", "tapa_buraco", "pista", "faixa", "reparo", "via", "pavimentacao"],
    "buracos": ["asfalto", "cratera", "pavimento", "tapa_buraco", "pista", "faixa", "reparo", "via", "pavimentacao"],
    "cratera": ["buraco", "asfalto", "pavimento", "afundamento", "via", "veicular", "acidente", "urgente"],
    "asfalto": ["pavimento", "buraco", "cratera", "recapeamento", "tapa_buraco", "cbuq", "subprefeitura"],
    "pavimento": ["asfalto", "buraco", "cratera", "recapeamento", "tapa_buraco", "cbuq", "subprefeitura"],
    "recapeamento": ["asfalto", "pavimentacao", "tapa_buraco", "subprefeitura", "cbuq", "via"],
    "tapa_buraco": ["buraco", "asfalto", "pavimentacao", "decreto", "subprefeitura", "cbuq"],

    # Iluminação Pública e Rede Elétrica
    "fio": ["fiacao", "eletrica", "enel", "curto", "faisca", "poste", "alta_tensao", "choque"],
    "fios": ["fiacao", "eletrica", "enel", "curto", "faisca", "poste", "alta_tensao", "choque"],
    "fiacao": ["fio", "fios", "eletrica", "enel", "curto", "faisca", "alta_tensao", "rede_eletrica"],
    "eletrico": ["energia", "enel", "fiacao", "fio", "alta_tensao", "choque"],
    "eletricos": ["energia", "enel", "fiacao", "fio", "alta_tensao", "choque"],
    "faisca": ["curto", "circuito", "fio", "eletrico", "enel", "fogo"],
    "faiscas": ["curto", "circuito", "fio", "eletrico", "enel", "fogo"],
    "poste": ["iluminacao", "lampada", "apagado", "escuro", "led", "luz", "ilumina_sp", "fiacao"],
    "postes": ["iluminacao", "lampada", "apagado", "escuro", "led", "luz", "ilumina_sp", "fiacao"],
    "iluminacao": ["poste", "lampada", "apagada", "escuro", "led", "ilumina_sp", "seguranca"],
    "lampada": ["poste", "iluminacao", "queimada", "apagada", "led", "ilumina_sp", "luminaria"],
    "luminaria": ["poste", "iluminacao", "lampada", "led", "ilumina_sp", "fotocelula"],
    "escuro": ["iluminacao", "poste", "lampada", "ponto_escuro", "apagado", "noite", "seguranca"],
    "escuridao": ["iluminacao", "poste", "lampada", "ponto_escuro", "apagado", "noite", "seguranca"],
    "sem_luz": ["iluminacao", "poste", "lampada", "apagado", "ponto_escuro", "ilumina_sp"],
    "apagado": ["iluminacao", "poste", "lampada", "queimada", "ponto_escuro", "semaforo"],
    "led": ["iluminacao", "lampada", "luminaria", "ilumina_sp", "modernizacao"],

    # Drenagem, Bueiros e Enchentes
    "bueiro": ["boca_lobo", "alagamento", "enchente", "drenagem", "galeria", "entupido", "tampa"],
    "bueiros": ["boca_lobo", "alagamento", "enchente", "drenagem", "galeria", "entupido", "tampa"],
    "boca_lobo": ["bueiro", "alagamento", "enchente", "drenagem", "hidrojateamento", "entupido"],
    "boca_de_lobo": ["bueiro", "boca_lobo", "alagamento", "enchente", "drenagem", "entupido"],
    "alagamento": ["enchente", "bueiro", "boca_lobo", "drenagem", "chuva", "inundacao", "risco"],
    "alagado": ["alagamento", "enchente", "bueiro", "drenagem", "chuva", "inundacao"],
    "enchente": ["alagamento", "bueiro", "drenagem", "chuva", "defesa_civil", "inundacao"],
    "entupido": ["bueiro", "boca_lobo", "desobstrucao", "hidrojateamento", "limpeza", "sedimentos"],
    "entupida": ["bueiro", "boca_lobo", "desobstrucao", "hidrojateamento", "limpeza", "sedimentos"],
    "tampa": ["bueiro", "boca_lobo", "quebrada", "furtada", "ferro_fundido", "risco", "queda"],

    # Limpeza Urbana, Resíduos e Ecopontos
    "lixo": ["entulho", "descarte", "residuo", "ecoponto", "cata_bagulho", "limpeza", "cacamba"],
    "entulho": ["lixo", "descarte", "obra", "reforma", "ecoponto", "residuos", "cacamba", "metro_cubico"],
    "ecoponto": ["entulho", "descarte", "gratuito", "sobras", "madeira", "moveis", "amlurb"],
    "ecopontos": ["entulho", "descarte", "gratuito", "sobras", "madeira", "moveis", "amlurb"],
    "descarte": ["lixo", "entulho", "ecoponto", "clandestino", "multa", "irregular", "cata_bagulho"],
    "cata_bagulho": ["moveis", "colchao", "eletrodomesticos", "subprefeitura", "calendario", "coleta"],
    "terreno": ["baldio", "lixo", "dengue", "mato", "notificacao", "fiscalizacao", "proprietario"],
    "mato": ["terreno", "baldio", "lixo", "dengue", "capinacao", "fiscalizacao", "subprefeitura"],

    # Manejo Arbóreo e Vegetação
    "arvore": ["poda", "galho", "queda", "arborizacao", "enel", "fiacao", "raiz", "tombamento"],
    "arvores": ["poda", "galho", "queda", "arborizacao", "enel", "fiacao", "raiz", "tombamento"],
    "poda": ["arvore", "galho", "subprefeitura", "enel", "fiacao", "laudo", "agronomo"],
    "podar": ["arvore", "poda", "galho", "subprefeitura", "enel", "fiacao", "agronomo"],
    "galho": ["arvore", "poda", "fiacao", "eletrica", "enel", "queda", "risco"],
    "galhos": ["arvore", "poda", "fiacao", "eletrica", "enel", "queda", "risco"],
    "tombamento": ["arvore", "queda", "defesa_civil", "bombeiros", "risco", "tronco"],

    # Sinalização e Trânsito (CET)
    "semaforo": ["sinal", "transito", "cet", "cruzamento", "amarelo", "apagado", "farol", "defeito"],
    "semaforos": ["sinal", "transito", "cet", "cruzamento", "amarelo", "apagado", "farol", "defeito"],
    "farol": ["semaforo", "sinal", "transito", "cet", "cruzamento", "amarelo"],
    "sinal": ["semaforo", "farol", "transito", "cet", "placa", "faixa"],
    "placa": ["sinalizacao", "transito", "cet", "pare", "sentido", "vandalizada", "derrubada"],
    "zebrada": ["faixa_pedestres", "pintura", "cet", "travessia", "sinalizacao"],
    "pedestre": ["faixa_pedestres", "travessia", "cet", "calcada", "sinalizacao"],
    "pedestres": ["faixa_pedestres", "travessia", "cet", "calcada", "sinalizacao"],
    "faixa": ["pedestres", "faixa_pedestres", "zebrada", "pintura", "cet", "sinalizacao"],
    "faixa_pedestres": ["zebrada", "pintura", "cet", "escola", "hospital", "atropelamento", "sinalizacao"],

    # Saneamento e Abastecimento (Sabesp)
    "vazamento": ["agua", "esgoto", "sabesp", "adutora", "cano", "infiltracao", "hidrometro", "195"],
    "agua": ["vazamento", "sabesp", "adutora", "cano", "cavalete", "pressao", "falta"],
    "esgoto": ["vazamento", "sabesp", "extravasamento", "coletora", "mau_cheiro", "risco_biologico"],
    "adutora": ["vazamento", "rompimento", "sabesp", "solapamento", "cratera", "emergencia"],

    # Calçadas e Acessibilidade
    "calcada": ["acessibilidade", "pedestre", "degrau", "piso_tatil", "rampa", "cadeirante", "buraco"],
    "calcadas": ["acessibilidade", "pedestre", "degrau", "piso_tatil", "rampa", "cadeirante", "buraco"],
    "acessibilidade": ["calcada", "cadeirante", "piso_tatil", "rampa", "pcd", "idoso", "mobilidade"],

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
    Aplica o dicionário de sinônimos e termos técnicos municipais sem duplicar tokens.
    Verifica tanto o token completo (incluindo bigramas como 'boca_lobo') quanto suas partes.
    """
    expandidos: List[str] = list(tokens)
    vistos: Set[str] = set(tokens)
    for t in tokens:
        candidatos: List[str] = []
        if t in MAPA_EXPANSAO_SEMANTICA:
            candidatos.extend(MAPA_EXPANSAO_SEMANTICA[t])
        if "_" in t:
            for parte in t.split("_"):
                if parte in MAPA_EXPANSAO_SEMANTICA:
                    candidatos.extend(MAPA_EXPANSAO_SEMANTICA[parte])
        for c in candidatos:
            if c not in vistos:
                vistos.add(c)
                expandidos.append(c)
    return expandidos

def limpar_texto_mobile(texto: str) -> str:
    """
    Higieniza a saída gerada por LLM para renderização limpa no app Mobile React Native:
    - Remove eventuais tags <think>...</think>.
    - Limite de segurança de 50.000 caracteres.
    - Remove asteriscos brutos de negrito/itálico Markdown (** ou *).
    - Converte tabelas Markdown com pipes (|) em listas com marcadores simples ('• ').
    - Remove delimitadores desnecessários de blocos de código.
    """
    if not texto:
        return ""
    texto = texto[:50000]
    texto = re.sub(r"<think>.*?</think>", "", texto, flags=re.DOTALL | re.IGNORECASE)
    texto = re.sub(r"<think>.*$", "", texto, flags=re.DOTALL | re.IGNORECASE)

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
