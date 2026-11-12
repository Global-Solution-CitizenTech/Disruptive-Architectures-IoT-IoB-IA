"""
Serviço de Inferência: Cliente Groq Cloud Multimodal (Qwen 3.8 27B) — ZelaFix AI
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)

Suporta processamento multimodal (texto e visão computacional de fotos urbanas).
"""
import io
import base64
import logging
from typing import Optional, List, Dict, Any, Union
from groq import Groq
from src.core.config import GROQ_MODEL, GROQ_API_KEY
from src.core.prompts import SYSTEM_INSTRUCTION
from src.schemas.chat import MensagemHistorico

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

logger = logging.getLogger("ZelaFixAI.GroqService")


class GroqService:
    """
    Comunicação com a API do Groq usando o modelo multimodal `qwen/qwen3.8-27b`.
    Suporta prompts textuais e análise de imagens (fotos de ocorrências urbanas).
    """

    MAX_HISTORICO_TURNOS = 6
    _client: Optional[Groq] = None

    @classmethod
    def _obter_cliente(cls) -> Optional[Groq]:
        """Obtém ou instancia o cliente Groq reutilizável (singleton)."""
        if not GROQ_API_KEY:
            return None
        if cls._client is None:
            cls._client = Groq(api_key=GROQ_API_KEY)
        return cls._client

    @classmethod
    def _sanitizar_imagem_base64(cls, imagem_raw: Union[str, bytes]) -> Optional[str]:
        """
        Valida e prepara a imagem para o Groq Qwen:
        - Garante formato base64 puro.
        - Valida dimensões mínimas (Groq exige >= 32px em cada dimensão).
        - Converte para JPEG otimizado caso necessário.
        """
        try:
            dados_bytes = b""
            if isinstance(imagem_raw, bytes):
                dados_bytes = imagem_raw
            elif isinstance(imagem_raw, str):
                limpa = imagem_raw.strip()
                if "," in limpa and limpa.startswith("data:image"):
                    limpa = limpa.split(",", 1)[1]
                dados_bytes = base64.b64decode(limpa)

            if len(dados_bytes) < 32:
                return None

            if HAS_PIL:
                try:
                    img = Image.open(io.BytesIO(dados_bytes))
                    # Se dimensões forem menores que 32px, redimensiona para 64x64
                    if img.width < 32 or img.height < 32:
                        img = img.resize((max(32, img.width), max(32, img.height)))
                    buf = io.BytesIO()
                    img.convert("RGB").save(buf, format="JPEG", quality=85)
                    return base64.b64encode(buf.getvalue()).decode("utf-8")
                except Exception:
                    pass

            return base64.b64encode(dados_bytes).decode("utf-8")
        except Exception as e:
            logger.warning(f"Erro ao processar imagem para o Groq: {e}")
            return None

    @classmethod
    def formatar_mensagens(
        cls,
        prompt_atual: str,
        historico: Optional[List[MensagemHistorico]] = None,
        imagem_base64: Optional[Union[str, bytes]] = None
    ) -> List[Dict[str, Any]]:
        """Formata histórico, texto e foto no padrão OpenAI/Groq Chat Completions."""
        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_INSTRUCTION}
        ]

        # Adiciona histórico multi-turno (apenas texto para economizar tokens de contexto)
        for msg in (historico or [])[-cls.MAX_HISTORICO_TURNOS:]:
            if not msg.text or not msg.text.strip():
                continue
            role = "user" if msg.sender.lower() in ["user", "municipe", "cidadao", "cliente"] else "assistant"
            messages.append({"role": role, "content": msg.text.strip()})

        # Processa imagem caso fornecida
        img_b64 = cls._sanitizar_imagem_base64(imagem_base64) if imagem_base64 else None

        if img_b64:
            user_content = [
                {"type": "text", "text": prompt_atual.strip()},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{img_b64}"
                    }
                }
            ]
            messages.append({"role": "user", "content": user_content})
        else:
            messages.append({"role": "user", "content": prompt_atual.strip()})

        return messages

    @classmethod
    def gerar_resposta(
        cls,
        prompt_atual: str,
        historico: Optional[List[MensagemHistorico]] = None,
        imagem_base64: Optional[Union[str, bytes]] = None
    ) -> Optional[str]:
        """
        Executa inferência com Qwen 3.8 27B via Groq Cloud.
        Retorna o texto gerado ou None se a chamada falhar (acionando fallback local).
        """
        client = cls._obter_cliente()
        if client is None:
            return None

        try:
            messages = cls.formatar_mensagens(prompt_atual, historico, imagem_base64)
            completion = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=messages,
                temperature=0.5,
                max_tokens=800
            )
            if completion.choices and completion.choices[0].message.content:
                return completion.choices[0].message.content.strip()
            return None
        except Exception as e:
            logger.warning(f"Falha na inferência Groq ({GROQ_MODEL}): {e}")
            return None
