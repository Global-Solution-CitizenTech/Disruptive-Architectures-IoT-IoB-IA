"""
Utilitários de Proteção de Dados (LGPD) — ZelaFix AI
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)
"""
import re

def sanitizar_lgpd(texto: str) -> str:
    """
    Mascara números de CPF ou dados potencialmente sensíveis antes da persistência ou retorno,
    assegurando conformidade com a LGPD para a plataforma CitizenTech.
    """
    if not texto:
        return ""
    # Mascara CPF: 000.000.000-00 ou 11 dígitos sequenciais
    texto_mascarado = re.sub(r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b', '[DADO PESSOAL ANONIMIZADO]', texto)
    # Mascara números de cartão de crédito (16 dígitos)
    texto_mascarado = re.sub(r'\b(?:\d{4}[-\s]?){3}\d{4}\b', '[DADO PESSOAL ANONIMIZADO]', texto_mascarado)
    return texto_mascarado
