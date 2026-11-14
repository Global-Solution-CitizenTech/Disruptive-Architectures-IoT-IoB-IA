"""
Serviço Orquestrador do Chat Conversacional Cidadão (ZelaBot) — ZelaFix AI
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)
"""
import uuid
import logging
from typing import Optional, List, Any
from pydantic import BaseModel, Field

from src.core.config import AI_EMBEDDING_MODEL
from src.core.prompts import SYSTEM_INSTRUCTION, formatar_prompt_rag
from src.schemas.chat import ChatRequest, ChatResponse, RetrievedSource, MensagemHistorico
from src.services.knowledge_service import KnowledgeService
from src.services.foundry_service import FoundryService
from src.services.chamado_oracle_service import ChamadoOracleService, TOOLS_ZELAFIX
from src.repositories.chat_repository import ChatRepository
from src.utils.guardrails import sanitizar_lgpd
from src.utils.text import normalizar_texto, limpar_texto_mobile

logger = logging.getLogger("ZelaFixAI.ChatService")

_SLA_POR_URGENCIA = {"URGENTE": 12, "alta": 24, "media": 48, "baixa": 72}


class _ChatIaSchema(BaseModel):
    resposta: str
    categoria: str = "zeladoria"
    urgencia: str = "baixa"
    acoes_recomendadas: List[str] = Field(default_factory=list)


