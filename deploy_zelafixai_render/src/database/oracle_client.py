"""
Cliente de Conexão com o Banco de Dados Oracle FIAP (Modo Thin — Somente Leitura) — ZelaFix AI
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)

Executa exclusivamente consultas SELECT parametrizadas com limites e timeouts defensivos.
"""
import os
import logging
from typing import Optional, Dict, Any, List, Tuple
from src.core.config import ORACLE_USER, ORACLE_PASSWORD, ORACLE_URL, ORACLE_DSN
from src.utils.text import normalizar_texto

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
    Gerenciador SOMENTE LEITURA de acesso ao banco relacional Oracle da FIAP.
    Todas as operações utilizam exclusivamente SELECT com bind variables e timeouts.
    """

    _SQL_BAIRRO_NORM = (
        "TRANSLATE(LOWER(b.nm_bairro), "
        "'áàâãäéèêëíìîïóòôõöúùûüç', "
        "'aaaaaeeeeiiiiooooouuuuc')"
    )

    @staticmethod
    def _preparar_filtro_bairro(bairro: Optional[str]) -> Tuple[Optional[str], str]:
        """Normaliza o filtro de bairro sem acentos para busca LIKE no Oracle."""
        if not bairro or not bairro.strip():
            return None, "%"
        termo = normalizar_texto(bairro)
        if not termo:
            return None, "%"
        return termo, f"%{termo}%"

    @classmethod
    def _obter_config(cls) -> Dict[str, Any]:
        """Obtém os parâmetros Oracle a partir das variáveis de ambiente carregadas no config."""
        user = os.environ.get("ORACLE_USER", ORACLE_USER).strip()
        password = os.environ.get("ORACLE_PASSWORD", ORACLE_PASSWORD).strip()
        url = os.environ.get("ORACLE_URL", ORACLE_URL).strip()
        dsn = os.environ.get("ORACLE_DSN", ORACLE_DSN).strip() or "oracle.fiap.com.br:1521/orcl"

        if url and "@//" in url:
            partes = url.split("@//")
            if len(partes) > 1 and partes[1].strip():
                dsn = partes[1].strip()

        return {
            "user": user,
            "password": password,
            "dsn": dsn,
        }

    @classmethod
    def _conectar(cls):
        """Estabelece conexão com o Oracle com timeouts defensivos de rede e query."""
        if not HAS_ORACLE:
            return None
        cfg = cls._obter_config()
        if not cfg["user"] or not cfg["password"]:
            return None
        try:
            conn = oracledb.connect(
                user=cfg["user"],
                password=cfg["password"],
                dsn=cfg["dsn"],
                tcp_connect_timeout=3.0,
                expire_time=5,
            )
            try:
                conn.call_timeout = 5000
            except Exception:
                pass
            return conn
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
    def consultar_chamado_com_status(
        cls,
        id_chamado: int,
        incluir_foto: bool = False
    ) -> Tuple[Optional[Dict[str, Any]], str]:
        """
        Consulta (somente SELECT) os dados de um chamado no Oracle e distingue
        'encontrado', 'nao_encontrado', 'oracle_offline' e 'erro'.
        """
        conn = cls._conectar()
        if not conn:
            return None, "oracle_offline"

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
                    return None, "nao_encontrado"

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
                    "tamanho_foto_bytes": tam_foto,
                }

                # Carrega BLOB apenas sob demanda para economizar rede e RAM
                if incluir_foto and tem_foto_valida and tam_foto <= 8 * 1024 * 1024:
                    try:
                        cursor.execute("SELECT foto FROM chamado WHERE id_chamado = :id_chamado", id_chamado=id_chamado)
                        blob_row = cursor.fetchone()
                        if blob_row and blob_row[0]:
                            resultado["foto_bytes"] = blob_row[0].read()
                    except Exception as err_blob:
                        logger.warning(f"Erro ao ler BLOB de foto do chamado {id_chamado}: {err_blob}")

                return resultado, "encontrado"
        except Exception as e:
            logger.warning(f"Erro ao consultar chamado {id_chamado} no Oracle: {e}")
            return None, "erro"
        finally:
            try:
                conn.close()
            except Exception:
                pass

    @classmethod
    def obter_chamado_completo(cls, id_chamado: int, incluir_foto: bool = False) -> Optional[Dict[str, Any]]:
        """Retorna os dados do chamado no Oracle ou None se indisponível/inexistente."""
        dados, _ = cls.consultar_chamado_com_status(id_chamado, incluir_foto=incluir_foto)
        return dados

    @classmethod
    def listar_chamados_recentes(cls, limit: int = 10, bairro: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lista os chamados mais recentes cadastrados no Oracle (somente leitura, limitado)."""
        conn = cls._conectar()
        if not conn:
            return []

        limite_seguro = max(1, min(int(limit), 25))
        bairro_norm, bairro_like = cls._preparar_filtro_bairro(bairro)
        query = f"""
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
            WHERE (:bairro_norm IS NULL OR {cls._SQL_BAIRRO_NORM} LIKE :bairro_like)
            ORDER BY c.id_chamado DESC
            FETCH FIRST :limit ROWS ONLY
        """

        chamados = []
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, bairro_norm=bairro_norm, bairro_like=bairro_like, limit=limite_seguro)
                for row in cursor.fetchall():
                    dt_str = row[4].strftime("%d/%m/%Y") if row[4] else ""
                    chamados.append({
                        "id": row[0],
                        "titulo": row[1],
                        "categoria": row[2] or "Geral",
                        "bairro": row[3] or "São Paulo",
                        "dt_abertura": dt_str,
                        "status": row[5] or "ABERTO",
                        "votos": row[6] or 0,
                    })
        except Exception as e:
            logger.warning(f"Erro ao listar chamados no Oracle: {e}")
        finally:
            try:
                conn.close()
            except Exception:
                pass

        return chamados

    @classmethod
    def resumo_estatistico_bairro(cls, bairro: Optional[str] = None) -> Dict[str, Any]:
        """
        Retorna contagem agregada (SELECT somente leitura) de chamados e votos por categoria.
        """
        conn = cls._conectar()
        if not conn:
            return {"oracle_online": False, "bairro": bairro, "total_chamados": 0, "total_votos": 0, "por_categoria": {}}

        bairro_limpo = bairro.strip() if bairro and bairro.strip() else None
        bairro_norm, bairro_like = cls._preparar_filtro_bairro(bairro_limpo)

        query_cat = f"""
            SELECT
                NVL(cat.nm_categoria, 'Geral') AS categoria,
                COUNT(DISTINCT c.id_chamado) AS total
            FROM chamado c
            LEFT JOIN categoria cat ON c.categoria_id_categoria = cat.id_categoria
            LEFT JOIN endereco e ON c.endereco_id_endereco = e.id_endereco
            LEFT JOIN bairro b ON e.bairro_id_bairro = b.id_bairro
            WHERE (:bairro_norm IS NULL OR {cls._SQL_BAIRRO_NORM} LIKE :bairro_like)
            GROUP BY NVL(cat.nm_categoria, 'Geral')
            ORDER BY total DESC
            FETCH FIRST 10 ROWS ONLY
        """
        query_votos = f"""
            SELECT COUNT(1)
            FROM voto_chamado v
            JOIN chamado c ON v.chamado_id_chamado = c.id_chamado
            LEFT JOIN endereco e ON c.endereco_id_endereco = e.id_endereco
            LEFT JOIN bairro b ON e.bairro_id_bairro = b.id_bairro
            WHERE (:bairro_norm IS NULL OR {cls._SQL_BAIRRO_NORM} LIKE :bairro_like)
        """

        por_categoria: Dict[str, int] = {}
        total_chamados = 0
        total_votos = 0
        try:
            with conn.cursor() as cursor:
                cursor.execute(query_cat, bairro_norm=bairro_norm, bairro_like=bairro_like)
                for cat, total in cursor.fetchall():
                    qtd = int(total or 0)
                    por_categoria[cat] = qtd
                    total_chamados += qtd

                cursor.execute(query_votos, bairro_norm=bairro_norm, bairro_like=bairro_like)
                row_v = cursor.fetchone()
                total_votos = int(row_v[0] or 0) if row_v else 0

            return {
                "oracle_online": True,
                "bairro": bairro_limpo,
                "total_chamados": total_chamados,
                "total_votos": total_votos,
                "por_categoria": por_categoria,
            }
        except Exception as e:
            logger.warning(f"Erro ao obter resumo estatístico no Oracle: {e}")
            return {"oracle_online": False, "bairro": bairro_limpo, "total_chamados": 0, "total_votos": 0, "por_categoria": {}}
        finally:
            try:
                conn.close()
            except Exception:
                pass
