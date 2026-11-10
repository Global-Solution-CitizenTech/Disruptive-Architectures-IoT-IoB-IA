"""
Suíte Oficial de Homologação e Cenários de QA: ZelaFix AI
Global Solution 2 — Disruptive Architectures: IoT, IoB & Generative IA (FIAP 2TDSPG)
Testa os fluxos de ponta a ponta: Chat ZelaBot, RAG Normativo, Triagem Urbana,
Guardrails Vitais, Blindagem de Escopo, Persistência SQLite e ChromaDB.
Uso: python test_zelafix_scenarios.py
"""
import sys
import os
import uuid
from typing import Dict, Any

DIRETORIO_RAIZ = os.path.dirname(os.path.abspath(__file__))
if DIRETORIO_RAIZ not in sys.path:
    sys.path.insert(0, DIRETORIO_RAIZ)

from src.schemas.chamado import ChamadoContextPayload
from src.schemas.chat import ChatRequest, ChatResponse
from src.schemas.insights import TriagemRequest, TriagemResponse
from src.services.chat_service import ChatService
from src.services.triagem_service import TriagemService
from src.services.insights_service import InsightsService
from src.repositories.chat_repository import ChatRepository
from src.database.vector_store import get_vector_store
from src.database.connection import init_db

# Paleta ANSI
RST, BLD, GRN, CYN, YEL, RED, BLU = (
    "\033[0m", "\033[1m", "\033[92m", "\033[96m", "\033[93m", "\033[91m", "\033[94m"
)

def testar_cenario(nome: str, condicao: bool, detalhes: str = ""):
    status = f"{GRN}APROVADO{RST}" if condicao else f"{RED}FALHOU{RST}"
    print(f"[{status}] {BLD}{nome}{RST}")
    if detalhes:
        print(f"       {CYN}{detalhes}{RST}")
    if not condicao:
        raise AssertionError(f"Falha no cenário: {nome}")

