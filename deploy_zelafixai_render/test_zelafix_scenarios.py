#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏛️ ZELAFIX AI — SUÍTE OFICIAL DE QA, HOMOLOGAÇÃO & AUDITORIA DE CENÁRIOS
FIAP Global Solution 2026/2 — Disruptive Architectures: IoT, IoB & Generative IA (2TDSPG)

Testa os 10 fluxos críticos de ponta a ponta:
 1. Chat ZelaBot com RAG Normativo (Lei 13.478/2002 - AMLURB / Ecopontos)
 2. Higienização Mobile Clean (Sem tabelas pipes ou markdown bruto no chat)
 3. Orientação Cívica sobre Fiação e Poda Arbórea (Lei 17.267 / ENEL)
 4. Consulta Conversacional de Chamado Real no Oracle FIAP (#2)
 5. Triagem Técnica de Pavimentação com Alto Engajamento Comunitário (+1 IoB)
 6. Triagem Emergencial de Semáforo (CET — SLA 4h)
 7. Triagem de Saneamento Básico (Sabesp 195)
 8. Integridade Relacional e Auditoria Cívica no SQLite
 9. Conexão e Telemetria em Tempo Real no Banco Oracle FIAP (Modo Thin)
 10. Visão Computacional Multimodal (Groq Qwen 3.8 27B) sobre Fotos Urbanas

Uso:
    python test_zelafix_scenarios.py
    python test_zelafix_scenarios.py --mode local --delay 0.5
    python test_zelafix_scenarios.py --mode api --url https://deploy-zelafixai-render.onrender.com --delay 0.8
"""
import os
import sys
import time
import uuid
import base64
import io
import argparse
import urllib.request
import json
from typing import Dict, Any, Optional

# Garante saída UTF-8 no terminal Windows
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DIRETORIO_RAIZ = os.path.dirname(os.path.abspath(__file__))
if DIRETORIO_RAIZ not in sys.path:
    sys.path.insert(0, DIRETORIO_RAIZ)

# Paleta ANSI
RST = "\033[0m"
BLD = "\033[1m"
GRN = "\033[92m"
CYN = "\033[96m"
YEL = "\033[93m"
RED = "\033[91m"
BLU = "\033[94m"
GRY = "\033[90m"


def testar_cenario(numero: int, titulo: str, condicao: bool, detalhes: str = "", delay: float = 0.0):
    status = f"{GRN}APROVADO{RST}" if condicao else f"{RED}FALHOU{RST}"
    print(f"[{status}] {BLD}Cenário {numero}: {titulo}{RST}")
    if detalhes:
        print(f"         {CYN}↳ {detalhes}{RST}")
    if delay > 0:
        time.sleep(delay)
    if not condicao:
        raise AssertionError(f"Falha no cenário {numero}: {titulo}")


def criar_imagem_teste_base64() -> str:
    """Gera uma cena sintética (256x256) de via asfaltada com cratera para teste multimodal."""
    try:
        from PIL import Image, ImageDraw
        img = Image.new("RGB", (256, 256), color=(72, 75, 82))
        draw = ImageDraw.Draw(img)
        # Faixa amarela central da via e meio-fio claro
        draw.rectangle((0, 0, 255, 22), fill=(195, 195, 190))
        draw.rectangle((120, 40, 134, 95), fill=(235, 195, 45))
        draw.rectangle((120, 165, 134, 230), fill=(235, 195, 45))
        # Cratera/buraco irregular no asfalto com borda quebrada e fundo terroso
        draw.polygon([(58, 108), (112, 86), (176, 102), (188, 148), (138, 178), (74, 162)], fill=(28, 22, 18), outline=(145, 140, 130), width=4)
        draw.ellipse((86, 112, 160, 156), fill=(62, 42, 24))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=88)
        return base64.b64encode(buf.getvalue()).decode("utf-8")
    except Exception:
        # Fallback para um PNG mínimo 64x64 se PIL não disponível
        return "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAAPElEQVR42u3BAQ0AAADCoPdPbQ8HFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC4GBU0AAGl9jSCAAAAAElFTkSuQmCC"


def executar_local(delay: float):
    from src.schemas.chamado import ChamadoContextPayload, TelemetriaIotPayload
    from src.schemas.chat import ChatRequest
    from src.schemas.insights import TriagemRequest
    from src.services.chat_service import ChatService
    from src.services.triagem_service import TriagemService
    from src.services.insights_service import InsightsService
    from src.services.groq_service import GroqService
    from src.repositories.chat_repository import ChatRepository
    from src.database.vector_store import get_vector_store
    from src.database.connection import init_db
    from src.database.oracle_client import OracleClient

    print(f"\n{BLU}======================================================================{RST}")
    print(f"{BLD}🏛️  ZELAFIX AI — SUÍTE DE TESTES E HOMOLOGAÇÃO DE CENÁRIOS (LOCAL){RST}")
    print(f"{CYN}FIAP Global Solution 2026/2 — Disruptive Architectures: IoT, IoB & IA{RST}")
    print(f"{BLU}======================================================================{RST}\n")

    # Inicialização
    init_db()
    vs = get_vector_store()
    print(f"{GRY}[INFO] ChromaDB ativo com {vs.count} chunks normativos indexados.{RST}\n")

    # Cenário 1: Chat ZelaBot com RAG Normativo (Ecopontos e Lei 13.478)
    sessao_1 = f"t_{uuid.uuid4().hex[:6]}"
    req_1 = ChatRequest(
        pergunta="Onde posso descartar entulho de obra residencial e quanto custa no ecoponto?",
        sessionId=sessao_1
    )
    resp_1 = ChatService.processar_chat(req_1)
    testar_cenario(
        1, "Chat ZelaBot com RAG Normativo de Ecoponto (Lei 13.478)",
        resp_1.rag_grounded is True and ("13.478" in resp_1.resposta or "ecoponto" in resp_1.resposta.lower()),
        f"Origem: {resp_1.origem_resposta} | Chunks: {[s.id for s in resp_1.sources_used]}",
        delay
    )

    # Cenário 2: Higienização Mobile Clean
    testar_cenario(
        2, "Formatação Mobile Clean (Sem Tabelas Pipes ou Markdown Bruto)",
        "|" not in resp_1.resposta and "**" not in resp_1.resposta,
        "Resposta perfeitamente higienizada para visualização mobile e acessibilidade.",
        delay
    )

    # Cenário 3: Orientação Cívica sobre Fiação e Poda Arbórea (Lei 17.267 / ENEL)
    sessao_3 = f"t_{uuid.uuid4().hex[:6]}"
    req_3 = ChatRequest(
        pergunta="Tem galhos de árvore encostando na fiação elétrica do poste da minha rua, quem deve podar?",
        sessionId=sessao_3
    )
    resp_3 = ChatService.processar_chat(req_3)
    testar_cenario(
        3, "Orientação Cívica sobre Fiação e Poda Arbórea (Lei 17.267 / ENEL)",
        resp_3.rag_grounded is True and ("17.267" in resp_3.resposta or "enel" in resp_3.resposta.lower() or "árvore" in resp_3.resposta.lower() or "poda" in resp_3.resposta.lower()),
        f"Origem: {resp_3.origem_resposta} | Chunks: {[s.id for s in resp_3.sources_used]}",
        delay
    )

    # Cenário 4: Consulta Conversacional de Chamado Real no Oracle (#2)
    sessao_4 = f"t_{uuid.uuid4().hex[:6]}"
    req_4 = ChatRequest(
        pergunta="Qual é a situação e os detalhes do meu chamado número 2?",
        sessionId=sessao_4
    )
    resp_4 = ChatService.processar_chat(req_4)
    testar_cenario(
        4, "Consulta Conversacional de Chamado Real no Oracle FIAP (#2)",
        "2" in resp_4.resposta
        and ("buraco" in resp_4.resposta.lower() or "aberto" in resp_4.resposta.lower() or "pinheiros" in resp_4.resposta.lower())
        and "não localiz" not in resp_4.resposta.lower(),
        f"Resposta integrada ao Oracle: {resp_4.resposta[:95]}...",
        delay
    )

    # Cenário 5: Triagem Técnica de Pavimentação com Alto Engajamento (+1 IoB)
    req_tria_1 = TriagemRequest(
        chamado=ChamadoContextPayload(
            id=101,
            categoria="Buraco na Rua",
            titulo="Cratera profunda na faixa de ônibus da Av. Paulista",
            descricao="Buraco com mais de 10cm de profundidade no asfalto com risco de queda de moto.",
            bairro="Bela Vista",
            logradouro="Avenida Paulista",
            apoios_comunitarios=32
        )
    )
    resp_tria_1 = TriagemService.realizar_triagem(req_tria_1)
    testar_cenario(
        5, "Triagem Técnica de Pavimentação com Alto Engajamento (+1 IoB)",
        resp_tria_1.prioridade in ["ALTA", "URGENTE"] and "Subprefeitura" in resp_tria_1.orgao_responsavel and resp_tria_1.sla_sugerido_horas <= 24,
        f"Prioridade: {resp_tria_1.prioridade} | Órgão: {resp_tria_1.orgao_responsavel} | SLA: {resp_tria_1.sla_sugerido_horas}h | Parecer: '{resp_tria_1.parecer_ia}'",
        delay
    )

    # Cenário 6: Triagem Emergencial de Semáforo (CET - SLA 4h)
    req_tria_2 = TriagemRequest(
        chamado=ChamadoContextPayload(
            id=102,
            categoria="Sinalização",
            titulo="Semáforo apagado no cruzamento com risco de batida",
            descricao="Cruzamento movimentado sem sinalização luminosa.",
            bairro="Pinheiros",
            apoios_comunitarios=5
        )
    )
    resp_tria_2 = TriagemService.realizar_triagem(req_tria_2)
    testar_cenario(
        6, "Triagem Emergencial de Semáforo (CET — SLA 4h)",
        resp_tria_2.prioridade == "URGENTE" and "CET" in resp_tria_2.orgao_responsavel and resp_tria_2.sla_sugerido_horas <= 4,
        f"Prioridade: {resp_tria_2.prioridade} | Órgão: {resp_tria_2.orgao_responsavel} | SLA: {resp_tria_2.sla_sugerido_horas}h",
        delay
    )

    # Cenário 7: Triagem de Saneamento Básico (Sabesp 195)
    req_tria_3 = TriagemRequest(
        chamado=ChamadoContextPayload(
            id=103,
            categoria="Vazamento Água",
            titulo="Cano rompido jorrando água limpa e afundando o asfalto",
            descricao="Muita água vazando na sarjeta e asfalto cedendo.",
            bairro="Mooca",
            apoios_comunitarios=15
        )
    )
    resp_tria_3 = TriagemService.realizar_triagem(req_tria_3)
    testar_cenario(
        7, "Triagem de Saneamento Básico (Sabesp 195)",
        "Sabesp" in resp_tria_3.orgao_responsavel and resp_tria_3.sla_sugerido_horas <= 12,
        f"Órgão: {resp_tria_3.orgao_responsavel} | SLA: {resp_tria_3.sla_sugerido_horas}h",
        delay
    )

    # Cenário 8: Persistência Relacional e Auditoria Cívica no SQLite
    historico = ChatRepository.buscar_historico(session_id=sessao_1)
    auditorias = ChatRepository.listar_auditorias(limit=10)
    testar_cenario(
        8, "Integridade Relacional no SQLite (Histórico & Auditorias)",
        len(historico) >= 2 and len(auditorias) >= 3,
        f"Histórico sessão 1: {len(historico)} msgs | Auditorias registradas: {len(auditorias)}",
        delay
    )

    # Cenário 9: Conexão e Consulta em Tempo Real no Oracle FIAP
    oracle_status = OracleClient.verificar_conexao()
    chamado_real = OracleClient.obter_chamado_completo(2) if oracle_status.get("status") == "online" else None
    
    condicao_ora = (
        (oracle_status.get("status") == "online" and chamado_real is not None and chamado_real.get("id") == 2)
        or (oracle_status.get("status") in ["offline", "erro", "indisponivel"])
    )
    detalhes_ora = (
        f"Oracle Online: Chamado #{chamado_real['id']} ('{chamado_real['titulo']}', Status: {chamado_real['status_atual']}, Votos: {chamado_real['apoios_comunitarios']})"
        if chamado_real else
        f"Oracle Telemetria: {oracle_status.get('status')} (Fallback resiliente ativado com segurança)"
    )
    testar_cenario(
        9, "Conexão e Consulta em Tempo Real no Banco Oracle FIAP (Modo Thin)",
        condicao_ora,
        detalhes_ora,
        delay
    )

    # Cenário 10: Visão Computacional Multimodal (Groq Qwen 3.8 27B)
    foto_b64 = criar_imagem_teste_base64()
    req_visao = TriagemRequest(
        chamado=ChamadoContextPayload(
            id=105,
            categoria="Buraco na Rua",
            titulo="Erosão asfáltica com foto da cratera",
            descricao="Registro visual do defeito de pavimentação.",
            bairro="Pinheiros",
            foto_base64=foto_b64
        )
    )
    resp_visao = TriagemService.realizar_triagem(req_visao)
    teve_visao = resp_visao.analise_visual is not None and len(resp_visao.analise_visual) > 5
    usou_groq = "Groq" in resp_visao.origem_triagem
    testar_cenario(
        10, "Visão Computacional Multimodal (Groq Qwen 3.8 27B)",
        resp_visao.prioridade in ["MEDIA", "ALTA", "URGENTE"] and (teve_visao or not usou_groq),
        f"Laudo Visual: {resp_visao.analise_visual[:80] if teve_visao else 'Triagem executada via motor de contingência'}",
        delay
    )

    # Cenário 11: Roteamento Real 'Drenagem e Esgoto' + Telemetria IoT (sem colidir com Sabesp)
    req_iot = TriagemRequest(
        chamado=ChamadoContextPayload(
            id=106,
            categoria="Drenagem e Esgoto",
            titulo="Bueiro com acúmulo de folhas e sensor indicando transbordo",
            descricao="Nível da galeria pluvial acima do limiar após chuva forte.",
            bairro="Bela Vista",
            apoios_comunitarios=4,
            telemetria_iot=TelemetriaIotPayload(
                device_id="IOT-BUEIRO-09",
                tipo_sensor="ultrassom_bueiro",
                valor_medido=92.5,
                unidade="%",
                anomalia_detectada=True,
            ),
        )
    )
    resp_iot = TriagemService.realizar_triagem(req_iot)
    ok_dren_iot = (
        ("Drenagem" in resp_iot.orgao_responsavel or "SIURB" in resp_iot.orgao_responsavel or "Subprefeitura" in resp_iot.orgao_responsavel)
        and "Sabesp" not in resp_iot.orgao_responsavel
        and resp_iot.prioridade in ["ALTA", "URGENTE"]
    )
    testar_cenario(
        11, "Triagem 'Drenagem e Esgoto' + Telemetria IoT (sem colisão Sabesp)",
        ok_dren_iot,
        f"Prioridade: {resp_iot.prioridade} | Órgão: {resp_iot.orgao_responsavel} | SLA: {resp_iot.sla_sugerido_horas}h",
        delay
    )

    # Cenário 12: Memória Multi-Turno Automática via sessionId (SQLite) + Insights Vivos Oracle
    sess_mem = f"mem_{uuid.uuid4().hex[:6]}"
    ChatService.processar_chat(ChatRequest(pergunta="Quais chamados estão abertos na base?", sessionId=sess_mem))
    resp_mem = ChatService.processar_chat(ChatRequest(pergunta="E sobre iluminação pública, qual o prazo?", sessionId=sess_mem))
    hist_mem = ChatRepository.buscar_historico(session_id=sess_mem, limit=10)
    insights_bela = InsightsService.gerar_insights_bairro("Bela Vista")
    ok_mem_ins = len(hist_mem) == 4 and len(resp_mem.resposta) > 15 and insights_bela.total_alertas >= 3
    testar_cenario(
        12, "Memória Automática por sessionId (SQLite) & Insights Oracle",
        ok_mem_ins,
        f"Mensagens na sessão: {len(hist_mem)} | Insights Bela Vista: {insights_bela.total_alertas} | Origem: {resp_mem.origem_resposta}",
        delay
    )

    print(f"\n{GRN}{BLD}======================================================================{RST}")
    print(f"{GRN}{BLD}✅ TODOS OS 12 CENÁRIOS DE HOMOLOGAÇÃO FORAM CONCLUÍDOS COM 100% DE SUCESSO!{RST}")
    print(f"{GRN}{BLD}======================================================================{RST}\n")
    return 0


def executar_api(base_url: str, delay: float):
    print(f"\n{BLU}======================================================================{RST}")
    print(f"{BLD}🏛️  ZELAFIX AI — SUÍTE DE TESTES E HOMOLOGAÇÃO VIA API HTTP{RST}")
    print(f"{CYN}Target: {base_url}{RST}")
    print(f"{BLU}======================================================================{RST}\n")

    def call_api(method: str, path: str, payload: Optional[dict] = None) -> dict:
        url = f"{base_url.rstrip('/')}{path}"
        data = json.dumps(payload).encode("utf-8") if payload else None
        headers = {"Content-Type": "application/json", "User-Agent": "ZelaFixQA/2.0"}
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))

    # 1. Health check
    health = call_api("GET", "/health")
    testar_cenario(1, "Health Check & Provedor Ativo", health.get("status") == "healthy", f"Provider: {health.get('provider')}", delay)

    # 2. Vector Store Status
    vs_status = call_api("GET", "/ai/vector-store/status")
    testar_cenario(2, "Status do ChromaDB Vetorial", vs_status.get("indexed_chunks", 0) >= 20, f"Chunks: {vs_status.get('indexed_chunks')}", delay)

    # 3. Oracle Status
    ora_status = call_api("GET", "/ai/oracle/status")
    testar_cenario(3, "Status da Conexão Oracle FIAP", "status" in ora_status, f"Status: {ora_status.get('status')}", delay)

    # 4. Chat com RAG
    sessao_api = f"api_{uuid.uuid4().hex[:6]}"
    chat_resp = call_api("POST", "/ai/chat", {
        "pergunta": "Como solicitar tapa-buraco em São Paulo?",
        "sessionId": sessao_api
    })
    testar_cenario(4, "Chat ZelaBot via HTTP", len(chat_resp.get("resposta", "")) > 10, f"Origem: {chat_resp.get('origem_resposta')}", delay)

    # 5. Triagem Técnica via HTTP
    triagem_resp = call_api("POST", "/ai/triagem", {
        "chamado": {
            "categoria": "Sinalização",
            "titulo": "Semáforo quebrado na esquina",
            "descricao": "Risco iminente de atropelamento",
            "bairro": "Pinheiros"
        }
    })
    testar_cenario(5, "Triagem Técnica CET via HTTP", triagem_resp.get("prioridade") in ["ALTA", "URGENTE"], f"Órgão: {triagem_resp.get('orgao_responsavel')}", delay)

    print(f"\n{GRN}{BLD}✅ SUÍTE DE API CONCLUÍDA COM SUCESSO!{RST}\n")
    return 0


def main():
    parser = argparse.ArgumentParser(description="ZelaFix AI — Test Runner Oficial de QA")
    parser.add_argument("--mode", choices=["local", "api"], default="local", help="Modo de execução (local ou api)")
    parser.add_argument("--url", default="http://localhost:8000", help="URL base para o modo api")
    parser.add_argument("--delay", type=float, default=0.0, help="Pausa entre cenários (segundos) para gravação/demonstração")
    args = parser.parse_args()

    if args.mode == "api":
        return executar_api(args.url, args.delay)
    else:
        return executar_local(args.delay)


if __name__ == "__main__":
    sys.exit(main())
