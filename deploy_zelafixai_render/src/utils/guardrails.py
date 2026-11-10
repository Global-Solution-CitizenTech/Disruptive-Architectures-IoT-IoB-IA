"""
Utilitários: Guardrails de Segurança Urbana, Risco Vital, Anti-Evasão de Escopo e LGPD — ZelaFix AI
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)
"""
import re
from src.utils.text import normalizar_texto

TERMOS_EMERGENCIA_VITAL = [
    "fio de alta tensao", "fio caido no chao", "fio dando choque", "choque eletrico na rua",
    "cabo rompido faisca", "poste caido pegando fogo", "arvore caindo em cima da casa",
    "deslizamento de terra", "desabamento de encosta", "cratera engolindo carro",
    "pessoas soterradas", "alagamento com correnteza arrastando", "adutora rompida inundando casas"
]

TERMOS_PROGRAMACAO_OFFTOPIC = [
    "inverter uma lista", "inverter lista", "em python", "codigo em python", "código em python",
    "funcao em python", "função em python", "script em python", "programacao", "programação",
    "algoritmo", "javascript", "linguagem python", "def ", "print(", "reverse()", "vetor",
    "matriz", "codigo java", "código java", "script", "desenvolva um codigo", "crie um codigo"
]

def detectar_emergencia_vital(texto: str) -> bool:
    """
    Verifica se a ocorrência urbana relatada envolve risco iminente de morte ou catástrofe física.
    """
    texto_norm = normalizar_texto(texto)
    # Detecta termos compostos de emergência vital
    if any(termo in texto_norm for termo in TERMOS_EMERGENCIA_VITAL):
        return True
    
    # Detecta combinações críticas de risco elétrico ou de colapso
    tem_eletricidade = any(k in texto_norm for k in ["fio", "poste", "cabo", "alta tensao"])
    tem_choque = any(k in texto_norm for k in ["choque", "faisca", "fogo", "energizado", "eletrocussao"])
    if tem_eletricidade and tem_choque:
        return True

    return False

def montar_resposta_emergencia_vital() -> str:
    """
    Gera a resposta padronizada de emergência com acionamento dos órgãos de socorro público.
    """
    return (
        "🚨 ALERTA DE EMERGÊNCIA VITAL MUNICIPAL!\n\n"
        "A situação relatada apresenta RISCO IMINENTE À VIDA e à integridade física dos cidadãos!\n\n"
        "• AFASTE-SE IMEDIATAMENTE do local e mantenha outras pessoas a uma distância segura mínima de 15 metros.\n"
        "• NUNCA toque em poças d'água, cabos elétricos caídos ou estruturas metálicas próximas.\n\n"
        "📞 ACIONAMENTO DE EMERGÊNCIA IMEDIATO:\n"
        "• Corpo de Bombeiros: Ligue 193 (Emergências e resgate com risco à vida)\n"
        "• Defesa Civil Municipal: Ligue 199 (Vistorias emergenciais, deslizamentos e temporais)\n"
        "• Concessionária ENEL: Ligue 0800 72 72 196 (Desligamento emergencial de rede elétrica)\n\n"
        "O ZelaFix gerou um sinal de prioridade URGENTE com alerta especial para a central operacional."
    )

def detectar_pedido_programacao(texto: str) -> bool:
    """
    Verifica se a pergunta do usuário contém tentativas de obter código ou scripts de programação.
    """
    texto_norm = normalizar_texto(texto)
    return any(termo in texto_norm for termo in TERMOS_PROGRAMACAO_OFFTOPIC)

def sanitizar_resposta_anti_codigo(texto: str, pedido_tinha_programacao: bool) -> str:
    """
    Remove blocos de código ou trechos de sintaxe técnica que a LLM possa ter gerado indevidamente
    e adiciona a nota cordial de recusa de escopo.
    """
    if not texto:
        return ""
    
    texto_limpo = re.sub(r'```[\s\S]*?```', '', texto)
    
    linhas_filtradas = []
    for linha in texto_limpo.split('\n'):
        l_strip = linha.strip()
        if (l_strip.startswith('def ') or l_strip.startswith('print(') or 
            '[::-1]' in l_strip or '.reverse()' in l_strip or l_strip.startswith('import ')):
            continue
        linhas_filtradas.append(linha)
    
    texto_final = '\n'.join(linhas_filtradas).strip()
    
    if pedido_tinha_programacao:
        aviso_escopo = (
            "\n\n💡 Nota de Escopo: Como ZelaBot, meu propósito exclusivo é auxiliar na zeladoria urbana, "
            "serviços públicos e melhoria da nossa cidade (CitizenTech). Não forneço códigos de programação ou scripts."
        )
        if "meu propósito exclusivo" not in texto_final and "zeladoria urbana" not in texto_final:
            texto_final += aviso_escopo
            
    return texto_final.strip()

def sanitizar_lgpd(texto: str) -> str:
    """
    Mascara números de CPF ou dados potencialmente sensíveis por conformidade com a LGPD.
    """
    if not texto:
        return ""
    # Mascara padrão de CPF: 000.000.000-00 ou 11 dígitos sequenciais
    texto_mascarado = re.sub(r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b', '[DADO PESSOAL ANONIMIZADO]', texto)
    # Mascara números de cartão de crédito (16 dígitos)
    texto_mascarado = re.sub(r'\b(?:\d{4}[ -]?){3}\d{4}\b', '[DADO PESSOAL ANONIMIZADO]', texto_mascarado)
    return texto_mascarado
