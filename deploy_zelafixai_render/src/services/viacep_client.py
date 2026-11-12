"""
Cliente HTTP Resiliente para ViaCEP — ZelaFix AI
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)

Espelha o padrão do módulo Java (`ViaCepService.java` / `EnderecoService.java`)
para resolver CEP -> bairro/logradouro sem bloquear ou derrubar o fluxo em offline.
"""
import re
import logging
from functools import lru_cache
from typing import Optional, Dict
import httpx

logger = logging.getLogger("ZelaFixAI.ViaCepClient")

_VIACEP_URL = "https://viacep.com.br/ws/{cep}/json"
_VIACEP_TIMEOUT_SECONDS = 2.5


@lru_cache(maxsize=256)
def _consultar_cep_cacheado(cep_digitos: str) -> Optional[Dict[str, str]]:
    """Consulta o ViaCEP em cache LRU para CEPs de 8 dígitos válidos."""
    try:
        resp = httpx.get(
            _VIACEP_URL.format(cep=cep_digitos),
            headers={"Accept": "application/json"},
            timeout=_VIACEP_TIMEOUT_SECONDS,
        )
        if resp.status_code != 200:
            return None
        dados = resp.json()
        if not isinstance(dados, dict) or dados.get("erro"):
            return None
        bairro = (dados.get("bairro") or "").strip()
        logradouro = (dados.get("logradouro") or "").strip()
        localidade = (dados.get("localidade") or "").strip()
        uf = (dados.get("uf") or "").strip()
        if not (bairro or logradouro or localidade):
            return None
        return {
            "cep": cep_digitos,
            "logradouro": logradouro,
            "bairro": bairro,
            "localidade": localidade,
            "uf": uf,
        }
    except Exception as e:
        logger.debug(f"Falha ao consultar ViaCEP para CEP {cep_digitos}: {e}")
        return None


class ViaCepClient:
    """Resolve CEP brasileiro (8 dígitos) para bairro e logradouro via ViaCEP."""

    @staticmethod
    def normalizar_cep(cep: Optional[str]) -> Optional[str]:
        """Extrai os 8 dígitos numéricos do CEP ou retorna None se inválido."""
        if not cep:
            return None
        digitos = re.sub(r"\D", "", str(cep))
        return digitos if len(digitos) == 8 else None

    @classmethod
    def consultar_cep(cls, cep: Optional[str]) -> Optional[Dict[str, str]]:
        """Retorna dados do endereço (com cópia defensiva) ou None se indisponível."""
        digitos = cls.normalizar_cep(cep)
        if not digitos:
            return None
        resultado = _consultar_cep_cacheado(digitos)
        return dict(resultado) if resultado else None
