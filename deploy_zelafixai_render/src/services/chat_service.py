"""
Serviço Orquestrador do Chat Cidadão ZelaBot com RAG Vetorial e Persistência SQLite — ZelaFix AI
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)
"""
import uuid
import logging
from typing import Optional, List, Dict, Any
from src.core.config import AI_PROVIDER, FALLBACK_PROVIDER, GROQ_MODEL, GEMINI_MODEL
from src.core.prompts import formatar_prompt_rag
from src.schemas.chat import ChatRequest, ChatResponse, RetrievedSource
from src.services.knowledge_service import KnowledgeService
from src.services.groq_service import GroqService
from src.services.gemini_service import GeminiService
from src.repositories.chat_repository import ChatRepository
from src.utils.text import limpar_texto_mobile, normalizar_texto
from src.utils.guardrails import (
    detectar_emergencia_vital,
    montar_resposta_emergencia_vital,
    detectar_pedido_programacao,
    sanitizar_resposta_anti_codigo,
    sanitizar_lgpd
)

logger = logging.getLogger("ZelaFixAI.ChatService")

class ChatService:
    """
    Orquestra o pipeline completo de conversação cívica e RAG:
    1. Guardrail de Segurança Urbana e Risco Vital (fios energizados, desabamentos)
    2. Identificação de intenções sobre protocolo e chamado ativo
    3. Recuperação vetorial de normas e decretos municipais via RAG (Embeddings 512D)
    4. Inferência generativa primária (Groq / Gemini) com fallback automático
    5. Motor Local Resiliente de Alta Fidelidade (garantia de uptime 100%)
    6. Blindagem de escopo (anti-código e anti-alucinação) e conformidade LGPD
    7. Persistência de mensagens, auditoria de triagem e fontes no SQLite
    """

    @classmethod
    def _finalizar_e_persistir(
        cls,
        response: ChatResponse,
        request: ChatRequest,
        session_id: str,
        chamado_id: Optional[int],
        bairro: Optional[str]
    ) -> ChatResponse:
        """
        Atribui o sessionId ao response e grava o turno e o parecer no SQLite.
        """
        response.sessionId = session_id
        ChatRepository.salvar_interacao(
            session_id=session_id,
            pergunta=request.pergunta,
            resposta=response.resposta,
            categoria=response.categoria,
            urgencia=response.urgencia,
            origem_resposta=response.origem_resposta,
            chamado_id=chamado_id,
            bairro=bairro
        )
        return response

    @staticmethod
    def _resposta_guardrail_emergencia() -> ChatResponse:
        """Monta a resposta de emergência vital determinística ancorada nos protocolos municipais."""
        texto = montar_resposta_emergencia_vital()
        return ChatResponse(
            resposta=limpar_texto_mobile(texto),
            categoria="URGENTE",
            urgencia="URGENTE",
            acoes_recomendadas=[
                "Afastar-se do local imediatamente",
                "Acionar Corpo de Bombeiros (193)",
                "Acionar Defesa Civil (199)"
            ],
            origem_resposta="Guardrail de Segurança e Risco Vital ZelaFix",
            sources_used=[
                RetrievedSource(
                    id="emerg_vital",
                    source="Protocolo Integrado de Emergências Urbanas PMSP",
                    category="defesa_civil",
                    title="Alerta Imediato de Risco à Vida, Eletrocussão e Colapso Estrutural",
                    similarity_score=1.0
                )
            ],
            rag_grounded=True
        )

    @classmethod
    def _gerar_resposta_fallback_local(
        cls,
        pergunta: str,
        chunks: List[Dict[str, Any]],
        contexto_str: str = ""
    ) -> str:
        """
        Motor Heurístico Local de Alta Fidelidade:
        Gera resposta informativa, acolhedora e fundamentada diretamente dos chunks normativos
        sem necessidade de chamada a LLM externa (garantia de disponibilidade em cenários sem rede).
        """
        if not chunks:
            return (
                "🏛️ Olá! Sou o ZelaBot, assistente cívico da plataforma ZelaFix.\n\n"
                "Posso orientar você sobre serviços de zeladoria urbana na Cidade de São Paulo, tais como:\n"
                "• Operação tapa-buraco e prazos de pavimentação (24h a 48h)\n"
                "• Descarte gratuito de até 1 m³ de entulho em Ecopontos (Lei nº 13.478/2002)\n"
                "• Manutenção de iluminação pública e troca por LED (Ilumina SP)\n"
                "• Desobstrução de bueiros e prevenção de enchentes\n"
                "• Poda de árvores e desvios de trânsito pela CET\n\n"
                "Como posso ajudar a melhorar o seu bairro hoje?"
            )

        chunk_principal = chunks[0]
        linhas = [
            f"🏛️ Olá! De acordo com as diretrizes oficiais ({chunk_principal['source']}):\n",
            f"• {chunk_principal['title']}:",
            f"{chunk_principal['content']}\n"
        ]

        if len(chunks) > 1:
            chunk_sec = chunks[1]
            linhas.append(f"• Informação Complementar ({chunk_sec['title']}):\n{chunk_sec['content']}\n")

        linhas.append(
            "💡 Você pode cadastrar essa ocorrência diretamente no ZelaFix para gerarmos o laudo técnico "
            "e despacharmos para a Subprefeitura regional competente!"
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

            # 1. Guardrail de Emergência Vital (Risco Iminente de Morte / Eletrocussão)
            if detectar_emergencia_vital(request.pergunta):
                resp = cls._resposta_guardrail_emergencia()
                return cls._finalizar_e_persistir(resp, request, session_id, chamado_id, bairro)

            # 2. Identificação de Intenções Especiais (Dados do Chamado / Dúvidas Gerais)
            is_chamado_info_query = any(k in pergunta_norm for k in [
                "meu chamado", "dados do chamado", "qual o protocolo", "status do chamado",
                "acompanhar meu", "informacoes do chamado", "o que foi feito", "situacao do chamado",
                "detalhes da ocorrencia", "protocolo", "minha ocorrencia"
            ])

            is_general_query = any(k in pergunta_norm for k in [
                "o que voce faz", "o que e o zelafix", "como funciona", "quem e voce",
                "ajuda com meu bairro", "dicas de zeladoria", "o que voce sabe fazer"
            ])

            # 3. Recuperação de Chunks Normativos via RAG
            resultado_rag = KnowledgeService.buscar_chunks_rag(request.pergunta, top_k=3)
            chunks_recuperados = resultado_rag["chunks"]
            match_found = resultado_rag["match_found"]

            # Se for dúvida geral sem match direto, recupera diretrizes do ZelaFix e direitos cívicos
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

            # 4. Contexto Estruturado do Chamado (se fornecido)
            contexto_chamado_str = ""
            if c and (c.titulo or c.categoria):
                partes_contexto = [
                    f"Protocolo: {c.protocolo or 'ZF-TEMP'}",
                    f"Categoria: {c.categoria}",
                    f"Título: {c.titulo}",
                    f"Bairro: {c.bairro or 'Não informado'}",
                ]
                if c.descricao:
                    partes_contexto.append(f"Descrição: {c.descricao}")
                if c.logradouro:
                    partes_contexto.append(f"Logradouro: {c.logradouro}")
                if c.apoios_comunitarios is not None:
                    partes_contexto.append(f"Apoios Comunitários (+1): {c.apoios_comunitarios}")

                contexto_chamado_str = "[Ocorrência Ativa: " + ", ".join(partes_contexto) + "]"

            # 5. Montagem do Prompt Fundamentado
            prompt_fundamentado = formatar_prompt_rag(
                pergunta=request.pergunta,
                contexto_chamado_str=contexto_chamado_str,
                chunks_recuperados=chunks_recuperados,
                match_found=match_found,
                is_chamado_info_query=is_chamado_info_query,
                is_general_query=is_general_query
            )

            eh_pedido_programacao = detectar_pedido_programacao(request.pergunta)
            origem_ia = ""
            resposta_ia = None

            # 6. Tentativa de Geração com Provedor Primário e Fallback
            def _chamar_provedor(provedor: str) -> Optional[str]:
                if provedor == "groq":
                    return GroqService.gerar_resposta(prompt_fundamentado, request.historico)
                elif provedor == "gemini":
                    return GeminiService.gerar_resposta(prompt_fundamentado, request.historico)
                return None

            # Provedor Primário
            try:
                resposta_ia = _chamar_provedor(AI_PROVIDER)
                if resposta_ia:
                    origem_ia = f"ZelaBot ({AI_PROVIDER.capitalize()} Cloud)"
            except Exception as e:
                logger.warning(f"Erro no provedor primário ({AI_PROVIDER}): {e}")

            # Provedor Fallback em Nuvem
            if not resposta_ia:
                try:
                    resposta_ia = _chamar_provedor(FALLBACK_PROVIDER)
                    if resposta_ia:
                        origem_ia = f"ZelaBot ({FALLBACK_PROVIDER.capitalize()} Fallback Cloud)"
                except Exception as e:
                    logger.warning(f"Erro no provedor fallback ({FALLBACK_PROVIDER}): {e}")

            # Motor Local Resiliente de Alta Fidelidade (Fallback Offline)
            if not resposta_ia:
                resposta_ia = cls._gerar_resposta_fallback_local(request.pergunta, chunks_recuperados, contexto_chamado_str)
                origem_ia = "ZelaBot (Motor Heurístico Local Resiliente)"

            # 7. Sanitização de Saída (Anti-Código, LGPD e Mobile Clean)
            resposta_tratada = sanitizar_resposta_anti_codigo(resposta_ia, eh_pedido_programacao)
            resposta_tratada = sanitizar_lgpd(resposta_tratada)
            resposta_limpa = limpar_texto_mobile(resposta_tratada)

            # 8. Definição da Categoria e Urgência do Response
            categoria_resp = chunks_recuperados[0]["category"] if chunks_recuperados else "zeladoria"
            urgencia_resp = chunks_recuperados[0].get("urgency", "baixa") if chunks_recuperados else "baixa"

            acoes_recomendadas = [
                "Cadastrar relato detalhado no app ZelaFix",
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
