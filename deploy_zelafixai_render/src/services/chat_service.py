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
from src.schemas.chat import ChatRequest, ChatResponse, RetrievedSource
from src.services.knowledge_service import KnowledgeService
from src.services.groq_service import GroqService
from src.services.chamado_oracle_service import ChamadoOracleService
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
    def _finalizar_e_persistir(
        cls,
        resp: ChatResponse,
        request: ChatRequest,
        session_id: str,
        chamado_id: Optional[int],
        bairro: Optional[str]
    ) -> ChatResponse:
        """Persiste mensagem de entrada e resposta de auditoria no SQLite local."""
        resp.sessionId = session_id

        # Salva mensagem do munícipe
        ChatRepository.salvar_mensagem(
            session_id=session_id,
            chamado_id=chamado_id,
            sender="user",
            text=request.pergunta
        )

        # Salva resposta do ZelaBot
        ChatRepository.salvar_mensagem(
            session_id=session_id,
            chamado_id=chamado_id,
            sender="model",
            text=resp.resposta
        )

        # Registra parecer de auditoria
        parecer_audit = (resp.resposta[:147] + "...") if len(resp.resposta) > 150 else resp.resposta
        ChatRepository.salvar_triagem_audit(
            session_id=session_id,
            chamado_id=chamado_id,
            bairro=bairro or "São Paulo - SP",
            titulo=request.pergunta[:80],
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
        session_id = request.sessionId or f"sess_{uuid.uuid4().hex[:12]}"
        c = request.chamadoContext
        chamado_id = c.id if c else None
        bairro = c.bairro if c else None

        try:
            pergunta_norm = normalizar_texto(request.pergunta)

            # 1. Identificação de Intenções e Consulta ao Banco Oracle FIAP
            id_detectado = ChamadoOracleService.extrair_id_chamado_da_pergunta(request.pergunta)
            target_id = id_detectado or chamado_id

            contexto_chamado_str, dados_oracle = ChamadoOracleService.obter_contexto_chamado_real(
                id_chamado=target_id,
                contexto_dto=c
            )

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

            # 2. Recuperação de Chunks Normativos via RAG
            resultado_rag = KnowledgeService.buscar_chunks_rag(request.pergunta, top_k=3)
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

            # 3. Extração de Foto para Visão Computacional Multimodal (Groq Qwen 3.8 27B)
            imagem_para_inferencia: Optional[Any] = (
                request.foto_base64
                or (c.foto_base64 if c else None)
                or (dados_oracle.get("foto_bytes") if dados_oracle else None)
            )

            # 4. Montagem do Prompt Fundamentado
            prompt_fundamentado = formatar_prompt_rag(
                pergunta=request.pergunta,
                contexto_chamado_str=contexto_chamado_str,
                chunks_recuperados=chunks_recuperados,
                match_found=match_found,
                is_chamado_info_query=is_chamado_info_query,
                is_general_query=is_general_query
            )

            origem_ia = ""
            resposta_ia = None

            # 5. Inferência Primária com Groq Cloud (Qwen 3.8 27B Multimodal)
            try:
                resposta_ia = GroqService.gerar_resposta(
                    prompt_atual=prompt_fundamentado,
                    historico=request.historico,
                    imagem_base64=imagem_para_inferencia
                )
                if resposta_ia:
                    origem_ia = f"ZelaBot (Groq {GROQ_MODEL})"
            except Exception as e:
                logger.warning(f"Falha na chamada do Groq ({GROQ_MODEL}): {e}")

            # 6. Motor Heurístico Local Resiliente (Fallback Offline)
            if not resposta_ia:
                resposta_ia = cls._gerar_resposta_fallback_local(
                    request.pergunta,
                    chunks_recuperados,
                    contexto_chamado_str
                )
                origem_ia = "ZelaBot (Motor Heurístico Local Resiliente)"

            # 7. Higienização de Saída (LGPD e Mobile Clean)
            resposta_tratada = sanitizar_lgpd(resposta_ia)
            resposta_limpa = limpar_texto_mobile(resposta_tratada)

            # 9. Definição da Categoria e Urgência do Response
            categoria_resp = chunks_recuperados[0]["category"] if chunks_recuperados else "zeladoria"
            urgencia_resp = chunks_recuperados[0].get("urgency", "baixa") if chunks_recuperados else "baixa"

            acoes_recomendadas = [
                "Cadastrar relato detalhado com fotos no app ZelaFix",
                "Solicitar confirmação e apoios de outros vizinhos (+1)",
                "Acompanhar o prazo de execução via protocolo oficial"
            ]

            chat_response = ChatResponse(
                resposta=resposta_limpa,
                categoria=categoria_resp,
                urgencia=urgencia_resp,
                acoes_recomendadas=acoes_recomendadas,
                origem_resposta=origem_ia,
                sources_used=sources_used,
                rag_grounded=match_found and len(sources_used) > 0
            )

            return cls._finalizar_e_persistir(chat_response, request, session_id, chamado_id, bairro)

        except Exception as e:
            logger.error(f"Erro inesperado no ChatService: {e}")
            return ChatResponse(
                resposta="🏛️ Olá! O serviço ZelaBot está operando em modo de contingência. Para solicitações urgentes, consulte a Subprefeitura regional ou a central SP156.",
                categoria="geral",
                urgencia="baixa",
                origem_resposta="ZelaBot (Fallback Resiliente de Contingência)",
                sessionId=session_id
            )
