# 🏛️ AGENT.md — Especificação Técnica & Arquitetura do Agente ZelaFix AI

> **Projeto:** ZelaFix AI — Copiloto Inteligente de Triagem Urbana, Visão Computacional & Zeladoria Municipal  
> **Disciplina:** Disruptive Architectures: IoT, IoB & Generative IA (FIAP — 2TDSPG)  
> **Núcleo de Produção:** Microsserviço FastAPI em Produção no Render ([`deploy_zelafixai_render`](./deploy_zelafixai_render))  
> **Banco de Dados Oficial:** Oracle Database FIAP (`oracle.fiap.com.br:1521/orcl` — Modo Thin, somente leitura `SELECT`)  
> **Provedor de IA:** Azure AI Foundry (`ai-zelafix-e2-561432` — `phi-4-multimodal` + `embed-v-4-0`)  

---

## 🎯 1. Visão Geral & Propósito do Agente

O **ZelaFix AI** é o motor de inteligência artificial generativa multimodal e inteligência comportamental (IoB) da plataforma CitizenTech **ZelaFix**. Desenvolvido com foco no **ODS 11 da ONU (Cidades e Comunidades Sustentáveis)**, o agente atua entre os munícipes da Cidade de São Paulo e os órgãos públicos municipais:

1. **Atendimento Cívico Especializado (ZelaBot):** Orienta munícipes sobre direitos, prazos regulamentares (SLAs) e procedimentos municipais fundamentados na legislação paulistana via RAG semântico em nuvem (`embed-v-4-0`, 1536D).
2. **Visão Computacional Multimodal (Azure AI Foundry `phi-4-multimodal`):** Analisa fotografias enviadas pelos cidadãos (ou recuperadas do Oracle sob demanda), identificando danos urbanos e emitindo parecer técnico em formato estruturado (Pydantic JSON).
3. **Triagem Automática e Enquadramento Normativo:** Classifica prioridade (`BAIXA`, `MEDIA`, `ALTA`, `URGENTE`), órgão responsável, SLA regulamentar, enquadramento legal e checklist técnico de vistoria via Structured Outputs — sem matrizes rígidas de palavras-chave manuais.
4. **Internet of Behaviors (IoB) & IoT:** Incorpora confirmações comunitárias (`+1` >= 25 apoios) e anomalias de sensores urbanos para elevar automaticamente a prioridade mínima da ocorrência para `ALTA` / `URGENTE`.
5. **Integração Somente Leitura com Oracle FIAP:** Consulta chamados, histórico, votos e resumo de bairros via `oracledb` em Modo Thin (`SELECT` estrito) tanto por *fast-path* (`#ID`) quanto via **Tool Calling** nativo (`consultar_chamados_oracle`, `calcular_prazo_sla`).

---

## 🏗️ 2. Arquitetura do Pipeline RAG & Inferência Multimodal

