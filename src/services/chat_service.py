"""
Serviço de Chat Inteligente Cidadão (ZelaBot / Assistente RAG de Zeladoria)
Fornece atendimento interativo ao morador baseado nas normas e decretos municipais de SP
"""

from typing import Optional, List
from ..rag.knowledge_retriever import KnowledgeRetriever
from ..genai.gemini_client import GeminiClient
from ..schemas.chamado_ia import (
    ChatCidadaoRequestDTO,
    ChatCidadaoResponseDTO,
    ChatMessageDTO
)
from ..config import CATEGORIAS_OFICIAIS, ORGAOS_COMPETENTES

CHAT_SYSTEM_INSTRUCTION = """Você é o ZelaBot, o Assistente Cidadão de Zeladoria Urbana Inteligente da Cidade de São Paulo e do aplicativo ZelaFix (ODS 11 da ONU).
Sua missão é atender os moradores de forma acolhedora, clara e objetiva, esclarecendo:
1. Como abrir chamados e relatar problemas urbanos no app ZelaFix (buracos, bueiros, iluminação, árvores, entulho, etc.).
2. Prazos e regras dos Decretos Municipais de São Paulo.
3. Qual órgão é responsável por cada demanda e quando acionar órgãos de emergência (Defesa Civil 199, Bombeiros 193).

Sempre oriente o morador com base nas normas fornecidas e encoraje-o a abrir um chamado no ZelaFix com foto e localização GPS.
"""

