"""
Serviço Orquestrador do Chat Conversacional Cidadão (ZelaBot) — ZelaFix AI
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)

Integra RAG Normativo Municipal (PMSP), Consulta em Tempo Real ao Banco Oracle FIAP,
Inferência Multimodal via Groq (Qwen 3.8 27B) e Motor Heurístico Local Resiliente.
"""
import uuid
import logging
from typing import Optional, List, Dict, Any

from src.core.config import GROQ_MODEL
from src.core.prompts import formatar_prompt_rag
from src.schemas.chat import ChatRequest, ChatResponse, RetrievedSource, MensagemHistorico
from src.services.knowledge_service import KnowledgeService
from src.services.groq_service import GroqService
from src.services.chamado_oracle_service import ChamadoOracleService, TOOLS_ORACLE
from src.repositories.chat_repository import ChatRepository
from src.utils.guardrails import sanitizar_lgpd
from src.utils.text import normalizar_texto, limpar_texto_mobile

logger = logging.getLogger("ZelaFixAI.ChatService")


class ChatService:
    """
    Orquestrador conversacional do ZelaBot:
    1. Identifica menção a chamados e consulta a base Oracle da FIAP em tempo real.
    2. Recupera chunks normativos no ChromaDB via Similaridade de Cosseno (512D).
    3. Monta prompt fundamentado e aciona o Groq Cloud com Qwen 3.8 27B (multimodal com visão).
    4. Em caso de indisponibilidade externa, aciona o Motor Heurístico Local Resiliente.
    5. Higieniza a saída para renderização limpa no app React Native e audita no SQLite.
    """

    @classmethod
    def _gerar_acoes_recomendadas(
        cls,
        categoria: str,
        chamado_id: Optional[int],
        tem_oracle: bool
    ) -> List[str]:
        """Gera recomendações cívicas contextuais conforme categoria RAG e chamado ativo."""
        mapa_acoes = {
            "pavimentacao": [
                "Registrar foto evidenciando profundidade e risco na via pelo app ZelaFix",
                "Acompanhar prazo de tapa-buraco (24h a 48h) após abertura do protocolo",
            ],
            "drenagem": [
                "Não descartar lixo em sarjetas e solicitar hidrojateamento pelo ZelaFix",
                "Evitar atravessar pontos alagados e acionar Defesa Civil (199) em risco",
            ],
            "iluminacao": [
                "Informar poste apagado para atendimento da Ilumina SP (24h a 48h)",
                "Se houver fio partido ou faísca, isolar a área e ligar Bombeiros (193)",
            ],
            "limpeza_urbana": [
                "Descartar até 1 m³/dia gratuitamente no Ecoponto mais próximo",
                "Consultar calendário do Cata-Bagulho ou denunciar descarte irregular via SP156",
            ],
            "manejo_arboreo": [
                "Solicitar vistoria agronômica para poda preventiva pela Subprefeitura",
                "Em galho encostando na rede elétrica, acionar Enel / Bombeiros (193)",
            ],
            "sinalizacao_transito": [
                "Reportar semáforo apagado imediatamente para despacho da CET (2h a 4h)",
                "Informar cruzamento exato e logradouros afetados no app ZelaFix",
            ],
            "saneamento": [
                "Em vazamento contínuo de água ou esgoto, acionar emergência Sabesp (195)",
                "Registrar foto do ponto exato pelo ZelaFix para controle de erosão",
            ],
        }
        acoes = list(mapa_acoes.get(categoria, [
            "Registrar a ocorrência com localização exata e foto no app ZelaFix",
            "Recorrer à Ouvidoria Geral (SP156) se o prazo regulamentar expirar",
        ]))
        if tem_oracle and chamado_id:
            acoes.append(f"Compartilhar o chamado #{chamado_id} com vizinhos para somar apoios (+1)")
        else:
            acoes.append("Mobilizar apoios (+1) da vizinhança para elevar a prioridade do chamado")
        return acoes

    @classmethod
    def _finalizar_e_persistir(
        cls,
        resp: ChatResponse,
        pergunta_segura: str,
        session_id: str,
        chamado_id: Optional[int],
        bairro: Optional[str]
    ) -> ChatResponse:
        """Persiste mensagem sanitizada (LGPD) e auditoria no SQLite local."""
        resp.sessionId = session_id

        ChatRepository.salvar_mensagem(
            session_id=session_id,
            chamado_id=chamado_id,
            sender="user",
            text=pergunta_segura
        )

        ChatRepository.salvar_mensagem(
            session_id=session_id,
            chamado_id=chamado_id,
            sender="model",
            text=resp.resposta
        )

        parecer_audit = (resp.resposta[:147] + "...") if len(resp.resposta) > 150 else resp.resposta
        ChatRepository.salvar_triagem_audit(
            session_id=session_id,
            chamado_id=chamado_id,
            bairro=bairro or "São Paulo - SP",
            titulo=pergunta_segura[:80],
            parecer_ia=parecer_audit,
            categoria=resp.categoria,
            prioridade=resp.urgencia.upper(),
            orgao_responsavel="Zeladoria Urbana / Subprefeitura Regional",
            sla_horas=48,
            origem_triagem=resp.origem_resposta
        )

        return resp

    @classmethod
    def _gerar_resposta_fallback_local(
        cls,
        pergunta: str,
        chunks: List[Dict[str, Any]],
        contexto_chamado: str
    ) -> str:
        """
        Motor Heurístico Local de Alta Fidelidade:
        Gera resposta fundamentada nos Decretos Municipais mesmo sem internet ou sem Groq.
        """
        if not chunks:
            return (
                "🏛️ Olá! Sou o ZelaBot, assistente cívico de zeladoria urbana da plataforma ZelaFix.\n\n"
                "Posso orientá-lo sobre prazos e procedimentos da Prefeitura de São Paulo para:\n"
                "• Pavimentação asfáltica e operação tapa-buraco (Decreto nº 59.150/2019);\n"
                "• Limpeza e desobstrução de bueiros e bocas de lobo (Decreto nº 57.545/2016);\n"
                "• Iluminação pública e pontos escuros (Portaria SGM/SES nº 03/2021);\n"
                "• Regras de descarte gratuito em Ecopontos (Lei nº 13.478/2002);\n"
                "• Poda preventiva e manejo arbóreo (Lei nº 17.267/2020);\n"
                "• Falhas semafóricas e trânsito CET (Código de Trânsito Brasileiro);\n"
                "• Vazamentos de água e esgoto da concessionária Sabesp (Central 195).\n\n"
                "Como posso ajudar a melhorar o seu bairro hoje?"
            )

        chunk_principal = chunks[0]
        linhas = [
            f"🏛️ Informação Oficial de Zeladoria Urbana — Cidade de São Paulo",
            f"Base Normativa: {chunk_principal['source']}\n",
            f"• Diretriz ({chunk_principal['title']}):",
            chunk_principal["content"],
            ""
        ]

        if len(chunks) > 1:
            chunk_sec = chunks[1]
            linhas.append(f"• Informação Complementar ({chunk_sec['title']}):\n{chunk_sec['content']}\n")

        if contexto_chamado:
            linhas.append(f"📌 {contexto_chamado}\n")

        linhas.append(
            "💡 Você pode cadastrar ou acompanhar essa ocorrência diretamente no ZelaFix para gerarmos o laudo técnico "
            "e despacharmos para o órgão competente!"
        )

        return "\n".join(linhas)

    @classmethod
    def processar_chat(cls, request: ChatRequest) -> ChatResponse:
        sessao_existente = bool(request.sessionId and request.sessionId.strip())
        session_id = request.sessionId.strip() if sessao_existente else f"sess_{uuid.uuid4().hex[:12]}"
        c = request.chamadoContext
        chamado_id = c.id if c else None
        bairro = c.bairro if c else None

        try:
            # 1. Proteção LGPD na entrada ANTES de enviar à LLM, Oracle ou salvar no SQLite
            pergunta_segura = sanitizar_lgpd(request.pergunta)
            pergunta_norm = normalizar_texto(pergunta_segura)

            # 2. Memória automática multi-turno do SQLite quando cliente envia apenas sessionId
            historico_para_llm = request.historico
            if (not historico_para_llm) and sessao_existente:
                registros_db = ChatRepository.buscar_historico(session_id=session_id, limit=6)
                if registros_db:
                    historico_para_llm = [
                        MensagemHistorico(
                            sender=row["sender"],
                            text=sanitizar_lgpd(row["text"])
                        )
                        for row in registros_db
                    ]

            # 3. Consulta somente leitura ao Oracle FIAP (foto BLOB apenas sob demanda visual)
            id_detectado = ChamadoOracleService.extrair_id_chamado_da_pergunta(pergunta_segura)
            target_id = id_detectado or chamado_id
            precisa_foto_oracle = any(k in pergunta_norm for k in [
                "foto", "imagem", "analis", "visual", "veja", "mostre", "anexo", "parece"
            ])

            contexto_chamado_str, dados_oracle = ChamadoOracleService.obter_contexto_chamado_real(
                id_chamado=target_id,
                contexto_dto=c,
                incluir_foto=precisa_foto_oracle,
            )
            if contexto_chamado_str:
                contexto_chamado_str = sanitizar_lgpd(contexto_chamado_str)

            if dados_oracle:
                chamado_id = dados_oracle["id"]
                bairro = dados_oracle["bairro"]

            is_chamado_info_query = any(k in pergunta_norm for k in [
                "meu chamado", "dados do chamado", "qual o protocolo", "status do chamado",
                "acompanhar meu", "informacoes do chamado", "o que foi feito", "situacao do chamado",
                "detalhes da ocorrencia", "protocolo", "minha ocorrencia", "situacao do", "como esta o"
            ]) or (id_detectado is not None)

            is_general_query = any(k in pergunta_norm for k in [
                "o que voce faz", "o que e o zelafix", "como funciona", "quem e voce",
                "ajuda com meu bairro", "dicas de zeladoria", "o que voce sabe fazer"
            ])

            # 4. Recuperação de Chunks Normativos via RAG
            resultado_rag = KnowledgeService.buscar_chunks_rag(pergunta_segura, top_k=3)
            chunks_recuperados = resultado_rag["chunks"]
            match_found = resultado_rag["match_found"]

            if (is_general_query or not match_found) and not chunks_recuperados:
                chunk_default = KnowledgeService.buscar_chunk_por_id("faq_01")
                if chunk_default:
                    chunks_recuperados = [chunk_default]
                    match_found = True

            sources_used = [
                RetrievedSource(
                    id=chunk["id"],
                    source=chunk["source"],
                    category=chunk["category"],
                    title=chunk["title"],
                    similarity_score=chunk.get("similarity_score", 0.85)
                )
                for chunk in chunks_recuperados
            ]

            # 5. Foto para Visão Computacional Multimodal (app ou BLOB do Oracle sob demanda)
            imagem_para_inferencia: Optional[Any] = (
                request.foto_base64
                or (c.foto_base64 if c else None)
                or (dados_oracle.get("foto_bytes") if dados_oracle else None)
            )

            # 6. Montagem do Prompt Fundamentado e Inferência Multimodal Groq Qwen 3.8 27B
            prompt_fundamentado = formatar_prompt_rag(
                pergunta=pergunta_segura,
                contexto_chamado_str=contexto_chamado_str,
                chunks_recuperados=chunks_recuperados,
                match_found=match_found,
                is_chamado_info_query=is_chamado_info_query
            )

            origem_ia = ""
            resposta_ia = None

            try:
                habilitar_tool_oracle = (target_id is None) and (c is None) and (not imagem_para_inferencia)
                resposta_ia = GroqService.gerar_resposta(
                    prompt_atual=prompt_fundamentado,
                    historico=historico_para_llm,
                    imagem_base64=imagem_para_inferencia,
                    tools=TOOLS_ORACLE if habilitar_tool_oracle else None,
                    tool_executor=ChamadoOracleService.executar_tool_oracle if habilitar_tool_oracle else None,
                )
                if resposta_ia:
                    origem_ia = f"ZelaBot (Groq {GROQ_MODEL})"
            except Exception as e:
                logger.warning(f"Falha na chamada do Groq ({GROQ_MODEL}): {e}")

            if not resposta_ia:
                resposta_ia = cls._gerar_resposta_fallback_local(
                    pergunta_segura,
                    chunks_recuperados,
                    contexto_chamado_str
                )
                origem_ia = "ZelaBot (Motor Heurístico Local Resiliente)"

            # 7. Higienização de Saída (LGPD e Mobile Clean)
            resposta_tratada = sanitizar_lgpd(resposta_ia)
            resposta_limpa = limpar_texto_mobile(resposta_tratada)

            categoria_resp = chunks_recuperados[0]["category"] if chunks_recuperados else "zeladoria"
            urgencia_resp = chunks_recuperados[0].get("urgency", "baixa") if chunks_recuperados else "baixa"
            acoes_recomendadas = cls._gerar_acoes_recomendadas(
                categoria_resp,
                chamado_id=chamado_id,
                tem_oracle=bool(dados_oracle)
            )

            chat_response = ChatResponse(
                resposta=resposta_limpa,
                categoria=categoria_resp,
                urgencia=urgencia_resp,
                acoes_recomendadas=acoes_recomendadas,
                origem_resposta=origem_ia,
                sources_used=sources_used,
                rag_grounded=match_found and len(sources_used) > 0
            )

            return cls._finalizar_e_persistir(chat_response, pergunta_segura, session_id, chamado_id, bairro)

        except Exception as e:
            logger.error(f"Erro inesperado no ChatService: {e}")
            return ChatResponse(
                resposta="🏛️ Olá! O serviço ZelaBot está operando em modo de contingência. Para solicitações urgentes, consulte a Subprefeitura regional ou a central SP156.",
                categoria="geral",
                urgencia="baixa",
                origem_resposta="ZelaBot (Fallback Resiliente de Contingência)",
                sessionId=session_id
            )
