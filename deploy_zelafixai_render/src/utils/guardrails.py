"""
Utilitários de Proteção de Dados (LGPD) e Guardrails de Segurança — ZelaFix AI
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)
"""
import re
from src.utils.text import normalizar_texto

_RE_CPF = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")
_RE_CARTAO = re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b")
_RE_EMAIL = re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b")
_RE_TELEFONE = re.compile(r"(?:\+55\s?)?(?:\(\d{2}\)\s?|\b\d{2}\s+)9?\d{4}[-\s]\d{4}\b")

_RE_PROMPT_INJECTION = re.compile(
    r"(?:ignor[ae]\w*\s+(?:todas?\s+as?\s+|as?\s+|previous\s+|all\s+)?(?:instruc\w*|regras?|directions?|prompts?)"
    r"|(?:revel[ae]\w*|mostr[ae]\w*|exib[ae]\w*|print|dump|leak)\s+(?:o\s+|seu\s+|your\s+|the\s+)?(?:system\s+prompt|prompt\s+(?:de\s+|do\s+)?sistema|api[\s_]?key|oracle[\s_]?password|credencia\w*)"
    r"|\b(?:jailbreak|dan\s+mode|aja\s+como\s+dan|developer\s+mode)\b)",
    re.IGNORECASE,
)


def sanitizar_lgpd(texto: str) -> str:
    """
    Mascara CPF, cartão de crédito, e-mail e telefone antes da inferência,
    persistência ou retorno, assegurando conformidade com a LGPD.
    """
    if not texto:
        return ""
    mascarado = _RE_CARTAO.sub("[DADO PESSOAL ANONIMIZADO]", texto)
    mascarado = _RE_CPF.sub("[DADO PESSOAL ANONIMIZADO]", mascarado)
    mascarado = _RE_EMAIL.sub("[DADO PESSOAL ANONIMIZADO]", mascarado)
    mascarado = _RE_TELEFONE.sub("[DADO PESSOAL ANONIMIZADO]", mascarado)
    return mascarado


def detectar_prompt_injection(texto: str) -> bool:
    """Detecta tentativas explícitas de prompt injection, jailbreak ou extração de segredos."""
    if not texto:
        return False
    return bool(_RE_PROMPT_INJECTION.search(normalizar_texto(texto)))
