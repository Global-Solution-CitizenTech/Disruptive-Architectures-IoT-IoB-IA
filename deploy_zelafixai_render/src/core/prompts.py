"""
Módulo Core: Prompts e Diretrizes do ZelaBot & Motor de Triagem — ZelaFix AI
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)
"""
from typing import List, Dict, Any, Optional

# =============================================================================
# 1. SYSTEM PROMPT: Identidade, Tom Cívico, Diretrizes e Limites
# =============================================================================

SYSTEM_INSTRUCTION = """Você é o "ZelaBot", assistente da plataforma CitizenTech ZelaFix (ODS 11 — Cidades Sustentáveis) para serviços de zeladoria urbana e cidadania em São Paulo.

Diretrizes:
1. ATENDIMENTO RESOLUTIVO E CIDADÃO:
   - Responda dúvidas urbanas (Ecopontos, Cata-Bagulho, tapa-buraco, iluminação pública, bueiros, árvores, calçadas, trânsito/SP156) de forma clara, empática e prática. Nunca diga frases burocráticas como "não encontrei na base".
   - Quando houver normas em [DIRETRIZES DA BASE NORMATIVA MUNICIPAL (RAG)], priorize-as e cite a fonte com naturalidade.
   - Se a pergunta fugir totalmente de zeladoria urbana ou cidadania (ex.: receita de bolo), oriente com simpatia que seu foco é atendimento urbano de São Paulo, sem inventar normas.

2. USO DE DADOS DE CHAMADOS E PRAZOS OFICIAIS:
   - Ao responder sobre um protocolo ou lista de ocorrências, use diretamente [DADOS DA OCORRÊNCIA / CONTEXTO URBANO] em tópicos "• Campo: Valor".
   - Prazos de referência (não invente secretarias): tapa-buraco (24h–48h), semáforo CET (2h–4h), iluminação Ilumina SP (24h–48h), vazamento Sabesp (4h–12h), Ecoponto (até 1m³/dia grátis), recurso em atraso (Ouvidoria SP156).
   - Em risco grave iminente (fio energizado caído, risco de desabamento), oriente acionar Bombeiros (193) ou Defesa Civil (199).

3. FORMATAÇÃO MOBILE (OBRIGATÓRIA):
   - NUNCA use **negrito**, *itálico* ou tabelas Markdown com pipes (|). Use parágrafos curtos, marcadores "• " e emojis urbanos (🏛️, 🚧, 💡, 🌳, 🚨, 💧, 🚦)."""

# =============================================================================
# 2. PROMPT TEMPLATES: RAG E TRIAGEM TÉCNICA
# =============================================================================

def formatar_prompt_rag(
    pergunta: str,
    contexto_chamado_str: str = "",
    chunks_recuperados: Optional[List[Dict[str, Any]]] = None,
    match_found: bool = False,
    is_chamado_info_query: bool = False
) -> str:
    """
    Estrutura o prompt com contexto do chamado (Oracle/app), normas PMSP (RAG) e pergunta.
    """
    partes: List[str] = []

    if contexto_chamado_str and contexto_chamado_str.strip():
        partes.append(f"--- [DADOS DA OCORRÊNCIA / CONTEXTO URBANO] ---\n{contexto_chamado_str.strip()}")

    if is_chamado_info_query:
        partes.append(
            "--- [SOLICITAÇÃO DE PROTOCOLO] ---\n"
            "Apresente os dados acima de forma direta e organizada com marcadores '• ', sem tabelas com pipes (|)."
        )

    if match_found and chunks_recuperados:
        trechos_formatados = [
            f"[{c['id']}] Fonte: {c['source']} | Categoria: {c['category']}\n"
            f"Título: {c['title']}\n"
            f"Conteúdo: {c['content']}"
            for c in chunks_recuperados
        ]
        partes.append(
            "--- [DIRETRIZES DA BASE NORMATIVA MUNICIPAL (RAG)] ---\n"
            + "\n\n".join(trechos_formatados)
        )

    partes.append(f"--- [PERGUNTA DO MUNÍCIPE] ---\n{pergunta.strip()}")
    return "\n\n".join(partes)

def formatar_prompt_triagem(
    categoria: str,
    titulo: str,
    descricao: str,
    bairro: str,
    apoios: int,
    chunks_recuperados: Optional[List[Dict[str, Any]]] = None,
    telemetria_str: str = "",
    possui_imagem: bool = False
) -> str:
    """
    Prepara o prompt JSON para o modelo multimodal emitir laudo técnico de triagem urbana.
    """
    contexto_normas = ""
    if chunks_recuperados:
        linhas = [f"- {c['title']} ({c.get('source', 'PMSP')}): {c['content']}" for c in chunks_recuperados]
        contexto_normas = "\nNORMAS PMSP (RAG):\n" + "\n".join(linhas)

    bloco_iot = f"\nTELEMETRIA IOT:\n{telemetria_str}" if telemetria_str else ""
    instrucao_visao = (
        "\n- analise_visual: descreva objetivamente o problema visto na foto (ou null se imagem ilegível)."
        if possui_imagem
        else "\n- analise_visual: null"
    )

    return f"""Analise a ocorrência urbana abaixo e retorne EXCLUSIVAMENTE um objeto JSON válido com o laudo técnico de triagem.

DADOS DA OCORRÊNCIA:
- Categoria Informada: {categoria}
- Título: {titulo}
- Descrição: {descricao}
- Bairro: {bairro}
- Apoios Comunitários (+1): {apoios}{bloco_iot}{contexto_normas}

CAMPOS OBRIGATÓRIOS DO JSON:
- prioridade: rigorosamente "BAIXA", "MEDIA", "ALTA" ou "URGENTE".
- orgao_responsavel: órgão municipal adequado (ex: "CET - Companhia de Engenharia de Tráfego", "Ilumina SP / Prefeitura", "SIURB / Subprefeitura Regional (Drenagem)", "Sabesp (Saneamento)", "AMLURB / Limpeza Urbana", "Subprefeitura Regional / SVMA", "Defesa Civil Municipal", "Subprefeitura Regional (Vias)").
- sla_sugerido_horas: inteiro (ex: 2, 4, 12, 24, 48, 72).
- parecer_ia: parecer técnico objetivo com NO MÁXIMO 150 caracteres (sem aspas quebradas).
- enquadramento_legal: lei/decreto ou norma municipal aplicável.
- risco_potencial: risco urbano identificado em 1 frase curta.
- checklist_vistoria: array JSON com exatamente 3 ações técnicas curtas para equipe em campo.{instrucao_visao}"""