```text
 ┌────────────────────────────────────────────────────────────────────────┐
 │                   📱 APLICATIVO MOBILE (REACT NATIVE)                  │
 │      Foto do dano urbano + Relato cívico + Localização + Votos (+1)    │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │ POST /ai/chat | /ai/triagem | /ai/insights
                                     ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │                ⚡ FASTAPI CONTROLLER (ROUTER /AI)                      │
 │  1. Validação de Schema Pydantic (ChatRequest / TriagemRequest)        │
 │  2. Proteção LGPD na entrada (mascaramento de CPF e cartão)            │
 └───────────────────┬───────────────────────────────┬────────────────────┘
                     │                               │
    (Tool Call / Fast-Path #ID)                      ▼
                     │            ┌───────────────────────────────────────┐
                     ▼            │ 🔍 RAG SEMÂNTICO EM NUVEM (CHROMA DB) │
 ┌─────────────────────────────┐  │  • Embeddings: embed-v-4-0 (1536D)    │
 │  🏛️ ORACLE FIAP (MODO THIN) │  │  • ChromaDB Persistente (HNSW Cosine) │
 │  • Somente leitura (SELECT) │  │  • Fingerprint SHA-256 (0 reindexação │
 │  • Protocolo, Status, Votos │  │    desnecessária entre restarts)      │
 │  • BLOB de Foto sob demanda │  │  • 31 Chunks Decretos PMSP (Top-K)    │
 └─────────────┬───────────────┘  └──────────────────┬────────────────────┘
               │                                     │
               └─────────────────┬───────────────────┘
                                 ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │           🚀 AZURE AI FOUNDRY (`openai` SDK /OpenAI v1)                │
 │  • Modelo Único: phi-4-multimodal (Visão + Tool Calling + JSON)        │
 │  • Sem fallback para outro modelo LLM                                  │
 │  • Structured Output validado via Pydantic                             │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │        🧹 HIGIENIZAÇÃO MOBILE CLEAN & AUDITORIA RELACIONAL             │
 │  • Remoção de markdown/tabelas com pipes (`|`) para tela Mobile        │
 │  • Mascaramento LGPD na saída + Persistência SQLite (histórico/audit)  │
 └────────────────────────────────────────────────────────────────────────┘
```

---

## 📚 3. Base de Conhecimento RAG: Decretos e Leis da Cidade de São Paulo

A base normativa é composta por **31 chunks atômicos** distribuídos em **8 módulos temáticos**, indexados no ChromaDB com vetores densos de **1536 dimensões (`embed-v-4-0`)**:

```text
+-----------------------+-----------------------------+---------+------------------------------------------------+
| Módulo Legislativo    | Instrumento Normativo       | Chunks  | Competência & Órgão Responsável                |
+-----------------------+-----------------------------+---------+------------------------------------------------+
| Pavimentação          | Decreto Municipal 59.150/19 | pav_01..| Subprefeituras / SMSUB (Tapa-buraco, recape)   |
| Drenagem & Bueiros    | Decreto Municipal 57.545/16 | dren_01.| SIURB / Subprefeituras (Bocas de lobo, galerias|
| Saneamento Básico     | Regulamento ARSESP / 195    | sab_01..| Companhia Sabesp (Adutoras, esgoto e ramais)   |
| Iluminação Pública    | Portaria SGM/SES 03/2021    | ilum_01.| PPP Ilumina SP (Postes apagados, fiação LED)   |
| Manejo Arbóreo        | Lei Municipal 17.267/2020   | arb_01..| Subprefeituras (Poda) / ENEL (Fiação primária) |
| Limpeza Urbana        | Lei Municipal 13.478/2002   | limp_01.| AMLURB / Subprefeitura (Ecopontos, entulho)    |
| Sinalização Viária    | Código de Trânsito / CET    | cet_01..| Companhia de Engenharia de Tráfego (CET-SP)    |
| Direitos do Cidadão   | Decreto 58.611/19 & SP156   | faq_01..| Ouvidoria Geral / Carta de Serviços SP156      |
+-----------------------+-----------------------------+---------+------------------------------------------------+
```

---

## 🗄️ 4. Integração Somente Leitura com Banco Oracle FIAP (Modo Thin)

O microsserviço acessa a base Oracle FIAP com `oracledb` em **Modo Thin (100% Python)**, executando exclusivamente consultas `SELECT` parametrizadas (zero escrita/DDL) com timeout de 3 segundos e suporte a *Tool Calling* (`consultar_chamados_oracle`) e `calcular_prazo_sla`.

---

## 🛡️ 5. Proteção de Dados (LGPD) & Higienização Mobile Clean

1. **Conformidade LGPD:** Mascara automaticamente números de CPF e cartões na entrada e antes de enviar contexto à nuvem ou gravar no SQLite.
2. **Higienização Mobile Clean:** Remove `**`, `*` e tabelas Markdown (`| col |`), garantindo formatação limpa (`• `) no app React Native.
