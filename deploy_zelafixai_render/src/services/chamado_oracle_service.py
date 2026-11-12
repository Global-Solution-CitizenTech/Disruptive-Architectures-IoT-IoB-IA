"""
Serviço de Integração e Enriquecimento Contextual de Chamados (Oracle DB) — ZelaFix AI
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)
"""
import re
import logging
from typing import Optional, Dict, Any, Tuple
from src.database.oracle_client import OracleClient
from src.schemas.chamado import ChamadoContextPayload
from src.services.viacep_client import ViaCepClient
from src.utils.text import normalizar_texto

logger = logging.getLogger("ZelaFixAI.ChamadoOracleService")

_PADRAO_CHAMADO_ID = re.compile(
    r"(?:chamado|ocorr[eê]ncia|protocolo)\s*(?:d[eo]\s*)?(?:n[úu]mero|num\.?|n[ºo°]\.?|id|#)?\s*(\d+)|(?<!\S)#(\d+)\b",
    re.IGNORECASE
)
_PADRAO_CEP = re.compile(r"\b(\d{5}-?\d{3})\b")
_PADRAO_LISTAGEM = re.compile(
    r"\b(?:quais|liste|listar|mostr[ae]|mostrar|ver|existe[m]?|tem|ultim[oa]s?|recentes?|abert[oa]s?)\b.*\b(?:chamados?|ocorrencias?|problemas?|buracos?|queixas?)\b"
    r"|\b(?:chamados?|ocorrencias?)\b.*\b(?:abert[oa]s?|recentes?|bairro|regiao|cep|\d{5}-?\d{3}|(?:em|no|na|do|da)\s+[a-z])",
    re.IGNORECASE
)
_STOPWORDS_LOCAL = {
    "aberto", "abertos", "aberta", "abertas", "recente", "recentes",
    "sistema", "oracle", "zelafix", "app", "aplicativo", "sao paulo", "sp",
    "cidade", "geral", "rua", "avenida", "cep", "chamado", "chamados",
    "ocorrencia", "ocorrencias", "problema", "problemas", "buraco", "buracos",
    "hoje", "agora", "plataforma", "banco", "dados"
}


class ChamadoOracleService:
    """
    Identifica consultas a chamados ou listagens urbanas e enriquece o contexto
    do ZelaBot usando exclusivamente leitura (SELECT) no Oracle FIAP + ViaCEP.
    """

    @classmethod
    def extrair_id_chamado_da_pergunta(cls, pergunta: str) -> Optional[int]:
        """Extrai o número de chamado mencionado na pergunta do cidadão."""
        if not pergunta:
            return None
        match = _PADRAO_CHAMADO_ID.search(pergunta)
        if match:
            bruto = match.group(1) or match.group(2)
            try:
                return int(bruto) if bruto else None
            except ValueError:
                return None
        return None

    @classmethod
    def extrair_bairro_listagem(cls, pergunta: str) -> Optional[str]:
        """
        Detecta se a pergunta solicita listagem de chamados e resolve eventual
        bairro citado via CEP (ViaCEP), catálogo dinâmico do Oracle ou regex flexível.
        """
        if not pergunta:
            return None
        norm = normalizar_texto(pergunta)
        if not _PADRAO_LISTAGEM.search(norm):
            return None

        # 1. CEP explícito na pergunta -> resolve bairro real via ViaCEP (como no Java)
        m_cep = _PADRAO_CEP.search(pergunta)
        if m_cep:
            dados_cep = ViaCepClient.consultar_cep(m_cep.group(1))
            if dados_cep and dados_cep.get("bairro"):
                return dados_cep["bairro"]

        # 2. Catálogo dinâmico cacheado da tabela BAIRRO do Oracle (sem lista fixa)
        bairros_oracle = sorted(
            OracleClient.listar_bairros_cadastrados(),
            key=lambda b: len(b),
            reverse=True,
        )
        for bairro_real in bairros_oracle:
            bairro_norm = normalizar_texto(bairro_real)
            if bairro_norm and re.search(rf"\b{re.escape(bairro_norm)}\b", norm):
                return bairro_real

        # 3. Extração flexível (aceita minúsculas, sem acento e preposições como 'Freguesia do Ó')
        for m_bairro in re.finditer(
            r"\b(?:bairro|em|no|na|do|da|dos|das)\s+([A-Za-zÀ-Úà-ú0-9]+(?:\s+(?:d[eao]s?\s+)?[A-Za-zÀ-Úà-ú0-9]+){0,3})",
            pergunta,
            re.IGNORECASE,
        ):
            candidato = re.sub(r"\b(?:hoje|agora|por favor|sao paulo|sp)\b.*$", "", m_bairro.group(1), flags=re.IGNORECASE).strip(" ,.?!;:")
            cand_norm = normalizar_texto(candidato)
            if cand_norm and cand_norm not in _STOPWORDS_LOCAL and not cand_norm.isdigit():
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
