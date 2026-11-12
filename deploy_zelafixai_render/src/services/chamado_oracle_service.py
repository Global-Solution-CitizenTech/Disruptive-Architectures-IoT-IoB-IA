"""
Serviço de Integração e Enriquecimento Contextual de Chamados (Oracle DB) — ZelaFix AI
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)
"""
import re
import logging
from typing import Optional, Dict, Any, Tuple
from src.database.oracle_client import OracleClient
from src.schemas.chamado import ChamadoContextPayload

logger = logging.getLogger("ZelaFixAI.ChamadoOracleService")

_PADRAO_CHAMADO_ID = re.compile(
    r"(?:chamado|ocorr[eê]ncia|protocolo)\s*(?:n[ºo°]?|#)?\s*(\d+)",
    re.IGNORECASE
)


class ChamadoOracleService:
    """
    Identifica intenções de consulta a chamados específicos e enriquece
    o contexto do ZelaBot com os dados reais persistidos no Oracle da FIAP.
    """

    @classmethod
    def extrair_id_chamado_da_pergunta(cls, pergunta: str) -> Optional[int]:
        """Extrai o número de chamado mencionado na pergunta do cidadão."""
        if not pergunta:
            return None
        match = _PADRAO_CHAMADO_ID.search(pergunta)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                return None
        return None

    @classmethod
    def obter_contexto_chamado_real(
        cls,
        id_chamado: Optional[int] = None,
        contexto_dto: Optional[ChamadoContextPayload] = None
    ) -> Tuple[str, Optional[Dict[str, Any]]]:
        """
        Retorna (texto_formatado_contexto, dados_dict_oracle).
        Prioriza o ID informado ou extrai do DTO.
        """
        target_id = id_chamado or (contexto_dto.id if contexto_dto else None)
        dados_oracle: Optional[Dict[str, Any]] = None

        if target_id is not None:
            dados_oracle = OracleClient.obter_chamado_completo(target_id)

        if dados_oracle:
            texto_contexto = (
                f"[DADOS REAIS DA OCORRÊNCIA Nº {dados_oracle['id']} REGISTRADOS NO BANCO ORACLE:\n"
                f"• Título: {dados_oracle['titulo']}\n"
                f"• Categoria: {dados_oracle['categoria']}\n"
                f"• Status Oficial: {dados_oracle['status_atual']}\n"
                f"• Localização: {dados_oracle['logradouro']} - {dados_oracle['bairro']}\n"
                f"• Data de Abertura: {dados_oracle['dt_abertura']}\n"
                f"• Apoios Comunitários (+1): {dados_oracle['apoios_comunitarios']} munícipe(s)\n"
                f"• Descrição Relatada: {dados_oracle['descricao']}]"
            )
            return texto_contexto, dados_oracle

        # Se não encontrou no Oracle mas veio contexto estruturado no DTO
        if contexto_dto and (contexto_dto.titulo or contexto_dto.categoria):
            partes = [
                f"Protocolo: {contexto_dto.protocolo or ('#' + str(contexto_dto.id) if contexto_dto.id else 'ZF-NOVO')}",
                f"Categoria: {contexto_dto.categoria}",
                f"Título: {contexto_dto.titulo}",
                f"Bairro: {contexto_dto.bairro or 'São Paulo'}"
            ]
            if contexto_dto.logradouro:
                partes.append(f"Logradouro: {contexto_dto.logradouro}")
            if contexto_dto.descricao:
                partes.append(f"Descrição: {contexto_dto.descricao}")
            if contexto_dto.apoios_comunitarios is not None:
                partes.append(f"Apoios Comunitários (+1): {contexto_dto.apoios_comunitarios}")

            texto_contexto = "[Ocorrência Ativa: " + ", ".join(partes) + "]"
            return texto_contexto, None

        return "", None
