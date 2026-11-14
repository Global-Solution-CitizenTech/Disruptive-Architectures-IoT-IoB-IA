"""
Utilitários Textuais: Normalização ASCII e Higienização Mobile — ZelaFix AI
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)
"""
import re
import unicodedata


def normalizar_texto(texto: str) -> str:
    """
    Remove acentuações, converte para minúsculas e remove caracteres especiais
    para comparações uniformes. Limita defensivamente a 10.000 caracteres.
    """
    if not texto:
        return ""
    texto_seguro = texto[:10000]
    texto_sem_acento = unicodedata.normalize("NFKD", texto_seguro).encode("ASCII", "ignore").decode("utf-8")
    return re.sub(r"[^a-zA-Z0-9\s]", " ", texto_sem_acento).lower().strip()


def limpar_texto_mobile(texto: str) -> str:
    """
    Higieniza a saída gerada pela LLM para renderização limpa no app Mobile React Native:
    - Limite de segurança de 50.000 caracteres.
    - Converte tabelas Markdown com pipes (|) em listas simples com '• '.
    - Remove asteriscos de negrito/itálico Markdown (** ou *) e cercas de código ```.
    """
    if not texto:
        return ""
    texto = texto[:50000]

    linhas = texto.split("\n")
    linhas_tratadas = []

    for linha in linhas:
        l_strip = linha.strip()
        if re.match(r"^\|?[\s\-:]+(\|[\s\-:]+)+\|?$", l_strip):
            continue

        if "|" in l_strip:
            celulas = [c.strip() for c in l_strip.split("|") if c.strip()]
            if celulas:
                if len(celulas) >= 2:
                    linhas_tratadas.append(f"• {celulas[0]}: {' — '.join(celulas[1:])}")
                else:
                    linhas_tratadas.append(f"• {celulas[0]}")
            continue

        linhas_tratadas.append(linha)

    texto_ajustado = "\n".join(linhas_tratadas)
    texto_ajustado = re.sub(r"^\s*\*\s+", "• ", texto_ajustado, flags=re.MULTILINE)
    texto_ajustado = re.sub(r"\*\*(.+?)\*\*", r"\1", texto_ajustado, flags=re.DOTALL).replace("**", "")
    texto_ajustado = re.sub(r"\*([^*\n]+)\*", r"\1", texto_ajustado)
    texto_ajustado = re.sub(r"```[a-zA-Z]*\n?", "", texto_ajustado).replace("```", "")
    texto_ajustado = texto_ajustado.replace("|", "—")
    texto_ajustado = re.sub(r"\n{3,}", "\n\n", texto_ajustado)

    return texto_ajustado.strip()
