"""
Serviço de Triagem Urbana Inteligente, Enquadramento Normativo e Parecer Técnico — ZelaFix AI
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)
"""
import uuid
import logging
from typing import Dict, Any, List, Optional
from src.core.config import GROQ_MODEL
from src.core.prompts import formatar_prompt_triagem
from src.schemas.insights import TriagemRequest, TriagemResponse
from src.services.knowledge_service import KnowledgeService
from src.services.groq_service import GroqService
from src.services.viacep_client import ViaCepClient
from src.database.oracle_client import OracleClient
from src.repositories.chat_repository import ChatRepository
from src.utils.guardrails import sanitizar_lgpd
from src.utils.text import normalizar_texto, limpar_texto_mobile

logger = logging.getLogger("ZelaFixAI.TriagemService")

_PRIORIDADES_VALIDAS = {"BAIXA", "MEDIA", "ALTA", "URGENTE"}


class TriagemService:
    """
    Motor central de Triagem Urbana da ZelaFix:
    - Analisa categoria, relato, localização, engajamento comunitário (+1) e telemetria IoT.
    - Consulta a Base de Conhecimento RAG de Decretos Municipais de São Paulo.
    - Emite laudo estruturado com Qwen 3.8 27B (texto + visão) com fallback heurístico PMSP instantâneo.
    - Persiste a auditoria no SQLite local (sem alterar dados do Oracle FIAP).
    """

    @classmethod
    def _classificar_heuristica_local(
        cls,
        cat_norm: str,
        texto_norm: str,
        apoios: int,
        anomalia_iot: bool,
        chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calcula triagem determinística PMSP usada como baseline e fallback."""
        eh_critico = any(k in texto_norm for k in [
            "alta tensao", "choque", "faisca", "fogo", "cratera", "alagamento", "desabamento", "soterramento"
        ])

        eh_vazamento_agua = any(k in cat_norm for k in ["agua", "saneamento", "sabesp", "vazamento"]) or (
            any(
                k in texto_norm for k in [
                    "vazamento de agua", "adutora", "cano quebrado", "cano rompido",
                    "cano estourado", "esgoto a ceu aberto", "sabesp", "cavalete", "agua jorrando"
                ]
            )
            and "agua da chuva" not in texto_norm
        )
        eh_drenagem = (
            "drenagem" in cat_norm
            or any(k in cat_norm for k in ["bueiro", "enchente", "alagamento"])
            or any(k in texto_norm for k in [
                "bueiro", "boca de lobo", "alagamento", "enchente",
                "tampa de bueiro", "grelha", "galeria pluvial", "agua da chuva"
            ])
        )
        eh_transito = any(k in cat_norm for k in ["sinal", "transito", "cet"]) or any(
            k in texto_norm for k in [
                "semaforo", "farol", "faixa de pedestre", "faixa zebrada",
                "placa pare", "placa de transito", "cruzamento semaforo", "cet"
            ]
        )
        eh_iluminacao = any(k in cat_norm for k in ["iluminacao", "poste", "luz"]) or any(
            k in texto_norm for k in [
                "poste apagado", "lampada queimada", "ponto escuro",
                "luminaria led", "escuridao", "ilumina sp", "sem luz", "luz piscando",
                "rua escura", "praca escura"
            ]
        )
        eh_arvore = any(k in cat_norm for k in ["arvore", "poda", "arboreo", "parque"]) or any(
            k in texto_norm for k in [
                "poda de arvore", "podar galho", "arvore caindo",
                "tombamento de arvore", "arvore na fiacao", "galho no fio"
            ]
        )
        eh_limpeza = any(k in cat_norm for k in ["lixo", "entulho", "limpeza", "ecoponto"]) or any(
            k in texto_norm for k in [
                "entulho", "ecoponto", "cata bagulho",
                "descarte clandestino", "lixo na calcada", "terreno baldio"
            ]
        )
        eh_calcada = any(k in cat_norm for k in ["calcada", "acessibilidade"]) or any(
            k in texto_norm for k in [
                "calcada quebrada", "buraco na calcada", "calcada com buraco",
                "calcada afundando", "calcada irregular", "piso tatil",
                "rampa acessibilidade", "degrau calcada"
            ]
        )
        eh_pavimentacao = (not eh_calcada) and (
            any(k in cat_norm for k in ["buraco", "paviment", "asfalto", "via"]) or any(
                k in texto_norm for k in ["buraco", "cratera", "tapa buraco", "recapeamento", "asfalto"]
            )
        )

        # Drenagem tem prioridade sobre menção genérica a "esgoto" na categoria Oracle "Drenagem e Esgoto"
        if eh_drenagem and not eh_vazamento_agua:
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
        elif eh_vazamento_agua or ("esgoto" in cat_norm and not eh_drenagem):
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
                orgao = "Subprefeitura Regional — Manejo Arbóreo / SVMA"
                enquadramento = "Lei Municipal nº 17.267/2020 (Manejo Arbóreo PMSP)"
                sla_padrao = 72
                checklist = [
                    "Realizar vistoria agronômica e emitir laudo fitossanitário",
                    "Efetuar poda de equilíbrio de copa ou remoção autorizada",
                    "Destinar resíduos lenhosos para trituração e compostagem"
                ]
                risco = "Possibilidade de queda de galhos sobre calçadas ou veículos."
                parecer = "Triagem Manejo Arbóreo: Solicitação de poda preventiva ou manutenção de área verde."
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
        elif eh_calcada:
            orgao = "Subprefeitura Regional — Passeio e Acessibilidade"
            enquadramento = "Lei Municipal nº 15.442/2011 (Passeios Públicos e NBR 9050)"
            sla_padrao = 72
            checklist = [
                "Avaliar desnível, piso tátil e largura da faixa livre de circulação",
                "Identificar responsabilidade do lote confrontante ou área pública",
                "Notificar proprietário ou emitir ordem de reparo em passeio público"
            ]
            risco = "Risco de queda de pedestres, idosos e pessoas com deficiência."
            parecer = "Triagem Acessibilidade: Irregularidade em calçada exigindo vistoria pela Subprefeitura."
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

        if eh_critico or ("CET" in orgao and sla_padrao <= 4):
            prioridade = "URGENTE"
            sla_padrao = min(sla_padrao, 4)
        elif apoios >= 25 or anomalia_iot or any(k in texto_norm for k in ["cratera", "enchente", "apagao", "esgoto"]):
            prioridade = "ALTA"
            sla_padrao = min(sla_padrao, 24)
            if anomalia_iot and ("alagamento" in texto_norm or "drenagem" in cat_norm):
                prioridade = "URGENTE"
                sla_padrao = min(sla_padrao, 12)
        elif apoios >= 10 or sla_padrao <= 48:
            prioridade = "MEDIA"
        else:
            prioridade = "BAIXA"

        if chunks:
            primeiro_chunk = chunks[0]
            if "Decreto" in primeiro_chunk.get("source", "") or "Lei" in primeiro_chunk.get("source", ""):
                enquadramento = f"{primeiro_chunk['source']} — {primeiro_chunk['title']}"

        return {
            "prioridade": prioridade,
            "orgao_responsavel": orgao,
            "sla_sugerido_horas": sla_padrao,
            "enquadramento_legal": enquadramento,
            "risco_potencial": risco,
            "checklist_vistoria": checklist,
            "parecer": parecer,
        }

    @classmethod
    def realizar_triagem(cls, request: TriagemRequest) -> TriagemResponse:
        chamado = request.chamado
        session_id = request.sessionId or f"tria_{uuid.uuid4().hex[:12]}"

        try:
            dados_oracle = None
            if chamado.id:
                try:
                    dados_oracle = OracleClient.obter_chamado_completo(
                        chamado.id,
                        incluir_foto=not bool(chamado.foto_base64)
                    )
                except Exception as err_ora:
                    logger.warning(f"Consulta ao Oracle para chamado {chamado.id} falhou: {err_ora}")

            categoria_raw = sanitizar_lgpd(chamado.categoria or "Geral")
            titulo_raw = sanitizar_lgpd(chamado.titulo or "Relato de Zeladoria")
            descricao_raw = sanitizar_lgpd(chamado.descricao or "")
            bairro_raw = sanitizar_lgpd(chamado.bairro or "São Paulo - SP")
            apoios = max(0, chamado.apoios_comunitarios or 0)

            if dados_oracle:
                if (categoria_raw == "Geral" or not categoria_raw) and dados_oracle.get("categoria"):
                    categoria_raw = dados_oracle["categoria"]
                if (titulo_raw == "Relato de Zeladoria" or not titulo_raw) and dados_oracle.get("titulo"):
                    titulo_raw = dados_oracle["titulo"]
                if not descricao_raw and dados_oracle.get("descricao"):
                    descricao_raw = sanitizar_lgpd(dados_oracle["descricao"])
                if (bairro_raw == "São Paulo - SP" or not bairro_raw) and dados_oracle.get("bairro"):
                    bairro_raw = dados_oracle["bairro"]
                if apoios == 0 and dados_oracle.get("apoios_comunitarios"):
                    apoios = dados_oracle["apoios_comunitarios"]

            # Enriquecimento por ViaCEP quando CEP vier preenchido sem bairro real (padrão Java)
            cep_resolvido = chamado.cep or (dados_oracle.get("cep") if dados_oracle else None)
            if (bairro_raw == "São Paulo - SP" or not bairro_raw) and cep_resolvido:
                dados_cep = ViaCepClient.consultar_cep(cep_resolvido)
                if dados_cep and dados_cep.get("bairro"):
                    bairro_raw = sanitizar_lgpd(dados_cep["bairro"])

            # Telemetria IoT real (quando presente)
            telemetria = chamado.telemetria_iot
            anomalia_iot = bool(telemetria and telemetria.anomalia_detectada)
            telemetria_str = ""
            if telemetria:
                telemetria_str = (
                    f"Sensor {telemetria.device_id or 'IoT'} ({telemetria.tipo_sensor or 'urbano'}): "
                    f"{telemetria.valor_medido if telemetria.valor_medido is not None else 'N/D'} "
                    f"{telemetria.unidade or ''} | Anomalia na borda: {'SIM' if anomalia_iot else 'NÃO'}"
                ).strip()

            texto_completo = f"{categoria_raw} {titulo_raw} {descricao_raw}".strip()
            texto_norm = normalizar_texto(texto_completo)
            cat_norm = normalizar_texto(categoria_raw)

            # 1. Recuperação RAG da base normativa
            resultado_rag = KnowledgeService.buscar_chunks_rag(texto_completo, top_k=2)
            chunks = resultado_rag.get("chunks", [])

            # 2. Baseline heurístico determinístico PMSP + IoT
            base = cls._classificar_heuristica_local(cat_norm, texto_norm, apoios, anomalia_iot, chunks)
            prioridade = base["prioridade"]
            orgao = base["orgao_responsavel"]
            sla_padrao = base["sla_sugerido_horas"]
            enquadramento = base["enquadramento_legal"]
            risco = base["risco_potencial"]
            checklist = base["checklist_vistoria"]
            parecer = base["parecer"]
            if anomalia_iot and "IoT" not in risco:
                risco = f"Anomalia IoT confirmada em campo ({telemetria.tipo_sensor or 'sensor'}): {risco}"

            # 3. Enriquecimento Generativo Multimodal em chamada única (Qwen 3.8 27B JSON)
            foto_input = chamado.foto_base64 or (dados_oracle.get("foto_bytes") if dados_oracle else None)
            prompt_triagem = formatar_prompt_triagem(
                categoria=categoria_raw,
                titulo=titulo_raw,
                descricao=descricao_raw,
                bairro=bairro_raw,
                apoios=apoios,
                chunks_recuperados=chunks,
                telemetria_str=telemetria_str,
                possui_imagem=bool(foto_input),
            )

            analise_visual: Optional[str] = None
            origem_triagem = "ZelaFix AI Triagem Heurística Local + RAG"

            laudo_llm = GroqService.gerar_resposta_json(
                prompt_atual=prompt_triagem,
                imagem_base64=foto_input,
            )
            if laudo_llm:
                prio_llm = str(laudo_llm.get("prioridade", "")).upper().strip()
                if prio_llm in _PRIORIDADES_VALIDAS:
                    ordem_prio = {"BAIXA": 1, "MEDIA": 2, "ALTA": 3, "URGENTE": 4}
                    # Nunca reduz abaixo do piso normativo crítico/IoT/mobilização +1
                    if base["prioridade"] == "URGENTE":
                        prio_llm = "URGENTE"
                    elif (anomalia_iot or apoios >= 25) and ordem_prio[prio_llm] < 3:
                        prio_llm = "ALTA"
                    prioridade = prio_llm

                orgao_llm = str(laudo_llm.get("orgao_responsavel") or "").strip()
                if orgao_llm:
                    orgao = sanitizar_lgpd(orgao_llm)

                sla_llm = laudo_llm.get("sla_sugerido_horas")
                if isinstance(sla_llm, (int, float)) and 1 <= int(sla_llm) <= 168:
                    sla_padrao = min(int(sla_llm), sla_padrao) if (base["prioridade"] == "URGENTE" or anomalia_iot) else int(sla_llm)

                parecer_llm = str(laudo_llm.get("parecer_ia") or "").strip()
                if parecer_llm:
                    parecer = sanitizar_lgpd(limpar_texto_mobile(parecer_llm))

                enquad_llm = str(laudo_llm.get("enquadramento_legal") or "").strip()
                if enquad_llm:
                    enquadramento = sanitizar_lgpd(enquad_llm)

                risco_llm = str(laudo_llm.get("risco_potencial") or "").strip()
                if risco_llm:
                    risco = sanitizar_lgpd(limpar_texto_mobile(risco_llm))

                checklist_llm = laudo_llm.get("checklist_vistoria")
                if isinstance(checklist_llm, list):
                    itens_limpos = [limpar_texto_mobile(str(i).strip()) for i in checklist_llm if str(i).strip()]
                    if itens_limpos:
                        checklist = itens_limpos[:3]

                visao_llm = laudo_llm.get("analise_visual")
                if foto_input and isinstance(visao_llm, str) and visao_llm.strip() and visao_llm.strip().lower() != "null":
                    analise_visual = limpar_texto_mobile(sanitizar_lgpd(visao_llm))

                origem_triagem = f"ZelaFix AI Triagem Multimodal (Groq {GROQ_MODEL} + RAG)"

            if len(parecer) > 150:
                corte = parecer[:147].rsplit(" ", 1)[0].rstrip(" ,;:-")
                parecer_ia = f"{corte or parecer[:147]}..."
            else:
                parecer_ia = parecer

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
                origem_triagem=origem_triagem
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
                origem_triagem=origem_triagem
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
