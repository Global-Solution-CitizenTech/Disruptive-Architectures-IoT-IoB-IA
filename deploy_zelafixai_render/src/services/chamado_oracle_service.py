"""
Serviço de Integração e Enriquecimento Contextual de Chamados (Oracle DB) — ZelaFix AI
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)
"""
import re
import logging
from typing import Optional, Dict, Any, Tuple
from src.database.oracle_client import OracleClient
from src.schemas.chamado import ChamadoContextPayload
from src.utils.text import normalizar_texto

logger = logging.getLogger("ZelaFixAI.ChamadoOracleService")

_PADRAO_CHAMADO_ID = re.compile(
    r"(?:chamado|ocorr[eê]ncia|protocolo)\s*(?:n[ºo°]?|#)?\s*(\d+)",
    re.IGNORECASE
)
_PADRAO_LISTAGEM = re.compile(
    r"\b(?:quais|liste|listar|mostr[ae]|ver|existe[m]?|tem|ultim[oa]s?|recentes?|abert[oa]s?)\b.*\b(?:chamados?|ocorrencias?)\b"
    r"|\b(?:chamados?|ocorrencias?)\b.*\b(?:abert[oa]s?|recentes?|bairro|regiao)\b",
    re.IGNORECASE
)
_BAIRROS_CONHECIDOS = ["bela vista", "pinheiros", "se", "sé", "mooca", "santana"]


class ChamadoOracleService:
    """
    Identifica consultas a chamados ou listagens urbanas e enriquece o contexto
    do ZelaBot usando exclusivamente leitura (SELECT) no Oracle FIAP.
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
    def extrair_bairro_listagem(cls, pergunta: str) -> Optional[str]:
        """Detecta se a pergunta solicita listagem de chamados e eventual bairro citado."""
        if not pergunta:
            return None
        norm = normalizar_texto(pergunta)
        if not _PADRAO_LISTAGEM.search(norm):
            return None
        for b in _BAIRROS_CONHECIDOS:
            if re.search(rf"\b{re.escape(normalizar_texto(b))}\b", norm):
                return b if b != "se" else "Sé"
        # Padrão genérico "em/no/na <Bairro>" com inicial maiúscula na pergunta original
        m_bairro = re.search(r"\b(?:em|no|na)\s+([A-ZÀ-Ú][a-zà-ú]+(?:\s+[A-ZÀ-Ú][a-zà-ú]+)?)", pergunta)
        if m_bairro:
            candidato = m_bairro.group(1).strip()
            if candidato.lower() not in {"sao paulo", "sp", "aberto", "abertos", "oracle", "sistema"}:
                return candidato
        return "__TODOS__"

    @classmethod
    def obter_contexto_chamado_real(
        cls,
        id_chamado: Optional[int] = None,
        contexto_dto: Optional[ChamadoContextPayload] = None,
        incluir_foto: bool = False,
        pergunta: str = ""
    ) -> Tuple[str, Optional[Dict[str, Any]]]:
        """
        Retorna (texto_formatado_contexto, dados_dict_oracle).
        Suporta consulta por ID específico, aviso explícito se ID não existir no Oracle,
        e listagem limitada dos chamados recentes por bairro/cidade.
        """
        target_id = id_chamado or (contexto_dto.id if contexto_dto else None)
        dados_oracle: Optional[Dict[str, Any]] = None
        status_oracle = "nao_consultado"

        if target_id is not None:
            dados_oracle, status_oracle = OracleClient.consultar_chamado_com_status(
                target_id, incluir_foto=incluir_foto
            )

        if dados_oracle:
            texto_contexto = (
                f"[DADOS REAIS DA OCORRÊNCIA Nº {dados_oracle['id']} NO BANCO ORACLE:\n"
                f"• Título: {dados_oracle['titulo']}\n"
                f"• Categoria: {dados_oracle['categoria']}\n"
                f"• Status Oficial: {dados_oracle['status_atual']}\n"
                f"• Localização: {dados_oracle['logradouro']} - {dados_oracle['bairro']}\n"
                f"• Data de Abertura: {dados_oracle['dt_abertura']}\n"
                f"• Apoios Comunitários (+1): {dados_oracle['apoios_comunitarios']} munícipe(s)\n"
                f"• Descrição Relatada: {dados_oracle['descricao']}]"
            )
            return texto_contexto, dados_oracle

        # Se veio contexto estruturado no DTO do app/integrador
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

            return "[Ocorrência Ativa: " + ", ".join(partes) + "]", None

        # Protocolo solicitado explicitamente não localizado no Oracle online
        if target_id is not None and status_oracle == "nao_encontrado":
            return (
                f"[CONSULTA ORACLE FIAP: O chamado/protocolo nº {target_id} não foi encontrado na base de dados oficial. "
                "Informe ao munícipe com clareza que esse número não consta nos registros e peça para conferir o protocolo.]",
                None,
            )

        # Pergunta de listagem de chamados recentes/abertos por bairro ou geral
        filtro_bairro = cls.extrair_bairro_listagem(pergunta)
        if filtro_bairro is not None:
            bairro_param = None if filtro_bairro == "__TODOS__" else filtro_bairro
            recentes = OracleClient.listar_chamados_recentes(limit=5, bairro=bairro_param)
            if recentes:
                linhas = [
                    f"• Chamado #{c['id']} ({c['status']}): {c['titulo']} — {c['categoria']} ({c['bairro']}, {c['votos']} apoios)"
                    for c in recentes
                ]
                escopo = f"no bairro {bairro_param}" if bairro_param else "na cidade"
                return (
                    f"[CHAMADOS RECENTES NO BANCO ORACLE ({escopo}):\n" + "\n".join(linhas) + "]",
                    None,
                )
            if bairro_param:
                return (
                    f"[CONSULTA ORACLE FIAP: Nenhum chamado localizado para o filtro de bairro '{bairro_param}'. "
                    "Informe isso com transparência e ofereça abrir um novo chamado pelo app ZelaFix.]",
                    None,
                )

        return "", None