class ChatService:
    """
    Orquestrador conversacional do ZelaBot:
    - Proteção LGPD na entrada e na saída.
    - RAG semântico em nuvem (ChromaDB + Azure AI Foundry Embeddings).
    - Tool Calling nativo para consultas Oracle FIAP (`SELECT` somente leitura) e SLA.
    - Saída estruturada validada via Pydantic + sanitização Mobile Clean.
    """

    @classmethod
    def _fallback_contingencia(
        cls,
        chunks: List[dict],
        contexto_chamado: str,
    ) -> _ChatIaSchema:
        if chunks:
            c = chunks[0]
            txt = (
                f"🏛️ Diretriz Oficial — {c['title']} ({c['source']})\n\n"
                f"• Orientação: {c['content']}"
            )
            if contexto_chamado:
                txt += f"\n\n📌 {contexto_chamado}"
            return _ChatIaSchema(
                resposta=txt,
                categoria=c["category"],
                urgencia=c.get("urgency", "baixa"),
                acoes_recomendadas=[
                    "Acompanhar ou registrar a ocorrência com foto pelo app ZelaFix",
                    "Utilizar os canais oficiais (SP156 / 193 / 199) em situações de risco",
                ],
            )

        msg = "🏛️ Olá! Sou o ZelaBot (ZelaFix). Posso ajudar com dúvidas sobre tapa-buraco, bueiros, iluminação, podas, Ecopontos, trânsito CET, Sabesp e protocolos do app."
        if contexto_chamado:
            msg += f"\n\n📌 {contexto_chamado}"
        return _ChatIaSchema(
            resposta=msg,
            categoria="zeladoria",
            urgencia="baixa",
            acoes_recomendadas=["Descrever o problema urbano ou informar o número do protocolo (#ID)"],
        )

    @classmethod
    def processar_chat(cls, request: ChatRequest) -> ChatResponse:
        sessao_existente = bool(request.sessionId and request.sessionId.strip())
        session_id = request.sessionId.strip() if sessao_existente else f"sess_{uuid.uuid4().hex[:12]}"
        c = request.chamadoContext
        chamado_id = c.id if c else None
        bairro = c.bairro if c else None

        try:
            pergunta_segura = sanitizar_lgpd(request.pergunta)
            pergunta_norm = normalizar_texto(pergunta_segura)

            # 1. Memória conversacional multi-turno via SQLite quando sessão já existe
            historico_para_llm = request.historico
            if not historico_para_llm and sessao_existente:
                registros_db = ChatRepository.buscar_historico(session_id=session_id, limit=6)
                if registros_db:
                    historico_para_llm = [
                        MensagemHistorico(sender=row["sender"], text=sanitizar_lgpd(row["text"]))
                        for row in registros_db
                    ]

            # 2. Fast-path somente leitura no Oracle FIAP por #ID ou contexto do app
            id_detectado = ChamadoOracleService.extrair_id_chamado_da_pergunta(pergunta_segura)
            target_id = id_detectado or chamado_id
            precisa_foto_oracle = any(
                k in pergunta_norm for k in ("foto", "imagem", "analis", "visual", "veja", "mostre", "anexo")
            )

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

            # 3. Recuperação Semântica RAG (Azure AI Foundry Embeddings + ChromaDB)
            resultado_rag = KnowledgeService.buscar_chunks_rag(pergunta_segura, top_k=3)
            chunks_recuperados = resultado_rag["chunks"]
            match_found = resultado_rag["match_found"]

            sources_used = [
                RetrievedSource(
                    id=chunk["id"],
                    source=chunk["source"],
                    category=chunk["category"],
                    title=chunk["title"],
                    similarity_score=chunk.get("similarity_score", 0.0),
                )
                for chunk in chunks_recuperados
            ]

            imagem_para_inferencia: Optional[Any] = (
                request.foto_base64
                or (c.foto_base64 if c else None)
                or (dados_oracle.get("foto_bytes") if dados_oracle else None)
            )

            # 4. Inferência Estruturada + Tool Calling no Azure AI Foundry
            prompt_fundamentado = formatar_prompt_rag(
                pergunta=pergunta_segura,
                contexto_chamado_str=contexto_chamado_str,
                chunks_recuperados=chunks_recuperados,
                match_found=match_found,
            )

            precisa_tool_consulta = any(
                k in pergunta_norm
                for k in ("chamado", "protocolo", "ocorrencia", "bairro", "abert", "status", "situacao", "sla", "recente", "lista")
            )
            habilitar_tools = (target_id is None) and (c is None) and (not imagem_para_inferencia) and precisa_tool_consulta
            ia_result, modelo_usado = FoundryService.gerar_estruturado(
                schema_cls=_ChatIaSchema,
                system_prompt=SYSTEM_INSTRUCTION,
                user_prompt=prompt_fundamentado,
                historico=historico_para_llm,
                imagem_base64=imagem_para_inferencia,
                tools=TOOLS_ZELAFIX if habilitar_tools else None,
                tool_executor=ChamadoOracleService.executar_tool if habilitar_tools else None,
            )

            if ia_result is not None:
                origem_ia = f"ZelaBot (Azure AI Foundry: {modelo_usado} + {AI_EMBEDDING_MODEL})"
            else:
                ia_result = cls._fallback_contingencia(chunks_recuperados, contexto_chamado_str)
                origem_ia = "ZelaBot (Contingência Normativa Local)"

            # 5. Sanitização LGPD + Mobile Clean + Auditoria SQLite
            resposta_limpa = limpar_texto_mobile(sanitizar_lgpd(ia_result.resposta))
            acoes_limpas = [
                limpar_texto_mobile(sanitizar_lgpd(a))
                for a in ia_result.acoes_recomendadas
                if a and a.strip()
            ][:3]

            urgencia_norm = ia_result.urgencia.strip()
            if urgencia_norm.lower() == "urgente":
                urgencia_norm = "URGENTE"
            elif urgencia_norm.lower() in {"baixa", "media", "alta"}:
                urgencia_norm = urgencia_norm.lower()
            else:
                urgencia_norm = chunks_recuperados[0].get("urgency", "baixa") if chunks_recuperados else "baixa"

            categoria_limpa = ia_result.categoria.strip() or (
                chunks_recuperados[0]["category"] if chunks_recuperados else "zeladoria"
            )

            ChatRepository.salvar_interacao(
                session_id=session_id,
                chamado_id=chamado_id,
                bairro=bairro or "São Paulo - SP",
                pergunta=pergunta_segura,
                resposta=resposta_limpa,
                categoria=categoria_limpa,
                urgencia=urgencia_norm.upper(),
                orgao_responsavel="Zeladoria Urbana / Subprefeitura Regional",
                sla_horas=_SLA_POR_URGENCIA.get(urgencia_norm, 48),
                origem_resposta=origem_ia,
            )

            return ChatResponse(
                resposta=resposta_limpa,
                categoria=categoria_limpa,
                urgencia=urgencia_norm,
                acoes_recomendadas=acoes_limpas or None,
                origem_resposta=origem_ia,
                sessionId=session_id,
                sources_used=sources_used,
                rag_grounded=match_found and len(sources_used) > 0,
            )
        except Exception as err:
            logger.error(f"Erro inesperado no ChatService: {err}")
            return ChatResponse(
                resposta="🏛️ Olá! O ZelaBot está em modo de contingência no momento. Para demandas urgentes, utilize a central SP156.",
                categoria="geral",
                urgencia="baixa",
                origem_resposta="ZelaBot (Contingência)",
                sessionId=session_id,
            )
