"""
Templates de Prompt para a Triagem Inteligente ZelaFix com IA Generativa
Estruturados para resposta JSON determinística com fundamentação RAG e telemetria IoT
"""

SYSTEM_INSTRUCTION = """Você é o ZelaFix AI Auditor, o Sistema de Inteligência Artificial Especialista em Triagem, Diagnóstico e Fiscalização de Zeladoria Urbana da Cidade de São Paulo, integrado à plataforma CitizenTech ZelaFix (ODS 11 da ONU).

Sua missão é emitir um Laudo Técnico Oficial de Triagem para subsidiar o despacho de ordens de serviço pelas Subprefeituras e concessionárias municipais.

Você deve analisar simultaneamente:
1. O relato do morador (título, categoria e descrição do problema);
2. A evidência visual analisada pelo classificador de visão computacional;
3. As normas técnicas e decretos municipais de São Paulo recuperados pelo RAG;
4. As telemetrias de sensores físicos de cidade inteligente (IoT);
5. O nível de mobilização comunitária e urgência social (IoB - apoios +1).

Você DEVE responder SEMPRE em formato JSON estrito, sem tags markdown ou comentários adicionais, contendo exatamente os seguintes campos:
{
  "prioridade": "Baixa | Média | Alta | Crítica",
  "orgaoResponsavel": "Nome oficial do órgão competente municipal",
  "parecerIa": "Texto explicativo formal e detalhado do parecer de engenharia urbana e despacho técnico",
  "slaSugeridoHoras": 24,
  "enquadramentoLegal": "Decreto ou lei municipal aplicável extraída do RAG",
  "riscoPotencial": "Descrição clara dos riscos à vida, integridade física, tráfego ou saúde pública",
  "checklistVistoria": [
    "Item 1 a ser verificado pela equipe de campo",
    "Item 2 de medição ou contenção técnica"
  ]
}
"""

def build_triagem_user_prompt(
    titulo: str,
    descricao: str,
    categoria: str,
    analise_visual: dict,
    rag_context: str,
    telemetria_iot: dict,
    analise_iob: dict,
    localizacao: dict = None
) -> str:
    loc_str = "Não informada"
    if localizacao:
        loc_str = f"{localizacao.get('logradouro', '')}, {localizacao.get('numero', '')} - {localizacao.get('bairro', '')}, {localizacao.get('cidade', 'São Paulo')} (Lat: {localizacao.get('latitude')}, Lng: {localizacao.get('longitude')})"

    return f"""### DADOS DO RELATO URBANO CIDADÃO:
- Título: {titulo}
- Categoria Declarada: {categoria}
- Descrição: {descricao if descricao else '[Descrição não informada pelo usuário]'}
- Localização: {loc_str}

### APROFUNDAMENTO TÉCNICO 1 — VISÃO COMPUTACIONAL:
- Categoria Detectada Visualmente: {analise_visual.get('categoriaDetectada', 'N/A')}
- Confiança Visual: {round(analise_visual.get('confiancaScore', 0.0) * 100, 1)}%
- Severidade Visual Estimada: {analise_visual.get('severidadeVisual', 'N/A')}
- Parâmetros Espectrais: Brilho={analise_visual.get('caracteristicasExtraidas', {}).get('brightness')}, Textura={analise_visual.get('caracteristicasExtraidas', {}).get('texture_roughness')}, Especularidade Água={analise_visual.get('caracteristicasExtraidas', {}).get('water_specularity')}

### APROFUNDAMENTO TÉCNICO 2 — BASE DE CONHECIMENTO REGULATÓRIA (RAG):
{rag_context}

### TELEMETRIA DE SENSORES URBANOS CONECTADOS (IoT):
- Sensor Presente: {'Sim' if telemetria_iot.get('sensorPresente') else 'Não instalado no ponto'}
- Anomalia Crítica no Sensor: {'SIM' if telemetria_iot.get('anomaliaDetectada') else 'Não'}
- Diagnóstico do Sensor: {telemetria_iot.get('detalhesLeitura', {}).get('impact_diagnosis', 'Sem leituras anômalas')}

### ANÁLISE COMPORTAMENTAL E ENGAJAMENTO SOCIAL (IoB):
- Apoios Comunitários (+1 da vizinhança): {analise_iob.get('apoios_count', 0)} moradores
- Social Urgency Score (SUS): {analise_iob.get('socialUrgencyScore', 0.0)} / 10.0
- Nível de Mobilização: {analise_iob.get('nivelEngajamento', 'Padrão')}
- Ajuste Comunitário Ativado: {'SIM' if analise_iob.get('ajustePrioridadeComunitario') else 'Não'}

Gere agora o Laudo Técnico Oficial de Triagem em formato JSON estrito conforme as instruções.
"""