class ChatCidadaoService:
    """Assistente conversacional para suporte aos cidadãos integrado ao RAG."""

    def __init__(
        self,
        retriever: Optional[KnowledgeRetriever] = None,
        gemini_client: Optional[GeminiClient] = None
    ):
        self.rag = retriever or KnowledgeRetriever()
        self.genai = gemini_client or GeminiClient()

    def responder_cidadao(self, req: ChatCidadaoRequestDTO) -> ChatCidadaoResponseDTO:
        msg = req.mensagem.strip()
        msg_lower = msg.lower()

        # 1. Identifica categoria provável da dúvida
        categoria_identificada = None
        for cat in CATEGORIAS_OFICIAIS:
            termos = {
                "Buraco na Rua": ["buraco", "asfalto", "cratera", "pavimento", "pista", "via"],
                "Bueiro Entupido": ["bueiro", "boca de lobo", "enchente", "alagamento", "ralo"],
                "Iluminação Pública": ["poste", "lâmpada", "apagado", "escuridão", "luz", "iluminação"],
                "Entulho e Descarte Irregular": ["entulho", "lixo", "calçada", "descarte", "sofá", "obra"],
                "Poda de Árvore": ["árvore", "galho", "poda", "folha", "tronco", "raiz"],
                "Sinalização e Trânsito": ["semáforo", "sinal", "placa", "faixa", "trânsito"],
                "Vazamento de Água": ["vazamento", "água", "cano", "adutora", "sarjeta", "sabesp"]
            }.get(cat, [])

            if any(t in msg_lower for t in termos):
                categoria_identificada = cat
                break

        # 2. Busca contextual no RAG sobre o tema abordado
        rag_context, rag_chunks, rag_meta = self.rag.retrieve_context(
            titulo=msg,
            descricao="",
            categoria=categoria_identificada,
            top_k=2
        )

        base_legal = rag_meta.get("base_legal", "Decretos de Zeladoria Urbana da Cidade de São Paulo")
        orgao = rag_meta.get("orgao_competente", "Central de Zeladoria Municipal 156")
        sla_horas = rag_meta.get("sla_horas", 48)

        # 3. Geração de resposta (Gemini ou Fallback determinístico especialista)
        sugestao_abertura = categoria_identificada is not None or any(t in msg_lower for t in ["como fazer", "onde reclamar", "consertar", "arrumar", "denunciar", "solicitar"])

        # Monta resposta de fallback de alta fidelidade
        resposta_texto = ""
        if categoria_identificada == "Buraco na Rua":
            resposta_texto = (
                f"Olá! Buracos no asfalto são de responsabilidade da Subprefeitura regional (Operação Tapa-Buraco). "
                f"De acordo com o {base_legal}, o prazo previsto para reparo é de {sla_horas} horas. "
                f"Você pode abrir um chamado diretamente aqui no ZelaFix anexando uma foto e a localização GPS da via!"
            )
        elif categoria_identificada == "Bueiro Entupido":
            resposta_texto = (
                f"Olá! O desentupimento de bocas de lobo e galerias pluviais é realizado pela {orgao} com caminhão de hidrojateamento. "
                f"Pelo {base_legal}, o atendimento é prioritário ({sla_horas}h) em pontos de alagamento. "
                f"Recomendamos abrir um relato no ZelaFix para que a equipe de vistoria seja despachada."
            )
        elif categoria_identificada == "Iluminação Pública":
            resposta_texto = (
                f"Olá! A manutenção de postes e troca de lâmpadas queimadas é operada pela {orgao}. "
                f"Conforme a {base_legal}, o prazo padrão para troca de luminárias é de até {sla_horas} horas. "
                f"Se houver fiação solta ou faíscas com risco de choque elétrico, acione imediatamente os Bombeiros (193)."
            )
        elif categoria_identificada == "Poda de Árvore":
            resposta_texto = (
                f"Olá! A poda em vias públicas requer laudo agronômico da {orgao}. "
                f"Pela {base_legal}, caso galhos estejam encostando na rede de alta tensão da Enel ou houver risco de queda, o atendimento é emergencial. "
                f"Em caso de risco de queda iminente, contate a Defesa Civil pelo 199."
            )
        elif categoria_identificada == "Entulho e Descarte Irregular":
            resposta_texto = (
                f"Olá! O descarte de entulho em calçadas é infração prevista pela {base_legal}. "
                f"A {orgao} efetua a remoção e fiscalização em até {sla_horas} horas. "
                f"Cidadãos podem descartar até 1m³ gratuitamente nos Ecopontos oficiais da Prefeitura."
            )
        elif categoria_identificada == "Vazamento de Água":
            resposta_texto = (
                f"Olá! Vazamentos de água potável ou esgoto em vias públicas devem ser contidos pela {orgao}. "
                f"O prazo normativo de contenção para rompimento de ramal é de até {sla_horas} horas."
            )
        elif categoria_identificada == "Sinalização e Trânsito":
            resposta_texto = (
                f"Olá! Semáforos e placas são geridos pela {orgao}. Falhas em semáforos de cruzamentos movimentados têm prazo de emergência de 4 horas."
            )
        else:
            resposta_texto = (
                f"Olá! Eu sou o ZelaBot, seu assistente de zeladoria urbana da Prefeitura de São Paulo. "
                f"Posso tirar dúvidas sobre prazos, leis municipais (tapa-buraco, bueiros, iluminação, podas e descarte de lixo) "
                f"e ajudar você a protocolar ocorrências pelo app ZelaFix. Como posso te ajudar hoje?"
            )

        # Se houver client Gemini ativo, enriquece a resposta
        if self.genai.client:
            try:
                prompt_chat = (
                    f"{CHAT_SYSTEM_INSTRUCTION}\n\n"
                    f"DADOS REGULATÓRIOS DO RAG:\n{rag_context}\n\n"
                    f"MENSAGEM DO MORADOR: {msg}\n\n"
                    f"Responda ao morador de forma acolhedora, objetiva e orientativa."
                )
                gemini_resp = self.genai.client.models.generate_content(
                    model=self.genai.model_name,
                    contents=prompt_chat
                )
                if gemini_resp and gemini_resp.text:
                    resposta_texto = gemini_resp.text.strip()
            except Exception:
                pass

        return ChatCidadaoResponseDTO(
            resposta=resposta_texto,
            baseLegalUtilizada=base_legal,
            orgaoCompetenteSugerido=orgao,
            telefonesUteis=["Central SP: 156", "Defesa Civil: 199", "Bombeiros: 193", "SAMU: 192"],
            sugestaoAberturaChamado=sugestao_abertura,
            categoriaSugerida=categoria_identificada
        )