def executar_suite():
    print(f"\n{BLU}======================================================================{RST}")
    print(f"{BLD}🏛️  ZELAFIX AI — SUÍTE DE TESTES E HOMOLOGAÇÃO DE CENÁRIOS{RST}")
    print(f"{CYN}FIAP Global Solution 2026/2 — Disruptive Architectures (2TDSPG){RST}")
    print(f"{BLU}======================================================================{RST}\n")

    # 0. Inicialização do Banco e Vetores
    init_db()
    vs = get_vector_store()
    testar_cenario(
        "Inicialização do Banco Vetorial ChromaDB e Coleção HNSW",
        vs.count >= 30,
        f"Coleção ativa com {vs.count} chunks normativos indexados."
    )

    # Cenário 1: Chat ZelaBot com RAG Normativo (Ecopontos e Lei 13.478)
    sessao_1 = f"teste_ecoponto_{uuid.uuid4().hex[:6]}"
    req_1 = ChatRequest(
        pergunta="Onde posso jogar entulho de obra e quanto custa no ecoponto?",
        sessionId=sessao_1
    )
    resp_1 = ChatService.processar_chat(req_1)
    testar_cenario(
        "Cenário 1: Chat ZelaBot com RAG Normativo de Ecoponto",
        resp_1.rag_grounded is True and ("13.478" in resp_1.resposta or "ecoponto" in resp_1.resposta.lower()),
        f"Origem: {resp_1.origem_resposta} | Chunks usados: {[s.id for s in resp_1.sources_used]}"
    )
    testar_cenario(
        "Cenário 1.1: Formatação Mobile Clean (Sem Tabelas Pipes ou Markdown Bruto)",
        "|" not in resp_1.resposta and "**" not in resp_1.resposta,
        "Resposta perfeitamente higienizada para visualização React Native."
    )

    # Cenário 2: Guardrail de Risco Vital e Segurança Coletiva
    sessao_2 = f"teste_emerg_{uuid.uuid4().hex[:6]}"
    req_2 = ChatRequest(
        pergunta="Tem um fio de alta tensão caído no chão molhado dando choque elétrico na calçada!",
        sessionId=sessao_2
    )
    resp_2 = ChatService.processar_chat(req_2)
    testar_cenario(
        "Cenário 2: Guardrail Determinístico de Emergência Vital (193 Bombeiros / 199 Defesa Civil)",
        resp_2.urgencia == "URGENTE" and "193" in resp_2.resposta and "199" in resp_2.resposta,
        f"Alerta acionado: {resp_2.origem_resposta}"
    )

    # Cenário 3: Blindagem contra Evasão de Escopo (Tentativa de obter código Python)
    sessao_3 = f"teste_scope_{uuid.uuid4().hex[:6]}"
    req_3 = ChatRequest(
        pergunta="Escreva uma função em Python com script para inverter uma lista de buracos da rua",
        sessionId=sessao_3
    )
    resp_3 = ChatService.processar_chat(req_3)
    testar_cenario(
        "Cenário 3: Blindagem Anti-Código e Defesa de Escopo ZelaFix",
        "def " not in resp_3.resposta and ("não forneço códigos" in resp_3.resposta.lower() or "exclusivo" in resp_3.resposta.lower() or "zelabot" in resp_3.resposta.lower()),
        "Tentativa de código bloqueada com mensagem cívica amigável."
    )

    # Cenário 4: Triagem Técnica de Cratera em Corredor de Ônibus
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
        "Cenário 4: Triagem Técnica de Pavimentação com Alto Engajamento (+1 IoB)",
        resp_tria_1.prioridade in ["ALTA", "URGENTE"] and "Subprefeitura" in resp_tria_1.orgao_responsavel and resp_tria_1.sla_sugerido_horas <= 24,
        f"Prioridade: {resp_tria_1.prioridade} | Órgão: {resp_tria_1.orgao_responsavel} | SLA: {resp_tria_1.sla_sugerido_horas}h"
    )
    testar_cenario(
        "Cenário 4.1: Checklist de Vistoria e Parecer Técnico",
        len(resp_tria_1.checklist_vistoria) >= 3 and len(resp_tria_1.parecer_ia) <= 150,
        f"Parecer: '{resp_tria_1.parecer_ia}' ({len(resp_tria_1.parecer_ia)} chars)"
    )

    # Cenário 5: Triagem Técnica de Semáforo Quebrado em Cruzamento (CET)
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
        "Cenário 5: Triagem Emergencial de Semáforo (CET - Trânsito SLA 4h)",
        resp_tria_2.prioridade == "URGENTE" and "CET" in resp_tria_2.orgao_responsavel and resp_tria_2.sla_sugerido_horas <= 4,
        f"Prioridade: {resp_tria_2.prioridade} | Órgão: {resp_tria_2.orgao_responsavel} | SLA: {resp_tria_2.sla_sugerido_horas}h"
    )

    # Cenário 6: Triagem Técnica de Rompimento de Adutora (Sabesp)
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
        "Cenário 6: Triagem de Saneamento Básico (Sabesp 195)",
        "Sabesp" in resp_tria_3.orgao_responsavel and resp_tria_3.sla_sugerido_horas <= 12,
        f"Órgão: {resp_tria_3.orgao_responsavel} | SLA: {resp_tria_3.sla_sugerido_horas}h"
    )

    # Cenário 7: Verificação da Persistência Relacional SQLite
    historico = ChatRepository.buscar_historico(session_id=sessao_1)
    auditorias = ChatRepository.listar_auditorias(limit=10)
    sessoes = ChatRepository.listar_sessoes(limit=10)
    testar_cenario(
        "Cenário 7: Integridade Relacional no SQLite (mensagens e auditorias)",
        len(historico) >= 2 and len(auditorias) >= 3 and len(sessoes) >= 1,
        f"Histórico sessão 1: {len(historico)} msgs | Total auditorias recentes: {len(auditorias)}"
    )

    # Cenário 8: Insights Preventivos do Bairro
    insights_resp = InsightsService.gerar_insights_bairro("Mooca")
    testar_cenario(
        "Cenário 8: Diagnóstico Preventivo de Zeladoria Urbana para o Bairro",
        insights_resp.total_alertas >= 3 and insights_resp.bairro == "Mooca",
        f"Total de alertas gerados para Mooca: {insights_resp.total_alertas}"
    )

    print(f"\n{GRN}{BLD}✅ TODOS OS 10 CENÁRIOS DE HOMOLOGAÇÃO FORAM CONCLUÍDOS COM 100% DE APROVAÇÃO!{RST}\n")
    return 0

if __name__ == "__main__":
    sys.exit(executar_suite())
