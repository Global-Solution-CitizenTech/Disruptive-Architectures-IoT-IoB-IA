#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes de Regressão Determinísticos — ZelaFix AI (Sem gasto de cota Groq)
Cobre ViaCEP, extração dinâmica de bairros/protocolos, filtro Oracle acento-insensível,
heurística local de triagem e parsing JSON defensivo.
"""
import sys
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv

load_dotenv(".env")

from src.services.viacep_client import ViaCepClient, _consultar_cep_cacheado
from src.services.chamado_oracle_service import ChamadoOracleService
from src.services.triagem_service import TriagemService
from src.services.groq_service import GroqService
from src.database.oracle_client import OracleClient
from src.utils.text import normalizar_texto


def rodar_testes() -> int:
    falhas = 0

    def checar(nome: str, condicao: bool, detalhe: str = ""):
        nonlocal falhas
        status = "OK" if condicao else "FALHA"
        print(f"[{status}] {nome}" + (f" -> {detalhe}" if detalhe else ""))
        if not condicao:
            falhas += 1

    # 1. ViaCepClient (validação + mock offline + consulta real opcional)
    checar("ViaCep rejeita CEP curto", ViaCepClient.normalizar_cep("12345") is None)
    checar("ViaCep normaliza CEP formatado", ViaCepClient.normalizar_cep("05422-000") == "05422000")

    _consultar_cep_cacheado.cache_clear()
    with patch("src.services.viacep_client.httpx.get", side_effect=TimeoutError("timeout simulado")):
        checar("ViaCep retorna None em timeout", ViaCepClient.consultar_cep("01310-100") is None)

    _consultar_cep_cacheado.cache_clear()
    mock_resp = MagicMock(status_code=200)
    mock_resp.json.return_value = {
        "cep": "05422-000",
        "logradouro": "Rua dos Pinheiros",
        "bairro": "Pinheiros",
        "localidade": "São Paulo",
        "uf": "SP",
    }
    with patch("src.services.viacep_client.httpx.get", return_value=mock_resp):
        dados_cep = ViaCepClient.consultar_cep("05422-000")
        checar("ViaCep extrai bairro corretamente", bool(dados_cep and dados_cep["bairro"] == "Pinheiros"), str(dados_cep))

    # 2. Extração de protocolo/ID sem falsos positivos
    checar("Extrai 'chamado número 2'", ChamadoOracleService.extrair_id_chamado_da_pergunta("Qual a situação do chamado número 2?") == 2)
    checar("Extrai '#2' direto", ChamadoOracleService.extrair_id_chamado_da_pergunta("Como está o #2?") == 2)
    checar("Ignora número de endereço", ChamadoOracleService.extrair_id_chamado_da_pergunta("Buraco na Rua Paulista nº 100") is None)

    # 3. Extração dinâmica de bairro (sem lista fixa) + ViaCEP
    with patch.object(OracleClient, "listar_bairros_cadastrados", return_value=["Sé", "Pinheiros", "Consolação", "Vila Mariana"]):
        checar(
            "Extrai bairro sem acento contra catálogo Oracle ('consolacao')",
            ChamadoOracleService.extrair_bairro_listagem("tem chamados abertos na consolacao?") == "Consolação",
        )
        checar(
            "Extrai bairro composto em minúsculas ('vila mariana')",
            ChamadoOracleService.extrair_bairro_listagem("quais chamados em vila mariana?") == "Vila Mariana",
        )
        checar(
            "Extrai bairro composto fora do catálogo ('Freguesia do Ó')",
            normalizar_texto(ChamadoOracleService.extrair_bairro_listagem("quais ocorrencias na freguesia do ó?") or "") == "freguesia do o",
        )
        checar(
            "Stopword 'em aberto' não vira bairro",
            ChamadoOracleService.extrair_bairro_listagem("quais chamados em aberto?") == "__TODOS__",
        )

    with patch("src.services.chamado_oracle_service.ViaCepClient.consultar_cep", return_value={"bairro": "Bela Vista"}):
        checar(
            "Extrai bairro via CEP na pergunta",
            ChamadoOracleService.extrair_bairro_listagem("tem chamados no CEP 01310-100?") == "Bela Vista",
        )

    # 4. Heurística local corrigida
    h_calcada = TriagemService._classificar_heuristica_local(
        "geral", normalizar_texto("buraco na calcada dificultando passagem de cadeirante"), 1, False, []
    )
    checar("Heurística 'buraco na calçada' -> Passeio/Acessibilidade", "Passeio" in h_calcada["orgao_responsavel"], h_calcada["orgao_responsavel"])

    h_luz = TriagemService._classificar_heuristica_local(
        "geral", normalizar_texto("rua escura sem luz perto da praca"), 1, False, []
    )
    checar("Heurística 'rua escura sem luz' -> Ilumina SP", "Ilumina" in h_luz["orgao_responsavel"], h_luz["orgao_responsavel"])

    h_dren = TriagemService._classificar_heuristica_local(
        "drenagem", normalizar_texto("bueiro entupido com vazamento de agua da chuva"), 1, False, []
    )
    checar("Heurística 'bueiro com agua da chuva' -> Drenagem/SIURB", "Drenagem" in h_dren["orgao_responsavel"], h_dren["orgao_responsavel"])

    # 5. GroqService extração JSON com texto envolvente
    fake_completion = MagicMock()
    fake_completion.choices = [MagicMock(message=MagicMock(content='Segue o laudo:\n{"prioridade": "ALTA", "sla_sugerido_horas": 24}\nFim.'))]
    fake_client = MagicMock()
    fake_client.chat.completions.create.return_value = fake_completion
    with patch.object(GroqService, "_obter_cliente", return_value=fake_client):
        parsed = GroqService.gerar_resposta_json("teste")
        checar("GroqService extrai JSON mesmo com texto antes/depois", bool(parsed and parsed.get("prioridade") == "ALTA"), str(parsed))

    # 6. Oracle real (se disponível): catálogo de bairros + busca acento-insensível
    bairros_reais = OracleClient.listar_bairros_cadastrados()
    if bairros_reais:
        checar("Oracle retorna bairros dinâmicos", len(bairros_reais) > 0, f"{len(bairros_reais)} bairro(s)")
    else:
        print("[INFO] Oracle offline/vazio para teste de catálogo real; ignorado.")

    print(f"\nResumo: {falhas} falha(s).")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(rodar_testes())
