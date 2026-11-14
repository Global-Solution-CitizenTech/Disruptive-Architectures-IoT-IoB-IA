"""
Serviço de Tool Calling e Integração Oracle DB (Somente Leitura) — ZelaFix AI
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)
"""
import re
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Optional, Dict, Any, Tuple
from src.database.oracle_client import OracleClient
from src.schemas.chamado import ChamadoContextPayload
from src.utils.guardrails import sanitizar_lgpd

logger = logging.getLogger("ZelaFixAI.ChamadoOracleService")

_PADRAO_CHAMADO_ID = re.compile(
    r"(?:chamado|ocorr[eê]ncia|protocolo)\s*(?:d[eo]\s*)?(?:n[úu]mero|num\.?|n[ºo°]\.?|id|#)?\s*(\d+)|(?<!\S)#(\d+)\b",
    re.IGNORECASE,
)

_SLA_PADRAO_HORAS = {
    "URGENTE": 12,
    "ALTA": 24,
    "MEDIA": 48,
    "BAIXA": 72,
    "CET_SEMAFORO": 4,
}

TOOLS_ZELAFIX = [
    {
        "type": "function",
        "function": {
            "name": "consultar_chamados_oracle",
            "description": (
                "Consulta somente leitura (SELECT) de chamados urbanos reais no banco Oracle FIAP. "
                "Use quando o munícipe pedir status/detalhes de um protocolo, listar chamados recentes ou panorama de um bairro."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "id_chamado": {
                        "type": "integer",
                        "description": "ID numérico específico do chamado/protocolo, se informado.",
                    },
                    "bairro": {
                        "type": "string",
                        "description": "Nome do bairro citado (ex: Vila Mariana, Pinheiros, Sé). Omita para busca geral.",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Quantidade máxima de chamados recentes (1 a 10). Padrão: 5.",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calcular_prazo_sla",
            "description": (
                "Retorna data e hora atual em São Paulo e calcula a previsão exata de atendimento (SLA) "
                "para uma prioridade ou emergência semafórica."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "prioridade": {
                        "type": "string",
                        "enum": ["URGENTE", "ALTA", "MEDIA", "BAIXA", "CET_SEMAFORO"],
                        "description": "Nível de prioridade ou código CET_SEMAFORO para semáforo apagado.",
                    }
                },
                "required": ["prioridade"],
            },
        },
    },
]


class ChamadoOracleService:
    """
    Orquestra consultas somente leitura (`SELECT`) ao Oracle FIAP via fast-path
    por ID ou via Tool Calling nativo no Azure AI Foundry.
    """

    @staticmethod
    def _formatar_chamado_oracle(dados: Dict[str, Any]) -> str:
        return sanitizar_lgpd(
            f"[DADOS REAIS DA OCORRÊNCIA Nº {dados['id']} NO BANCO ORACLE:\n"
            f"• Título: {dados['titulo']}\n"
            f"• Categoria: {dados['categoria']}\n"
            f"• Status Oficial: {dados['status_atual']}\n"
            f"• Localização: {dados['logradouro']} - {dados['bairro']}\n"
            f"• Data de Abertura: {dados['dt_abertura']}\n"
            f"• Apoios Comunitários (+1): {dados['apoios_comunitarios']} munícipe(s)\n"
            f"• Descrição Relatada: {dados['descricao']}]"
        )

    @classmethod
    def extrair_id_chamado_da_pergunta(cls, pergunta: str) -> Optional[int]:
        """Extrai o número de chamado/protocolo mencionado na pergunta."""
        if not pergunta:
            return None
        match = _PADRAO_CHAMADO_ID.search(pergunta)
        if not match:
            return None
        bruto = match.group(1) or match.group(2)
        try:
            return int(bruto) if bruto else None
        except ValueError:
            return None

    @classmethod
    def obter_contexto_chamado_real(
        cls,
        id_chamado: Optional[int] = None,
        contexto_dto: Optional[ChamadoContextPayload] = None,
        incluir_foto: bool = False,
    ) -> Tuple[str, Optional[Dict[str, Any]]]:
        """
        Retorna (texto_formatado_contexto, dados_dict_oracle) para um chamado específico
        ou contexto estruturado enviado pelo app mobile/Java.
        """
        target_id = id_chamado or (contexto_dto.id if contexto_dto else None)
        dados_oracle: Optional[Dict[str, Any]] = None
        status_oracle = "nao_consultado"

        if target_id is not None:
            dados_oracle, status_oracle = OracleClient.consultar_chamado_com_status(
                target_id, incluir_foto=incluir_foto
            )

        if dados_oracle:
            return cls._formatar_chamado_oracle(dados_oracle), dados_oracle

        if contexto_dto and (contexto_dto.titulo or contexto_dto.categoria):
            partes = [
                f"Protocolo: {contexto_dto.protocolo or ('#' + str(contexto_dto.id) if contexto_dto.id else 'ZF-NOVO')}",
                f"Categoria: {contexto_dto.categoria}",
                f"Título: {contexto_dto.titulo}",
                f"Bairro: {contexto_dto.bairro or 'São Paulo'}",
            ]
            if contexto_dto.logradouro:
                partes.append(f"Logradouro: {contexto_dto.logradouro}")
            if contexto_dto.descricao:
                partes.append(f"Descrição: {contexto_dto.descricao}")
            if contexto_dto.apoios_comunitarios is not None:
                partes.append(f"Apoios Comunitários (+1): {contexto_dto.apoios_comunitarios}")
            return sanitizar_lgpd("[Ocorrência Ativa: " + ", ".join(partes) + "]"), None

        if target_id is not None and status_oracle == "nao_encontrado":
            return (
                f"[CONSULTA ORACLE FIAP: O chamado/protocolo nº {target_id} não foi encontrado na base oficial. "
                "Informe ao munícipe com clareza que esse número não consta nos registros.]",
                None,
            )

        return "", None

    @classmethod
    def executar_tool(cls, nome_tool: str, argumentos: Dict[str, Any]) -> str:
        """Executa tools somente leitura acionadas pelo modelo via Function Calling."""
        if nome_tool == "calcular_prazo_sla":
            prio = str(argumentos.get("prioridade", "MEDIA")).upper().strip()
            horas = _SLA_PADRAO_HORAS.get(prio, 48)
            try:
                agora = datetime.now(ZoneInfo("America/Sao_Paulo"))
            except Exception:
                agora = datetime.utcnow() - timedelta(hours=3)
            limite = agora + timedelta(hours=horas)
            return (
                f"Data/hora atual em São Paulo: {agora.strftime('%d/%m/%Y %H:%M')}. "
                f"SLA normativo para {prio}: {horas}h (previsão limite até {limite.strftime('%d/%m/%Y %H:%M')})."
            )

        if nome_tool != "consultar_chamados_oracle":
            return "Ferramenta não suportada."

        id_chamado = argumentos.get("id_chamado")
        if isinstance(id_chamado, (int, str)) and str(id_chamado).strip().isdigit():
            dados, status = OracleClient.consultar_chamado_com_status(int(id_chamado), incluir_foto=False)
            if dados:
                return cls._formatar_chamado_oracle(dados)
            if status == "nao_encontrado":
                return f"Nenhum chamado encontrado com o número {id_chamado}."
            return "Banco Oracle indisponível no momento."

        bairro_raw = argumentos.get("bairro")
        bairro = str(bairro_raw).strip() if isinstance(bairro_raw, str) and bairro_raw.strip() else None
        limit_raw = argumentos.get("limit")
        limit = int(limit_raw) if isinstance(limit_raw, (int, float)) else 5
        limit = max(1, min(limit, 10))

        recentes = OracleClient.listar_chamados_recentes(limit=limit, bairro=bairro)
        resumo = OracleClient.resumo_estatistico_bairro(bairro=bairro)
        if not recentes and not (resumo.get("oracle_online") and resumo.get("total_chamados", 0) > 0):
            escopo = f"no bairro '{bairro}'" if bairro else "cadastrados"
            return f"Nenhum chamado localizado {escopo} no Oracle FIAP (ou banco indisponível)."

        linhas = [
            f"• Chamado #{c['id']} ({c['status']}): {c['titulo']} — {c['categoria']} ({c['bairro']}, {c['votos']} apoios)"
            for c in recentes
        ]
        escopo = f"no bairro {bairro}" if bairro else "na cidade"
        total_txt = f"Total ativo {escopo}: {resumo.get('total_chamados', len(recentes))} | Apoios (+1): {resumo.get('total_votos', 0)}\n"
        return sanitizar_lgpd(total_txt + f"Chamados recentes ({escopo}):\n" + "\n".join(linhas))
