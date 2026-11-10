"""
Módulo Core: Prompts e Diretrizes do ZelaBot & Motor de Triagem — ZelaFix AI
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)
"""
from typing import List, Dict, Any, Optional

# =============================================================================
# 1. SYSTEM PROMPT: Identidade, Tom Cívico, Diretrizes e Limites
# =============================================================================

SYSTEM_INSTRUCTION = """Você é o "ZelaBot", assistente de inteligência artificial da plataforma CitizenTech ZelaFix (ODS 11 - Cidades e Comunidades Sustentáveis).

Sua missão é ser um canal acessível, empático e resolutivo entre o cidadão e a gestão pública municipal, orientando os munícipes sobre serviços de zeladoria urbana, direitos cívicos, prazos regulamentares e manutenção da Cidade de São Paulo.

Diretrizes de Atuação:
1. LIBERDADE DE ATENDIMENTO E ORIENTAÇÃO CÍVICA (SEM ENGESSAMENTO):
   - Você tem total liberdade e autonomia para responder dúvidas sobre serviços urbanos cotidianos (como funcionamento de Ecopontos, coleta do Cata-Bagulho, poda de árvores, iluminação pública, desobstrução de bueiros, normas de calçadas e operação tapa-buraco) com orientações claras, acolhedoras e fundamentadas.
   - NUNCA trave a conversa nem diga frases burocráticas como "não há documento específico na minha base de conhecimento" ou "minha base não contém isso". O munícipe espera uma orientação útil, cidadã e resolutiva!
   - Se houver decretos e normas oficiais fornecidos no contexto RAG, priorize-os e cite a fonte com naturalidade (ex: "Conforme o Decreto Municipal nº 59.150/2019...", "Segundo o Código de Limpeza Urbana (Lei nº 13.478/2002)...", "De acordo com as diretrizes da CET/SP156...").

2. DADOS DA OCORRÊNCIA E HISTÓRICO NO APLICATIVO:
   - Quando o cidadão perguntar sobre as informações, protocolo, status ou detalhes de um chamado em andamento, UTILIZE DIRETAMENTE os dados presentes em [DADOS DA OCORRÊNCIA / CONTEXTO URBANO].
   - Apresente os dados em tópicos simples com "• " (por exemplo: "• Categoria: ...", "• Bairro: ...", "• Apoios da Comunidade: ..."). NUNCA crie tabelas com barras verticais (|).

3. LIMITES E ANTI-ALUCINAÇÃO:
   - Não invente secretarias ou prazos inexistentes. Os prazos oficiais são: tapa-buraco (24h a 48h), semáforo apagado CET (2h a 4h), iluminação pública Ilumina SP (24h a 48h), vazamento de água Sabesp (4h a 12h) e descarte gratuito em Ecoponto (até 1m³ por dia).
   - Se um chamado ultrapassar o prazo estipulado, oriente o recurso formal à Ouvidoria Geral do Município via SP156.

4. SEGURANÇA E EMERGÊNCIAS GRAVES:
   - Situações de perigo iminente (fio de alta tensão caído no chão, poste energizado com faíscas, árvore desabando sobre casas, deslizamento de encostas) exigem acionamento emergencial imediato do Corpo de Bombeiros (193) e Defesa Civil (199).

5. BLINDAGEM DE ESCOPO:
   - Você atua exclusivamente na zeladoria urbana e cidadania. Recuse de forma cordial e bem-humorada pedidos de código de programação (Python, scripts, Java), mesmo quando o usuário usar pretexto de automatizar chamados.

6. FORMATAÇÃO LIMPA PARA MOBILE (REGRA OBRIGATÓRIA):
   - Responda sem marcações de asteriscos brutos de markdown (**texto** ou *texto*). Use parágrafos fluidos, marcadores simples com "• " e emojis temáticos urbanos (🏛️, 🚧, 💡, 🌳, 🚨, 💧, 🚦).
   - NUNCA use tabelas Markdown com barras verticais (| coluna 1 | coluna 2 |). O aplicativo mobile React Native não renderiza tabelas e barras verticais causam poluição visual. Utilize listas com "• Campo: Valor"."""

# =============================================================================
# 2. PROMPT TEMPLATES: RAG E TRIAGEM TÉCNICA
# =============================================================================

