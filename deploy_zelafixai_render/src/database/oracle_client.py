"""
Cliente de Conexão com o Banco de Dados Oracle FIAP (Modo Thin) — ZelaFix AI
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)

Permite que o ZelaFix AI consulte chamados reais, status atual e engajamento comunitário (IoB)
diretamente na base de dados oficial da solução CitizenTech.
"""
import os
import re
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger("ZelaFixAI.OracleClient")

# Tentativa de importação defensiva do oracledb
try:
    import oracledb
    # Garante operação em modo Thin (100% Python, compatível com Render sem Instant Client)
    HAS_ORACLE = True
except ImportError:
    HAS_ORACLE = False
    logger.warning("Biblioteca 'oracledb' não instalada. OracleClient operará em modo degradado.")


class OracleClient:
    """
    Gerenciador de acesso ao banco de dados relacional Oracle da FIAP.
    Executa queries parametrizadas com tratamento rigoroso de exceções e timeout.
    """

    @classmethod
    def _obter_config(cls) -> Dict[str, Any]:
        """Extrai os parâmetros de conexão a partir do ambiente ou padrões FIAP."""
        user = os.environ.get("ORACLE_USER", "rm566422").strip()
        password = os.environ.get("ORACLE_PASSWORD", "201006").strip()
        url = os.environ.get("ORACLE_URL", "").strip()

        # DSN padrão para o cluster de banco de dados da FIAP
        dsn = "oracle.fiap.com.br:1521/orcl"
        if url and "@//" in url:
            # Extrai host:port/service de jdbc:oracle:thin:@//oracle.fiap.com.br:1521/orcl
            partes = url.split("@//")
            if len(partes) > 1:
                dsn = partes[1].strip()
        elif os.environ.get("ORACLE_DSN"):
            dsn = os.environ.get("ORACLE_DSN").strip()

        return {
            "user": user,
            "password": password,
            "dsn": dsn
        }

    @classmethod
    def _conectar(cls):
        """Estabelece conexão com o Oracle com timeout seguro."""
        if not HAS_ORACLE:
            return None
        cfg = cls._obter_config()
        if not cfg["user"] or not cfg["password"]:
            return None
        try:
            return oracledb.connect(
                user=cfg["user"],
                password=cfg["password"],
                dsn=cfg["dsn"],
                tcp_connect_timeout=3.0,
                expire_time=5
            )
        except Exception as e:
            logger.warning(f"Falha ao conectar no Oracle ({cfg['dsn']}): {e}")
            return None

    @classmethod
    def verificar_conexao(cls) -> Dict[str, Any]:
        """Testa a conectividade com o Oracle e retorna telemetria."""
        if not HAS_ORACLE:
            return {"status": "indisponivel", "motivo": "modulo oracledb nao instalado"}

        conn = cls._conectar()
        if not conn:
            return {"status": "offline", "motivo": "nao foi possivel conectar ao servidor Oracle FIAP"}

        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT table_name FROM user_tables ORDER BY table_name")
                tabelas = [row[0] for row in cursor.fetchall()]
                return {
                    "status": "online",
                    "servidor": "oracle.fiap.com.br:1521/orcl",
                    "usuario": cls._obter_config()["user"],
                    "tabelas_encontradas": tabelas,
                    "modo": "thin (100% python nativo)"
                }
        except Exception as e:
            return {"status": "erro", "motivo": str(e)}
        finally:
            try:
                conn.close()
            except Exception:
                pass

    @classmethod
    def obter_chamado_completo(cls, id_chamado: int) -> Optional[Dict[str, Any]]:
        """
        Consulta os dados detalhados de uma ocorrência no Oracle:
        - Título, descrição, categoria, logradouro, número, bairro, CEP
        - Status oficial mais recente no histórico (HIST_CHAMADO)
        - Quantidade real de votos comunitários (+1 IoB)
        - Foto BLOB (se disponível e válida)
        """
        conn = cls._conectar()
        if not conn:
            return None

        query = """
            SELECT 
                c.id_chamado,
                c.titulo,
                c.descricao,
                cat.nm_categoria,
                e.rua,
                e.numero,
                e.cep,
                b.nm_bairro,
                c.dt_abertura,
                (
                    SELECT s.nm_status 
                    FROM hist_chamado h 
                    JOIN status s ON h.status_id_status = s.id_status 
                    WHERE h.chamado_id_chamado = c.id_chamado 
                    ORDER BY h.dt_mudanca DESC, h.id_hist DESC 
                    FETCH FIRST 1 ROWS ONLY
                ) AS status_atual,
                (
                    SELECT COUNT(1) 
                    FROM voto_chamado v 
                    WHERE v.chamado_id_chamado = c.id_chamado
                ) AS votos_comunitarios,
                DBMS_LOB.GETLENGTH(c.foto) AS tamanho_foto
            FROM chamado c
            LEFT JOIN categoria cat ON c.categoria_id_categoria = cat.id_categoria
            LEFT JOIN endereco e ON c.endereco_id_endereco = e.id_endereco
            LEFT JOIN bairro b ON e.bairro_id_bairro = b.id_bairro
            WHERE c.id_chamado = :id_chamado
        """

        try:
            with conn.cursor() as cursor:
                cursor.execute(query, id_chamado=id_chamado)
                row = cursor.fetchone()
                if not row:
                    return None

                tam_foto = row[11] or 0
                tem_foto_valida = tam_foto > 32

                dt_str = row[8].strftime("%d/%m/%Y %H:%M") if row[8] else "Não informada"

                resultado = {
                    "id": row[0],
                    "titulo": row[1] or "Ocorrência de Zeladoria",
                    "descricao": row[2] or "",
                    "categoria": row[3] or "Geral",
                    "logradouro": f"{row[4] or ''}, {row[5] or 'S/N'}".strip(", "),
                    "cep": row[6] or "",
                    "bairro": row[7] or "São Paulo - SP",
                    "dt_abertura": dt_str,
                    "status_atual": row[9] or "ABERTO",
                    "apoios_comunitarios": row[10] or 0,
                    "tem_foto": tem_foto_valida,
                    "tamanho_foto_bytes": tam_foto
                }

                # Se houver foto válida com tamanho substancial, recupera bytes
                if tem_foto_valida:
                    try:
                        cursor.execute("SELECT foto FROM chamado WHERE id_chamado = :id_chamado", id_chamado=id_chamado)
                        blob_row = cursor.fetchone()
                        if blob_row and blob_row[0]:
                            resultado["foto_bytes"] = blob_row[0].read()
                    except Exception as err_blob:
                        logger.warning(f"Erro ao ler BLOB de foto do chamado {id_chamado}: {err_blob}")

                return resultado
        except Exception as e:
            logger.warning(f"Erro ao consultar chamado {id_chamado} no Oracle: {e}")
            return None
        finally:
            try:
                conn.close()
            except Exception:
                pass

    @classmethod
    def listar_chamados_recentes(cls, limit: int = 10, bairro: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lista os chamados mais recentes cadastrados no Oracle para diagnósticos urbanos."""
        conn = cls._conectar()
        if not conn:
            return []

        query = """
            SELECT 
                c.id_chamado,
                c.titulo,
                cat.nm_categoria,
                b.nm_bairro,
                c.dt_abertura,
                (
                    SELECT s.nm_status 
                    FROM hist_chamado h 
                    JOIN status s ON h.status_id_status = s.id_status 
                    WHERE h.chamado_id_chamado = c.id_chamado 
                    ORDER BY h.dt_mudanca DESC, h.id_hist DESC 
                    FETCH FIRST 1 ROWS ONLY
                ) AS status_atual,
                (SELECT COUNT(1) FROM voto_chamado v WHERE v.chamado_id_chamado = c.id_chamado) AS votos
            FROM chamado c
            LEFT JOIN categoria cat ON c.categoria_id_categoria = cat.id_categoria
            LEFT JOIN endereco e ON c.endereco_id_endereco = e.id_endereco
            LEFT JOIN bairro b ON e.bairro_id_bairro = b.id_bairro
            WHERE (:bairro IS NULL OR LOWER(b.nm_bairro) LIKE LOWER(:bairro_like))
            ORDER BY c.id_chamado DESC
            FETCH FIRST :limit ROWS ONLY
        """

        chamados = []
        try:
            with conn.cursor() as cursor:
                bairro_like = f"%{bairro}%" if bairro else "%"
                cursor.execute(query, bairro=bairro, bairro_like=bairro_like, limit=limit)
                for row in cursor.fetchall():
                    dt_str = row[4].strftime("%d/%m/%Y") if row[4] else ""
                    chamados.append({
                        "id": row[0],
                        "titulo": row[1],
                        "categoria": row[2] or "Geral",
                        "bairro": row[3] or "São Paulo",
                        "dt_abertura": dt_str,
                        "status": row[5] or "ABERTO",
                        "votos": row[6] or 0
                    })
        except Exception as e:
            logger.warning(f"Erro ao listar chamados no Oracle: {e}")
        finally:
            try:
                conn.close()
            except Exception:
                pass

        return chamados
