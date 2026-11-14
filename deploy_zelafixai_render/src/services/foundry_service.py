"""
Serviço Unificado de IA Generativa, Visão Computacional, Tool Calling e Embeddings
via Azure AI Foundry (API OpenAI-compatible v1) — ZelaFix AI
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)
"""
import io
import os
import re
import json
import math
import base64
import logging
import threading
from collections import OrderedDict
from typing import Optional, List, Dict, Any, Union, Callable, Type, TypeVar, Tuple

from openai import OpenAI
from pydantic import BaseModel, ValidationError
import src.core.config as cfg
from src.schemas.chat import MensagemHistorico

try:
    from PIL import Image, ImageOps
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

logger = logging.getLogger("ZelaFixAI.FoundryService")
T = TypeVar("T", bound=BaseModel)


def _normalizar_base_url(url: str) -> str:
    limpa = url.strip().rstrip("/")
    if limpa and not limpa.endswith("/openai/v1"):
        limpa = f"{limpa}/openai/v1"
    return limpa


def _l2_normalize(vec: List[float]) -> List[float]:
    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 1e-12:
        return [x / norm for x in vec]
    return vec


def _normalizar_chaves_json(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {re.sub(r"[\s_]+", "_", str(k).strip()).strip("_"): _normalizar_chaves_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_normalizar_chaves_json(i) for i in obj]
    return obj


def _extrair_json_bruto(texto: str) -> Optional[Dict[str, Any]]:
    if not texto:
        return None
    limpo = re.sub(r"<think>.*?</think>", "", texto, flags=re.DOTALL)
    limpo = re.sub(r"```json\s*|```", "", limpo, flags=re.IGNORECASE).strip()
    match = re.search(r"\{.*\}", limpo, flags=re.DOTALL)
    candidato = match.group(0) if match else limpo
    try:
        parsed = json.loads(candidato)
        return _normalizar_chaves_json(parsed) if isinstance(parsed, dict) else None
    except Exception:
        return None


class FoundryService:
    """
    Cliente thread-safe para o Azure AI Foundry:
    - Embeddings semânticos densos em nuvem (`embed-v-4-0`, 1536D) com cache LRU em memória.
    - Chat multimodal + Tool Calling nativo + Structured JSON Outputs via `AI_MODEL` (`phi-4-multimodal`).
    """

    MAX_HISTORICO_TURNOS = 6
    _MAX_CACHE_EMBEDDINGS = 256
    _lock = threading.Lock()
    _client: Optional[OpenAI] = None
    _client_sig: Optional[Tuple[str, str]] = None
    _embedding_cache: "OrderedDict[str, List[float]]" = OrderedDict()

    @classmethod
    def _obter_cliente(cls) -> Optional[OpenAI]:
        api_key = (os.environ.get("AI_API_KEY") or cfg.AI_API_KEY or "").strip()
        base_url = _normalizar_base_url(os.environ.get("AI_BASE_URL") or cfg.AI_BASE_URL or "")
        if not api_key or not base_url:
            return None

        with cls._lock:
            sig = (base_url, api_key)
            if cls._client is None or cls._client_sig != sig:
                cls._client = OpenAI(
                    base_url=base_url,
                    api_key=api_key,
                    timeout=cfg.AI_TIMEOUT_SECONDS,
                    max_retries=2,
                )
                cls._client_sig = sig
            return cls._client

    @classmethod
    def sanitizar_imagem_base64(cls, imagem_raw: Union[str, bytes]) -> Optional[str]:
        """Valida, corrige rotação EXIF e converte foto para JPEG base64 <= 1024px."""
        try:
            if isinstance(imagem_raw, bytes):
                dados = imagem_raw
            elif isinstance(imagem_raw, str):
                limpa = imagem_raw.strip()
                if "," in limpa and limpa.startswith("data:image"):
                    limpa = limpa.split(",", 1)[1]
                dados = base64.b64decode(limpa)
            else:
                return None

            if len(dados) < 32:
                return None

            if HAS_PIL:
                img = Image.open(io.BytesIO(dados))
                img = ImageOps.exif_transpose(img)
                if img.width < 32 or img.height < 32:
                    img = img.resize((max(32, img.width), max(32, img.height)))
                elif img.width > 1024 or img.height > 1024:
                    img.thumbnail((1024, 1024))
                buf = io.BytesIO()
                img.convert("RGB").save(buf, format="JPEG", quality=82)
                return base64.b64encode(buf.getvalue()).decode("utf-8")

            return base64.b64encode(dados).decode("utf-8")
        except Exception as err:
            logger.warning(f"Imagem inválida ignorada antes do envio ao Foundry: {err}")
            return None

    @classmethod
    def gerar_embeddings(cls, textos: List[str]) -> Optional[List[List[float]]]:
        """Gera embeddings normalizados em lote via Azure AI Foundry com cache LRU."""
        if not textos:
            return []

        limpos = [t[:8000].strip() or "vazio" for t in textos]
        resultados: List[Optional[List[float]]] = [None] * len(limpos)
        faltantes_idx: List[int] = []
        faltantes_txt: List[str] = []

        with cls._lock:
            for idx, txt in enumerate(limpos):
                cached = cls._embedding_cache.get(txt)
                if cached is not None:
                    cls._embedding_cache.move_to_end(txt)
                    resultados[idx] = cached
                else:
                    faltantes_idx.append(idx)
                    faltantes_txt.append(txt)

        if faltantes_txt:
            client = cls._obter_cliente()
            if client is None:
                return None
            emb_model = (os.environ.get("AI_EMBEDDING_MODEL") or cfg.AI_EMBEDDING_MODEL).strip()
            try:
                resp = client.embeddings.create(model=emb_model, input=faltantes_txt)
                gerados = [_l2_normalize(list(item.embedding)) for item in resp.data]
                with cls._lock:
                    for idx, txt, vec in zip(faltantes_idx, faltantes_txt, gerados):
                        resultados[idx] = vec
                        cls._embedding_cache[txt] = vec
                        cls._embedding_cache.move_to_end(txt)
                        if len(cls._embedding_cache) > cls._MAX_CACHE_EMBEDDINGS:
                            cls._embedding_cache.popitem(last=False)
            except Exception as err:
                logger.error(f"Erro ao gerar embeddings no Foundry ({emb_model}): {err}")
                return None

        return [v for v in resultados if v is not None]

    @classmethod
    def gerar_embedding(cls, texto: str) -> Optional[List[float]]:
        lote = cls.gerar_embeddings([texto])
        return lote[0] if lote else None

    @classmethod
    def _montar_mensagens(
        cls,
        system_prompt: str,
        user_prompt: str,
        historico: Optional[List[MensagemHistorico]] = None,
        imagem_b64: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        mensagens: List[Dict[str, Any]] = [{"role": "system", "content": system_prompt}]

        if historico:
            for item in historico[-cls.MAX_HISTORICO_TURNOS:]:
                role = "assistant" if item.sender in ("model", "assistant") else "user"
                mensagens.append({"role": role, "content": item.text[:1500]})

        if imagem_b64:
            mensagens.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": user_prompt[:12000]},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{imagem_b64}"}},
                ],
            })
        else:
            mensagens.append({"role": "user", "content": user_prompt[:12000]})

        return mensagens

    @staticmethod
    def _descrever_tools_prompt(tools: List[Dict[str, Any]]) -> str:
        linhas = [
            "\n\nFERRAMENTAS DISPONÍVEIS (somente use se o prompt ainda não trouxer os dados reais necessários):"
        ]
        for item in tools:
            fn = item.get("function") or {}
            nome = fn.get("name", "")
            desc = fn.get("description", "")
            props = list((fn.get("parameters") or {}).get("properties", {}).keys())
            linhas.append(f"- {nome}({', '.join(props)}): {desc}")
        linhas.append(
            'Para invocar uma ferramenta, retorne EXCLUSIVAMENTE o JSON: {"tool_call": {"name": "<nome>", "arguments": {...}}}. '
            "Caso já tenha as informações suficientes no prompt ou após receber o resultado da ferramenta, retorne diretamente o JSON final da resposta."
        )
        return "\n".join(linhas)

    @classmethod
    def _executar_modelo(
        cls,
        client: OpenAI,
        modelo: str,
        system_prompt: str,
        user_prompt: str,
        historico: Optional[List[MensagemHistorico]] = None,
        imagem_b64: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_executor: Optional[Callable[[str, Dict[str, Any]], str]] = None,
        json_mode: bool = False,
        max_tokens: int = 2048,
    ) -> Optional[str]:
        """Executa inferência no modelo configurado com suporte a ReAct Tool Calling via JSON."""
        prompt_sistema = system_prompt
        usar_tools = bool(tools and tool_executor)
        if usar_tools and tools:
            prompt_sistema = f"{system_prompt}{cls._descrever_tools_prompt(tools)}"

        mensagens = cls._montar_mensagens(prompt_sistema, user_prompt, historico, imagem_b64)
        for _ in range(3):
            kwargs: Dict[str, Any] = {
                "model": modelo,
                "messages": mensagens,
                "temperature": 0.2,
                "max_tokens": max_tokens,
            }
            if json_mode or usar_tools:
                kwargs["response_format"] = {"type": "json_object"}

            resp = client.chat.completions.create(**kwargs)
            conteudo = (resp.choices[0].message.content or "").strip()
            if not conteudo:
                return None

            if usar_tools and tool_executor:
                dados = _extrair_json_bruto(conteudo)
                tool_req = dados.get("tool_call") if isinstance(dados, dict) else None
                if not isinstance(tool_req, dict) and isinstance(dados, dict) and "resposta" not in dados:
                    for val in dados.values():
                        if isinstance(val, dict) and val.get("name"):
                            tool_req = val
                            break
                if isinstance(tool_req, dict) and tool_req.get("name"):
                    nome_fn = str(tool_req["name"]).strip()
                    args = tool_req.get("arguments") if isinstance(tool_req.get("arguments"), dict) else {}
                    saida = tool_executor(nome_fn, args)
                    mensagens.append({"role": "assistant", "content": conteudo})
                    mensagens.append({
                        "role": "user",
                        "content": (
                            f"[RESULTADO DA FERRAMENTA {nome_fn}]:\n{str(saida)[:4000]}\n\n"
                            "Agora gere a resposta final no formato JSON completo."
                        ),
                    })
                    continue

            return conteudo

        return None

    @classmethod
    def executar_chat(
        cls,
        system_prompt: str,
        user_prompt: str,
        historico: Optional[List[MensagemHistorico]] = None,
        imagem_base64: Optional[Union[str, bytes]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_executor: Optional[Callable[[str, Dict[str, Any]], str]] = None,
        json_mode: bool = False,
        max_tokens: int = 2048,
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Executa inferência no modelo único configurado (`AI_MODEL`) com suporte a visão, tools e JSON.
        Retorna (conteudo_texto, nome_modelo_utilizado).
        """
        client = cls._obter_cliente()
        modelo = (os.environ.get("AI_MODEL") or cfg.AI_MODEL).strip()
        if client is None or not modelo:
            return None, None

        img_limpa = cls.sanitizar_imagem_base64(imagem_base64) if imagem_base64 else None
        try:
            conteudo = cls._executar_modelo(
                client=client,
                modelo=modelo,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                historico=historico,
                imagem_b64=img_limpa,
                tools=tools,
                tool_executor=tool_executor,
                json_mode=json_mode,
                max_tokens=max_tokens,
            )
            if conteudo:
                return conteudo, modelo
        except Exception as err:
            logger.warning(f"Falha no modelo '{modelo}' do Azure AI Foundry: {err}")

        return None, None

    @classmethod
    def gerar_estruturado(
        cls,
        schema_cls: Type[T],
        system_prompt: str,
        user_prompt: str,
        historico: Optional[List[MensagemHistorico]] = None,
        imagem_base64: Optional[Union[str, bytes]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_executor: Optional[Callable[[str, Dict[str, Any]], str]] = None,
        max_tokens: int = 2048,
    ) -> Tuple[Optional[T], Optional[str]]:
        """Executa inferência em JSON Mode no modelo configurado (`AI_MODEL`) e valida via Pydantic."""
        conteudo, modelo = cls.executar_chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            historico=historico,
            imagem_base64=imagem_base64,
            tools=tools,
            tool_executor=tool_executor,
            json_mode=True,
            max_tokens=max_tokens,
        )
        if not conteudo:
            return None, None

        dados = _extrair_json_bruto(conteudo)
        if dados is None:
            logger.warning(f"Resposta do modelo '{modelo}' não continha JSON válido.")
            return None, None

        try:
            return schema_cls.model_validate(dados), modelo
        except ValidationError as err:
            logger.warning(f"Falha na validação Pydantic ({schema_cls.__name__}) em '{modelo}': {err}")
            return None, None