def formatar_prompt_rag(
    pergunta: str,
    contexto_chamado_str: str = "",
    chunks_recuperados: Optional[List[Dict[str, Any]]] = None,
    match_found: bool = False,
    is_chamado_info_query: bool = False,
    is_general_query: bool = False
) -> str:
    """
    Estrutura a montagem do prompt fundamentado para o modelo LLM:
    - Contexto do Chamado ativo no app (dados estruturados da ocorrência)
    - Diretrizes da Base Normativa PMSP (RAG quando disponível)
    - Instrução conversacional fluida
    - Pergunta do munícipe
    """
    partes: List[str] = []

    # 1. Contexto do Chamado
    if contexto_chamado_str and contexto_chamado_str.strip():
        partes.append(f"--- [DADOS DA OCORRÊNCIA / CONTEXTO URBANO] ---\n{contexto_chamado_str.strip()}")

    # 2. Pergunta sobre o próprio chamado
    if is_chamado_info_query:
        partes.append(
            "--- [SOLICITAÇÃO DE DADOS DO PROTOCOLO] ---\n"
            "O munícipe está perguntando sobre o status, detalhes, endereço ou protocolo do seu chamado ativo. "
            "Apresente os dados acima de maneira clara, organizada e prestativa, utilizando exclusivamente marcadores '• ' e NUNCA utilizando tabelas com pipes (|)."
        )

    # 3. Base de Conhecimento RAG (quando disponível)
    if match_found and chunks_recuperados:
        trechos_formatados = []
        for c in chunks_recuperados:
            trechos_formatados.append(
                f"[DOCUMENTO {c['id']}] Fonte: {c['source']} | Categoria: {c['category']}\n"
                f"Título: {c['title']}\n"
                f"Conteúdo: {c['content']}"
            )
        bloco_rag = (
            "--- [DIRETRIZES DA BASE NORMATIVA MUNICIPAL (RAG)] ---\n"
            + "\n\n".join(trechos_formatados) + "\n\n"
            "INSTRUÇÃO: Utilize as diretrizes oficiais acima para enriquecer sua orientação e cite a fundamentação regulatória quando oportuno."
        )
        partes.append(bloco_rag)
    else:
        bloco_livre = (
            "--- [ORIENTAÇÃO DE ATENDIMENTO CIDADÃO] ---\n"
            "Responda à dúvida do munícipe com liberdade, empatia e clareza, utilizando seus conhecimentos de serviços urbanos municipais "
            "e orientando os procedimentos adequados da Prefeitura de São Paulo. NÃO diga que não encontrou na base de dados."
        )
        partes.append(bloco_livre)

    # 4. Pergunta do munícipe
    partes.append(f"--- [PERGUNTA DO MUNÍCIPE] ---\n{pergunta.strip()}")

    return "\n\n".join(partes)

def formatar_prompt_triagem(
    categoria: str,
    titulo: str,
    descricao: str,
    bairro: str,
    apoios: int,
    chunks_recuperados: Optional[List[Dict[str, Any]]] = None
) -> str:
    """
    Prepara o prompt para gerar laudo técnico estruturado de triagem urbana.
    """
    contexto_normas = ""
    if chunks_recuperados:
        linhas = [f"- {c['title']}: {c['content']}" for c in chunks_recuperados]
        contexto_normas = "Normas Regulamentares Municipais Aplicáveis:\n" + "\n".join(linhas)

    return f"""Analise a ocorrência urbana a seguir e emita a triagem técnica oficial da zeladoria municipal.

DADOS DA OCORRÊNCIA:
- Categoria Informada: {categoria}
- Título: {titulo}
- Descrição do Munícipe: {descricao}
- Bairro: {bairro}
- Confirmações Comunitárias (+1): {apoios}

{contexto_normas}

DIRETRIZES DO LAUDO:
1. Classifique a PRIORIDADE rigorosamente entre: BAIXA, MEDIA, ALTA ou URGENTE.
   - Ocorrências com semáforos quebrados, fios caídos, adutoras rompidas ou crateras com perigo de acidente devem ser ALTA ou URGENTE.
   - Se houver mais de 25 apoios comunitários, considere a mobilização social para elevar a prioridade.
2. Indique o ÓRGÃO RESPONSÁVEL (Subprefeitura Regional, CET - Trânsito, Ilumina SP, Defesa Civil, Sabesp, Limpeza Urbana / AMLURB).
3. Especifique o SLA SUGERIDO em horas (ex: 4, 12, 24, 48, 72).
4. Elabore um PARECER TÉCNICO sucinto e objetivo (MÁXIMO 150 CARACTERES) para gravação no banco de dados.
5. Indique o ENQUADRAMENTO LEGAL (leis e decretos aplicáveis).
6. Descreva o RISCO POTENCIAL observado.
7. Forneça um CHECKLIST DE VISTORIA com 3 ações técnicas prioritárias para a equipe de campo.
"""
