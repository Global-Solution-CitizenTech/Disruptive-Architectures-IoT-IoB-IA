"""
Serviço de Triagem Urbana Inteligente, Enquadramento Normativo e Parecer Técnico — ZelaFix AI
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)
"""
import uuid
import logging
from typing import Dict, Any, List, Optional
from src.core.config import AI_PROVIDER, FALLBACK_PROVIDER
from src.core.prompts import formatar_prompt_triagem
from src.schemas.chamado import ChamadoContextPayload
from src.schemas.insights import TriagemRequest, TriagemResponse
from src.services.knowledge_service import KnowledgeService
from src.services.groq_service import GroqService
from src.database.oracle_client import OracleClient
from src.repositories.chat_repository import ChatRepository
from src.utils.guardrails import detectar_emergencia_vital
from src.utils.text import normalizar_texto

logger = logging.getLogger("ZelaFixAI.TriagemService")

class TriagemService:
    """
    Motor central de Triagem Urbana da ZelaFix:
    - Analisa categoria, relato, localização, engajamento comunitário (+1) e telemetria IoT.
    - Consulta a Base de Conhecimento RAG de Decretos Municipais de São Paulo.
    - Define Prioridade ('BAIXA', 'MEDIA', 'ALTA', 'URGENTE'), Órgão Responsável, SLA e Parecer Técnico.
    - Persiste o parecer na auditoria relacional SQLite.
    """

    @classmethod
    def realizar_triagem(cls, request: TriagemRequest) -> TriagemResponse:
        chamado = request.chamado
        session_id = request.sessionId or f"tria_{uuid.uuid4().hex[:12]}"

        try:
            dados_oracle = None
            if chamado.id:
                try:
                    dados_oracle = OracleClient.obter_chamado_completo(chamado.id)
                except Exception as err_ora:
                    logger.warning(f"Consulta ao Oracle para chamado {chamado.id} falhou: {err_ora}")

            categoria_raw = chamado.categoria or "Geral"
            titulo_raw = chamado.titulo or "Relato de Zeladoria"
            descricao_raw = chamado.descricao or ""
            bairro_raw = chamado.bairro or "São Paulo - SP"
            apoios = max(0, chamado.apoios_comunitarios or 0)

            # Enriquecimento com dados reais do Oracle se disponíveis
            if dados_oracle:
                if (categoria_raw == "Geral" or not categoria_raw) and dados_oracle.get("categoria"):
                    categoria_raw = dados_oracle["categoria"]
                if (titulo_raw == "Relato de Zeladoria" or not titulo_raw) and dados_oracle.get("titulo"):
                    titulo_raw = dados_oracle["titulo"]
                if not descricao_raw and dados_oracle.get("descricao"):
                    descricao_raw = dados_oracle["descricao"]
                if (bairro_raw == "São Paulo - SP" or not bairro_raw) and dados_oracle.get("bairro"):
                    bairro_raw = dados_oracle["bairro"]
                if apoios == 0 and dados_oracle.get("apoios_comunitarios"):
                    apoios = dados_oracle["apoios_comunitarios"]

            texto_completo = f"{categoria_raw} {titulo_raw} {descricao_raw}".strip()
            texto_norm = normalizar_texto(texto_completo)
            cat_norm = normalizar_texto(categoria_raw)

            # 1. Recuperação RAG da base normativa
            resultado_rag = KnowledgeService.buscar_chunks_rag(texto_completo, top_k=2)
            chunks = resultado_rag.get("chunks", [])

            # 2. Heurística Especializada de Domínio Municipal (PMSP)
            eh_emergencia = detectar_emergencia_vital(texto_completo)

            # Classificação por órgão municipal competente
            eh_saneamento = any(k in cat_norm for k in ["agua", "esgoto", "saneamento", "sabesp", "vazamento"]) or any(k in texto_norm for k in ["vazamento de agua", "adutora", "cano quebrado", "cano rompido", "cano estourado", "esgoto a ceu aberto", "sabesp", "cavalete", "agua jorrando"])
            eh_transito = any(k in cat_norm for k in ["sinal", "transito", "cet"]) or any(k in texto_norm for k in ["semaforo", "farol", "faixa de pedestre", "faixa zebrada", "placa pare", "placa de transito", "cruzamento semaforo", "cet"])
            eh_iluminacao = any(k in cat_norm for k in ["iluminacao", "poste", "luz"]) or any(k in texto_norm for k in ["poste apagado", "lampada queimada", "ponto escuro", "luminaria led", "escuridao", "ilumina sp"])
            eh_drenagem = any(k in cat_norm for k in ["bueiro", "drenagem", "enchente", "alagamento"]) or any(k in texto_norm for k in ["bueiro", "boca de lobo", "alagamento", "enchente", "tampa de bueiro", "grelha"])
            eh_arvore = any(k in cat_norm for k in ["arvore", "poda", "arboreo"]) or any(k in texto_norm for k in ["poda de arvore", "podar galho", "arvore caindo", "tombamento de arvore", "arvore na fiacao", "galho no fio"])
            eh_limpeza = any(k in cat_norm for k in ["lixo", "entulho", "limpeza", "ecoponto"]) or any(k in texto_norm for k in ["entulho", "ecoponto", "cata bagulho", "descarte clandestino", "lixo na calcada", "terreno baldio"])
            eh_pavimentacao = any(k in cat_norm for k in ["buraco", "paviment", "asfalto"]) or any(k in texto_norm for k in ["buraco", "cratera", "tapa buraco", "recapeamento", "asfalto"])

            if eh_saneamento:
                orgao = "Companhia de Saneamento Básico (Sabesp)"
                enquadramento = "Regulamento Geral ARSESP e Contrato de Programa Sabesp"
                sla_padrao = 12 if "esgoto" not in texto_norm else 24
                checklist = [
                    "Localizar ponto de fuga hídrica com geofone acústico",
                    "Abrir vala de inspeção e estancar vazamento de adutora/ramal",
                    "Recompor base de bica corrida e pavimento no padrão original"
                ]
                risco = "Desperdício hídrico e solapamento do subleito asfáltico gerando risco de cratera."
                parecer = "Triagem Sabesp: Vazamento em rede distribuidora com risco de erosão do asfalto."

            elif eh_transito:
                orgao = "Companhia de Engenharia de Tráfego (CET)"
                enquadramento = "Código de Trânsito Brasileiro e Procedimentos CET-SP"
                sla_padrao = 4
                checklist = [
                    "Verificar alimentação do controlador semafórico e queima de foco",
                    "Operar tráfego manual no cruzamento durante o horário de pico",
                    "Substituir conjunto de lentes LED e testar temporização"
                ]
                risco = "Perigo iminente de colisão transversal e atropelamento de pedestres no cruzamento."
                parecer = "Triagem CET: Falha semafórica identificada em via pública. Despacho urgente para equipe técnica."

            elif eh_pavimentacao:
                orgao = "Subprefeitura Regional — Conservação de Pavimento"
                enquadramento = "Decreto Municipal nº 59.150/2019 (Regulamento de Pavimentação PMSP)"
                sla_padrao = 24 if any(k in texto_norm for k in ["cratera", "fundo", "onibus", "avenida", "moto"]) else 48
                checklist = [
                    "Efetuar corte geométrico com serra clipper e varrição do fundo",
                    "Aplicar emulsão asfáltica de ligação e CBUQ a quente",
                    "Compactar com rolo tandem vibratório para nivelamento perfeito"
                ]
                risco = "Danos à suspensão de veículos e risco de queda de motociclistas e ciclistas."
                parecer = "Triagem Pavimentação: Deformação asfáltica em via pública. Reparo por tapa-buraco."

            elif eh_iluminacao:
                orgao = "Departamento de Iluminação Pública (Ilumina SP)"
                enquadramento = "Portaria SGM/SES nº 03/2021 e Contrato PPP Ilumina SP"
                sla_padrao = 24 if any(k in texto_norm for k in ["escola", "onibus", "hospital", "apagao"]) else 48
                checklist = [
                    "Medir tensão na base do poste e verificar circuito secundário",
                    "Substituir relé fotoelétrico e luminária por modelo LED telegestionado",
                    "Testar isolamento elétrico e continuidade do aterramento"
                ]
                risco = "Insegurança pública noturna, vulnerabilidade a delitos e acidentes em vias escuras."
                parecer = "Triagem Ilumina SP: Ponto escuro em logradouro. Encaminhado para troca de luminária LED."

            elif eh_drenagem:
                orgao = "Subprefeitura Regional — Drenagem Urbana / SIURB"
                enquadramento = "Decreto Municipal nº 57.545/2016 (Drenagem Urbana PMSP)"
                sla_padrao = 24 if any(k in texto_norm for k in ["enchente", "alagamento", "tampa", "grelha"]) else 48
                checklist = [
                    "Desobstruir grelha e retirar detritos retidos na caixa de coleta",
                    "Aplicar hidrojateamento de alta pressão para desentupir ramal",
                    "Verificar integridade estrutural das paredes de alvenaria e tampa"
                ]
                risco = "Risco de alagamento viário, acúmulo de águas pluviais e danos a pedestres e veículos."
                parecer = "Triagem Drenagem: Obstrução de captação pluvial com risco de alagamento viário."

            elif eh_arvore:
                if any(k in texto_norm for k in ["fio", "fiacao", "alta tensao", "choque", "faisca"]):
                    orgao = "Concessionária ENEL Distribuição São Paulo"
                    enquadramento = "Lei Municipal nº 17.267/2020 e Procedimentos de Segurança ANEEL"
                    sla_padrao = 12
                    checklist = [
                        "Isolar área sob condutores elétricos primários",
                        "Efetuar manobra de desligamento da rede para poda com segurança",
                        "Remover galhos em contato com fiação de alta tensão"
                    ]
                    risco = "Perigo letal de eletrocussão e interrupção do fornecimento de energia no circuito."
                    parecer = "Triagem ENEL: Conflito de arborização com rede primária energizada."
                else:
                    orgao = "Subprefeitura Regional — Manejo Arbóreo"
                    enquadramento = "Lei Municipal nº 17.267/2020 (Manejo Arbóreo PMSP)"
                    sla_padrao = 72
                    checklist = [
                        "Realizar vistoria agronômica e emitir laudo fitossanitário",
                        "Efetuar poda de equilíbrio de copa ou remoção autorizada",
                        "Destinar resíduos lenhosos para trituração e compostagem"
                    ]
                    risco = "Possibilidade de queda de galhos sobre calçadas ou veículos."
                    parecer = "Triagem Manejo Arbóreo: Solicitação de poda preventiva em logradouro público."

            elif eh_limpeza:
                orgao = "Subprefeitura Regional — Limpeza Urbana / AMLURB"
                enquadramento = "Lei Municipal nº 13.478/2002 (Código de Limpeza Urbana PMSP)"
                sla_padrao = 48
                checklist = [
                    "Inspecionar volume e tipo de resíduo descartado irregularmente",
                    "Executar recolhimento com caminhão basculante e pá carregadeira",
                    "Notificar fiscalização de posturas para identificação do infrator"
                ]
                risco = "Proliferação de vetores de doenças (dengue, roedores) e obstrução de calçadas."
                parecer = "Triagem Limpeza Urbana: Descarte irregular de resíduos na via pública."

            else:
                orgao = "Subprefeitura Regional — Zeladoria Urbana"
                enquadramento = "Carta de Serviços ao Cidadão da Cidade de São Paulo"
                sla_padrao = 48
                checklist = [
                    "Realizar vistoria presencial da equipe técnica de campo",
                    "Verificar conformidade com posturas municipais",
                    "Programar ordem de serviço para manutenção"
                ]
                risco = "Impacto no bem-estar e circulação da comunidade local."
                parecer = "Triagem ZelaFix: Ocorrência cadastrada e encaminhada para vistoria técnica da Subprefeitura."

            # 3. Cálculo de Prioridade com IoB (Apoios Comunitários) e Risco Vital
            if eh_emergencia or ("CET" in orgao and sla_padrao <= 4):
                prioridade = "URGENTE"
                sla_padrao = min(sla_padrao, 4)
            elif apoios >= 25 or any(k in texto_norm for k in ["cratera", "enchente", "apagao", "esgoto"]):
                prioridade = "ALTA"
                sla_padrao = min(sla_padrao, 24)
            elif apoios >= 10 or sla_padrao <= 48:
                prioridade = "MEDIA"
            else:
                prioridade = "BAIXA"

            # Se houver chunks RAG com enquadramento específico, atualiza
            if chunks:
                primeiro_chunk = chunks[0]
                if "Decreto" in primeiro_chunk.get("source", "") or "Lei" in primeiro_chunk.get("source", ""):
                    enquadramento = f"{primeiro_chunk['source']} — {primeiro_chunk['title']}"

            # Análise visual multimodal via Qwen 3.8 27B caso haja foto fornecida ou persistida
            foto_input = chamado.foto_base64
            if not foto_input and dados_oracle and dados_oracle.get("foto_bytes"):
                foto_input = dados_oracle["foto_bytes"]

            analise_visual = None
            if foto_input:
                try:
                    prompt_visao = (
                        f"Você é o ZelaFix AI, especialista em engenharia e zeladoria urbana da PMSP. "
                        f"Analise esta fotografia do defeito urbano '{titulo_raw}' ({categoria_raw}) no bairro {bairro_raw}. "
                        f"Descreva em até duas frases objetivas o dano físico identificado, "
                        f"sua aparente severidade e o risco estrutural imediato."
                    )
                    analise_visual = GroqService.gerar_resposta(prompt_atual=prompt_visao, imagem_base64=foto_input)
                except Exception as err_v:
                    logger.warning(f"Erro na análise visual da triagem: {err_v}")

            # Assegura limite estrito de 150 caracteres no parecer para persistência
            parecer_ia = (parecer[:147] + "...") if len(parecer) > 150 else parecer

            # Persiste auditoria da triagem no SQLite
            ChatRepository.salvar_triagem_audit(
                session_id=session_id,
                chamado_id=chamado.id,
                bairro=bairro_raw,
                titulo=titulo_raw,
                parecer_ia=parecer_ia,
                categoria=categoria_raw,
                prioridade=prioridade,
                orgao_responsavel=orgao,
                sla_horas=sla_padrao,
                origem_triagem="ZelaFix AI Triagem Multimodal + RAG"
            )

            return TriagemResponse(
                prioridade=prioridade,
                orgao_responsavel=orgao,
                parecer_ia=parecer_ia,
                sla_sugerido_horas=sla_padrao,
                enquadramento_legal=enquadramento,
                risco_potencial=risco,
                checklist_vistoria=checklist,
                analise_visual=analise_visual,
                origem_triagem="ZelaFix AI Triagem Multimodal + RAG"
            )
        except Exception as e:
            logger.error(f"Erro inesperado no TriagemService: {e}")
            return TriagemResponse(
                prioridade="MEDIA",
                orgao_responsavel="Subprefeitura Regional — Zeladoria Urbana",
                parecer_ia="Triagem ZelaFix: Ocorrência cadastrada para vistoria técnica da Subprefeitura.",
                sla_sugerido_horas=48,
                enquadramento_legal="Carta de Serviços ao Cidadão da Cidade de São Paulo",
                risco_potencial="Necessidade de avaliação presencial pela equipe técnica.",
                checklist_vistoria=["Realizar vistoria presencial no logradouro", "Verificar conformidade com normas municipais"],
                origem_triagem="ZelaFix AI Fallback de Contingência"
            )
