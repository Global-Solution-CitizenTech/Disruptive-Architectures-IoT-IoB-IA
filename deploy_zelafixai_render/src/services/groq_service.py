"""
Serviço de Inferência: Cliente Groq Cloud (SDK oficial) — ZelaFix AI
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)
"""
import logging
from typing import Optional, List, Dict
from groq import Groq
from src.core.config import GROQ_MODEL, GROQ_API_KEY
from src.core.prompts import SYSTEM_INSTRUCTION
from src.schemas.chat import MensagemHistorico

logger = logging.getLogger("ZelaFixAI.GroqService")

class GroqService:
    """
    Comunicação com a API do Groq (LPU) usando o modelo fixo definido em `GROQ_MODEL`.
    Aplica janela deslizante ao histórico para evitar contaminação contextual.
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
    def formatar_mensagens(
        cls,
        prompt_atual: str,
        historico: Optional[List[MensagemHistorico]] = None
    ) -> List[Dict[str, str]]:
        """Formata histórico e instrução de sistema no padrão OpenAI/Groq Chat Completions."""
        messages: List[Dict[str, str]] = [
            {"role": "system", "content": SYSTEM_INSTRUCTION}
        ]

        for msg in (historico or [])[-cls.MAX_HISTORICO_TURNOS:]:
            if not msg.text or not msg.text.strip():
                continue
            role = "user" if msg.sender.lower() in ["user", "municipe", "cidadao", "cliente"] else "assistant"
            messages.append({"role": role, "content": msg.text.strip()})

        messages.append({"role": "user", "content": prompt_atual.strip()})
        return messages

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

        try:
            completion = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=cls.formatar_mensagens(prompt_atual, historico),
                temperature=0.6,
                max_tokens=800
            )
            if completion.choices and completion.choices[0].message.content:
                return completion.choices[0].message.content.strip()
        except Exception as e:
            logger.warning(f"[Groq] Falha na chamada ({GROQ_MODEL}): {e}")
        return None
