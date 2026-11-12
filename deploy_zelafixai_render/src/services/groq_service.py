"""
Serviço de Inferência: Cliente Groq Cloud Multimodal (Qwen 3.8 27B) — ZelaFix AI
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)

Suporta processamento multimodal (texto e visão computacional de fotos urbanas).
"""
import io
import re
import json
import base64
import logging
from typing import Optional, List, Dict, Any, Union
from groq import Groq
from src.core.config import GROQ_MODEL, GROQ_API_KEY, GROQ_BASE_URL, GROQ_TIMEOUT_SECONDS
from src.core.prompts import SYSTEM_INSTRUCTION
from src.schemas.chat import MensagemHistorico

try:
    from PIL import Image, ImageOps
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

logger = logging.getLogger("ZelaFixAI.GroqService")

SYSTEM_TRIAGEM_JSON = (
    "Você é um engenheiro especialista em triagem urbana da Prefeitura de São Paulo (ZelaFix). "
    "Responda exclusivamente com um objeto JSON válido seguindo exatamente os campos solicitados."
)


class GroqService:
    """
    Comunicação com a API do Groq usando o modelo multimodal `qwen/qwen3.8-27b`.
    Suporta prompts textuais e análise de imagens (fotos de ocorrências urbanas).
    """

    MAX_HISTORICO_TURNOS = 6
    _client: Optional[Groq] = None

    @classmethod
    def _obter_cliente(cls) -> Optional[Groq]:
        """Obtém ou instancia o cliente Groq reutilizável com base_url normalizada e timeout."""
        if not GROQ_API_KEY:
            return None
        if cls._client is None:
            # O SDK oficial Groq acrescenta '/openai/v1/*' automaticamente; evita duplicação se .env trouxer '/openai/v1'
            base_url = (GROQ_BASE_URL or "https://api.groq.com").strip().rstrip("/")
            if base_url.endswith("/openai/v1"):
                base_url = base_url[: -len("/openai/v1")]
            cls._client = Groq(
                api_key=GROQ_API_KEY,
                base_url=base_url or "https://api.groq.com",
                timeout=GROQ_TIMEOUT_SECONDS,
                max_retries=1,
            )
        return cls._client

    @classmethod
    def _sanitizar_imagem_base64(cls, imagem_raw: Union[str, bytes]) -> Optional[str]:
        """
        Valida e otimiza a imagem para o Groq Qwen Multimodal:
        - Extrai bytes de base64/data-URI.
        - Corrige rotação EXIF de câmeras mobile e limita dimensões máximas a 1024x1024.
        - Rejeita bytes corrompidos com None para não derrubar a chamada de texto.
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
                    img = ImageOps.exif_transpose(img)
                    if img.width < 32 or img.height < 32:
                        img = img.resize((max(32, img.width), max(32, img.height)))
                    elif img.width > 1024 or img.height > 1024:
                        img.thumbnail((1024, 1024))
                    buf = io.BytesIO()
                    img.convert("RGB").save(buf, format="JPEG", quality=82)
                    return base64.b64encode(buf.getvalue()).decode("utf-8")
                except Exception as img_err:
                    logger.warning(f"Imagem inválida ou corrompida ignorada antes do envio ao Groq: {img_err}")
                    return None

            return base64.b64encode(dados_bytes).decode("utf-8")
        except Exception as e:
            logger.warning(f"Erro ao processar imagem para o Groq: {e}")
            return None

    @staticmethod
    def _limpar_raciocinio(texto: str) -> str:
        """Remove eventuais tags <think>...</think> emitidas por modelos Qwen3."""
        limpo = re.sub(r"<think>.*?</think>", "", texto, flags=re.DOTALL | re.IGNORECASE)
        limpo = re.sub(r"<think>.*$", "", limpo, flags=re.DOTALL | re.IGNORECASE)
        return limpo.strip()

    @classmethod
    def formatar_mensagens(
        cls,
        prompt_atual: str,
        historico: Optional[List[MensagemHistorico]] = None,
        imagem_base64: Optional[Union[str, bytes]] = None,
        system_prompt: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Formata histórico, texto e foto no padrão OpenAI/Groq Chat Completions."""
        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": system_prompt or SYSTEM_INSTRUCTION}
        ]

        for msg in (historico or [])[-cls.MAX_HISTORICO_TURNOS:]:
            if not msg.text or not msg.text.strip():
                continue
            role = "user" if msg.sender.lower() in ["user", "municipe", "cidadao", "cliente"] else "assistant"
            messages.append({"role": role, "content": msg.text.strip()})

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
        Retorna o texto limpo gerado ou None se a chamada falhar (acionando fallback local).
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
                limpo = cls._limpar_raciocinio(completion.choices[0].message.content)
                return limpo or None
            return None
        except Exception as e:
            logger.warning(f"Falha na inferência Groq ({GROQ_MODEL}): {e}")
            return None

    @classmethod
    def gerar_resposta_json(
        cls,
        prompt_atual: str,
        imagem_base64: Optional[Union[str, bytes]] = None,
        system_prompt: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Executa inferência estruturada em JSON via Groq para laudos de triagem.
        Retorna dict parseado ou None caso ocorra timeout/429/JSON inválido.
        """
        client = cls._obter_cliente()
        if client is None:
            return None

        try:
            messages = cls.formatar_mensagens(
                prompt_atual=prompt_atual,
                imagem_base64=imagem_base64,
                system_prompt=system_prompt or SYSTEM_TRIAGEM_JSON,
            )
            completion = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=messages,
                temperature=0.2,
                max_tokens=500,
                response_format={"type": "json_object"},
            )
            bruto = (completion.choices[0].message.content or "") if completion.choices else ""
            limpo = cls._limpar_raciocinio(bruto)
            if not limpo:
                return None
            # Remove eventuais cercas ```json ... ```
            limpo = re.sub(r"^```(?:json)?\s*|\s*```$", "", limpo, flags=re.IGNORECASE).strip()
            dados = json.loads(limpo)
            return dados if isinstance(dados, dict) else None
        except Exception as e:
            logger.warning(f"Falha na inferência JSON Groq ({GROQ_MODEL}): {e}")
            return None
