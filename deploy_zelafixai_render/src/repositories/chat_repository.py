"""
Repositório de Persistência do Chat e Auditoria de Triagens — ZelaFix AI
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)
"""
import logging
from typing import Optional, List, Dict, Any
from src.database.connection import get_db_connection

logger = logging.getLogger("ZelaFixAI.ChatRepository")

class ChatRepository:
    """
    Encapsula todas as operações de banco de dados para mensagens de chat
    e auditoria de triagens técnicas de zeladoria urbana no SQLite.
    """

    @staticmethod
    def salvar_mensagem(
        session_id: str,
        sender: str,
        text: str,
        chamado_id: Optional[int] = None
    ) -> bool:
        """
        Salva uma única mensagem (user ou model) no histórico do SQLite.
        """
        try:
            with get_db_connection() as conn:
                conn.execute(
                    "INSERT INTO mensagens_chat (session_id, chamado_id, sender, text) VALUES (?, ?, ?, ?)",
                    (session_id, chamado_id, sender, text)
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Erro ao salvar mensagem no SQLite: {e}")
            return False

    @staticmethod
    def salvar_interacao(
        session_id: str,
        pergunta: str,
        resposta: str,
        categoria: str,
        urgencia: str,
        origem_resposta: str,
        chamado_id: Optional[int] = None,
        bairro: Optional[str] = None,
        orgao_responsavel: Optional[str] = None,
        sla_horas: Optional[int] = None
    ) -> bool:
        """
        Grava, em uma única transação, as mensagens do turno e o parecer de auditoria da triagem.
        """
        try:
            with get_db_connection() as conn:
                conn.executemany(
                    "INSERT INTO mensagens_chat (session_id, chamado_id, sender, text) VALUES (?, ?, ?, ?)",
                    [
                        (session_id, chamado_id, "user", pergunta),
                        (session_id, chamado_id, "model", resposta),
                    ]
                )
                conn.execute(
                    """
                    INSERT INTO auditoria_triagens (
                        session_id, chamado_id, bairro, pergunta, resposta,
                        categoria, urgencia, orgao_responsavel, sla_horas, origem_resposta
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (session_id, chamado_id, bairro, pergunta, resposta, categoria, urgencia, orgao_responsavel, sla_horas, origem_resposta)
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Erro ao salvar interação no SQLite: {e}")
            return False

    @staticmethod
    def salvar_triagem_audit(
        session_id: str,
        chamado_id: Optional[int],
        bairro: Optional[str],
        titulo: str,
        parecer_ia: str,
        categoria: str,
        prioridade: str,
        orgao_responsavel: str,
        sla_horas: int,
        origem_triagem: str
    ) -> bool:
        """
        Persiste especificamente um registro de laudo técnico de triagem urbana.
        """
        try:
            with get_db_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO auditoria_triagens (
                        session_id, chamado_id, bairro, pergunta, resposta,
                        categoria, urgencia, orgao_responsavel, sla_horas, origem_resposta
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (session_id, chamado_id, bairro, titulo, parecer_ia, categoria, prioridade, orgao_responsavel, sla_horas, origem_triagem)
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Erro ao salvar laudo de triagem no SQLite: {e}")
            return False

    @staticmethod
    def buscar_historico(
        session_id: Optional[str] = None,
        chamado_id: Optional[int] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Recupera as mensagens filtradas por session_id ou chamado_id em ordem cronológica.
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                filtros = []
                parametros: List[Any] = []

                if session_id:
                    filtros.append("session_id = ?")
                    parametros.append(session_id)
                if chamado_id:
                    filtros.append("chamado_id = ?")
                    parametros.append(chamado_id)

                where_sql = f"WHERE {' AND '.join(filtros)}" if filtros else ""
                ordem_sql = "ORDER BY id ASC" if filtros else "ORDER BY id DESC"
                parametros.append(limit)

                cursor.execute(f"""
                    SELECT id, session_id, chamado_id, sender, text, timestamp
                    FROM mensagens_chat
                    {where_sql}
                    {ordem_sql}
                    LIMIT ?
                """, tuple(parametros))

                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Erro ao buscar histórico no SQLite: {e}")
            return []

    @staticmethod
    def listar_auditorias(
        chamado_id: Optional[int] = None,
        bairro: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Recupera os registros de auditoria e laudos técnicos de zeladoria mais recentes.
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                filtros = []
                parametros: List[Any] = []

                if chamado_id:
                    filtros.append("chamado_id = ?")
                    parametros.append(chamado_id)
                if bairro:
                    filtros.append("bairro = ?")
                    parametros.append(bairro)

                where_sql = f"WHERE {' AND '.join(filtros)}" if filtros else ""
                parametros.append(limit)

                cursor.execute(f"""
                    SELECT id, session_id, chamado_id, bairro, pergunta, resposta,
                           categoria, urgencia, orgao_responsavel, sla_horas, origem_resposta, timestamp
                    FROM auditoria_triagens
                    {where_sql}
                    ORDER BY id DESC
                    LIMIT ?
                """, tuple(parametros))

                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Erro ao listar auditorias no SQLite: {e}")
            return []

    @staticmethod
    def listar_sessoes(
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Recupera as sessões de conversa do munícipe agrupadas, com título baseado na primeira
        pergunta do cidadão, quantidade de mensagens e data da última interação.
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT
                        m.session_id,
                        COUNT(*) AS total_mensagens,
                        MAX(m.timestamp) AS last_activity,
                        COALESCE(
                            (SELECT text FROM mensagens_chat WHERE session_id = m.session_id AND sender = 'user' ORDER BY id ASC LIMIT 1),
                            m.text
                        ) AS titulo
                    FROM mensagens_chat m
                    GROUP BY m.session_id
                    ORDER BY MAX(m.id) DESC
                    LIMIT ?
                """, (limit,))

                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Erro ao listar sessões de chat no SQLite: {e}")
            return []

    @staticmethod
    def excluir_sessao(session_id: str) -> bool:
        """
        Exclui todas as mensagens e registros de auditoria vinculados a uma sessão.
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM mensagens_chat WHERE session_id = ?", (session_id,))
                cursor.execute("DELETE FROM auditoria_triagens WHERE session_id = ?", (session_id,))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Erro ao excluir sessão {session_id} no SQLite: {e}")
            return False
