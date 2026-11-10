"""
Serviço de Inferência: Cliente Google Gemini (SDK oficial google-genai) — ZelaFix AI
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)
"""
import logging
from typing import Optional, List
from google import genai
from google.genai import types
from src.core.config import GEMINI_MODEL, GEMINI_API_KEY
from src.core.prompts import SYSTEM_INSTRUCTION
from src.schemas.chat import MensagemHistorico

logger = logging.getLogger("ZelaFixAI.GeminiService")

class GeminiService:
    """
    Comunicação com o Google Gemini usando o modelo fixo definido em `GEMINI_MODEL`.
    Aplica janela deslizante ao histórico para evitar contaminação contextual.
    """

    MAX_HISTORICO_TURNOS = 6
    _client: Optional[genai.Client] = None

    @classmethod
    def _obter_cliente(cls) -> Optional[genai.Client]:
        """Obtém ou instancia o cliente Gemini reutilizável (singleton)."""
        if not GEMINI_API_KEY:
            return None
        if cls._client is None:
            cls._client = genai.Client(api_key=GEMINI_API_KEY)
        return cls._client

    @classmethod
    def gerar_resposta(
        cls,
        prompt_atual: str,
        historico: Optional[List[MensagemHistorico]] = None
    ) -> Optional[str]:
        """Retorna o texto gerado ou None se não houver chave ou a chamada falhar."""
        client = cls._obter_cliente()
        if client is None:
            return None

        contents = []
        for msg in (historico or [])[-cls.MAX_HISTORICO_TURNOS:]:
            if not msg.text or not msg.text.strip():
                continue
            role = "user" if msg.sender.lower() in ["user", "municipe", "cidadao", "cliente"] else "model"
            contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg.text.strip())]))
        contents.append(types.Content(role="user", parts=[types.Part.from_text(text=prompt_atual.strip())]))

        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.6,
                    max_output_tokens=800
                )
            )
            if response and response.text:
                return response.text
        except Exception as e:
            logger.warning(f"[Gemini] Falha na chamada ({GEMINI_MODEL}): {e}")
        return None
