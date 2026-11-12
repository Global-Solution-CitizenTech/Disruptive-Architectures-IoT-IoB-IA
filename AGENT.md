# 🏛️ AGENT.md — Especificação Técnica & Arquitetura do Agente ZelaFix AI

> **Projeto:** ZelaFix AI — Copiloto Inteligente de Triagem Urbana, Visão Computacional & Zeladoria Municipal  
> **Disciplina:** Disruptive Architectures: IoT, IoB & Generative IA (FIAP — 2TDSPG)  
> **Núcleo de Produção:** Microsserviço FastAPI em Produção no Render ([`deploy_zelafixai_render`](./deploy_zelafixai_render))  
> **Banco de Dados Oficial:** Oracle Database FIAP (`oracle.fiap.com.br:1521/orcl` — Modo Thin)  
> **Status:** Concluído, homologado e 100% operacional  

---

## 🎯 1. Visão Geral & Propósito do Agente

O **ZelaFix AI** é o motor de inteligência artificial generativa multimodal e inteligência comportamental (IoB) da plataforma CitizenTech **ZelaFix**. Desenvolvido com foco no **ODS 11 da ONU (Cidades e Comunidades Sustentáveis)**, o agente atua na linha de frente entre os munícipes da Cidade de São Paulo e o poder público:

1. **Atendimento Cívico Especializado (ZelaBot):** Orienta munícipes sobre direitos, deveres, prazos regulamentares (SLAs) e procedimentos municipais com embasamento estrito na legislação de São Paulo.
2. **Visão Computacional Multimodal (Groq Qwen 3.8 27B):** Analisa fotografias enviadas pelos cidadãos, identificando o tipo de dano na infraestrutura (buracos, asfalto cedido, semáforos quebrados, bocas de lobo obstruídas, fios rompidos) e emitindo parecer técnico objetivo.
3. **Triagem Automática e Enquadramento Normativo:** Classifica a urgência da ocorrência (`BAIXA`, `MEDIA`, `ALTA`, `URGENTE`), identifica a secretaria competente (Subprefeitura, CET, Ilumina SP, Sabesp, AMLURB, ENEL, Defesa Civil) e gera checklist técnico de vistoria presencial.
4. **Internet of Behaviors (IoB):** Incorpora o engajamento coletivo através dos apoios comunitários (+1 dos vizinhos) para reescalonar a prioridade na fila de atendimento da prefeitura.
5. **Integração Real-Time com Banco Oracle FIAP:** Consulta ocorrências diretamente na base relacional oficial da solução via driver Python Thin sem dependência de binários externos, garantindo compatibilidade total com contêineres cloud Linux.

---

## 🏗️ 2. Arquitetura do Pipeline RAG & Inferência Multimodal

```text
 ┌────────────────────────────────────────────────────────────────────────┐
 │                   📱 APLICATIVO MOBILE (REACT NATIVE)                  │
 │      Foto do dano urbano + Relato cívico + Localização + Votos (+1)    │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │ POST /ai/chat ou POST /ai/triagem
                                     ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │                ⚡ FASTAPI CONTROLLER (ROUTER /AI)                      │
 │  1. Validação de Schema Pydantic (ChatRequest / TriagemRequest)        │
 │  2. Guardrail Determinístico Vital (Fios energizados, 193/199)          │
 │  3. Blindagem Anti-Código e Defesa de Escopo Municipal                │
 └───────────────────┬───────────────────────────────┬────────────────────┘
                     │                               │
       (Se menciona chamado #ID)                     ▼
                     │            ┌───────────────────────────────────────┐
                     ▼            │ 🔍 RECUPERAÇÃO RAG & BANCO VETORIAL   │
 ┌─────────────────────────────┐  │  • ChromaDB (HNSW Cosine Metric)      │
 │  🏛️ ORACLE FIAP (MODO THIN) │  │  • LocalSemanticEmbedder (R^512)      │
 │  • Título e Descrição       │  │  • 31 Chunks Decretos PMSP (Top-K)    │
 │  • Status Atual e Histórico │  │  • Score de corte: RAG_MIN_SCORE 0.18 │
 │  • Total de Apoios (+1 IoB) │  └──────────────────┬────────────────────┘
 │  • BLOB de Foto do Chamado  │                     │
 └─────────────┬───────────────┘                     ▼
               │                  ┌───────────────────────────────────────┐
               └─────────────────►│ 📝 MONTAGEM DO PROMPT FUNDAMENTADO    │
                                  │  • System Prompt ZelaFix              │
                                  │  • Contexto real do Oracle / DTO      │
                                  │  • Chunks legislativos PMSP           │
                                  └──────────────────┬────────────────────┘
                                                     │
                                                     ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │           🚀 INFERÊNCIA MULTIMODAL GROQ CLOUD (QWEN 3.8 27B)           │
 │  • Visão Computacional sobre imagem Base64 (defeito físico e risco)    │
 │  • Geração fundamentada citando decretos e leis municipais             │
 │  • Fallback automático: Motor Heurístico Local Resiliente              │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │        🧹 HIGIENIZAÇÃO MOBILE CLEAN & AUDITORIA RELACIONAL             │
 │  • Remoção de tabelas markdown brutas (formatação limpa para celular)  │
 │  • Anonimização e proteção de dados (LGPD)                             │
 │  • Persistência em SQLite (mensagens_chat + auditoria_triagens)        │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │  Retorno JSON: ChatResponse / TriagemResponse com Parecer e Metadados  │
 └────────────────────────────────────────────────────────────────────────┘
```

---

## 📚 3. Base de Conhecimento RAG: Decretos e Leis da Cidade de São Paulo

A base normativa é composta por **31 chunks atômicos de alta precisão** distribuídos em **8 módulos temáticos**, indexados no ChromaDB com representação vetorial densa de 512 dimensões:

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

### 3.1. Eliminação de Colisão Semântica
Cada módulo possui vocabulário léxico estrito para evitar falsos positivos cruzados:
- Água pluvial em bueiro pertence exclusivamente a `drenagem_bueiros.py` (Decreto 57.545/2016).
- Vazamento de água tratada ou esgoto pertence exclusivamente a `saneamento_sabesp.py` (Sabesp Central 195).
- Queda de árvore sem fiação compete à Subprefeitura (Lei 17.267/2020); contato com fiação energizada transfere competência para a concessionária ENEL.

---

## 🗄️ 4. Integração com Banco de Dados Oracle FIAP (Modo Thin)

O ZelaFix AI conecta-se diretamente ao cluster oficial de banco de dados Oracle da FIAP através da biblioteca `oracledb` operando em **Modo Thin (100% Python nativo)**.

### Vantagens do Modo Thin em Produção no Render:
- **Zero Binários Externos:** Não requer instalação do Oracle Instant Client C-libraries (inviáveis no container enxuto do Render).
- **Timeouts Defensivos:** Conexão TCP com timeout estrito de 3 segundos para proteger a API de travamentos caso haja oscilação na rede acadêmica.
- **Consultas Parametrizadas:** Blindagem total contra SQL Injection.

### Consultas em Tempo Real Realizadas:
```text
+-----------------------------------+----------------------------------------------------------------------------+
| Operação                          | Dados Extraídos do Oracle                                                  |
+-----------------------------------+----------------------------------------------------------------------------+
| Enriquecimento no Chat            | Identifica "chamado nº 2" no texto do munícipe e recupera dados reais     |
| Consulta de Chamado Específico    | ID, Título, Descrição, Categoria, Endereço, Bairro, Status Atual e Votos   |
| Contagem de Votos Comunitários    | Apura os registros na tabela VOTO_CHAMADO para cálculo de IoB              |
| Histórico de Mudanças             | Busca o status mais recente via JOIN em HIST_CHAMADO e STATUS              |
| Recuperação de Foto BLOB          | Lê o binário da foto gravada na coluna FOTO para inspeção visual Qwen      |
+-----------------------------------+----------------------------------------------------------------------------+
```

---

## 👁️ 5. Visão Computacional Multimodal (Groq Qwen 3.8 27B)

O ZelaFix AI utiliza o modelo de pesos abertos de última geração **`qwen/qwen3.8-27b`** hospedado na infraestrutura de ultra-baixa latência da Groq Cloud.

### Pipeline de Visão:
1. **Recepção:** Recebe a foto do dano codificada em Base64 via payload HTTP (`foto_base64`) ou lê o BLOB diretamente da tabela `CHAMADO` do Oracle.
2. **Sanitização de Imagem:** Valida o cabeçalho base64 e garante dimensões mínimas exigidas pela API da Groq (mínimo de 32x32 pixels, redimensionando defensivamente via Pillow quando necessário).
3. **Prompt Multimodal Estruturado:** Instrui o Qwen como engenheiro de zeladoria urbana da PMSP a diagnosticar o defeito físico em 1 a 2 frases objetivas, severidade aparente e risco de acidentes.
4. **Laudo Visual Integrado:** O parecer visual é retornado no campo `analise_visual` da resposta de triagem técnica.

---

## 🛡️ 6. Guardrails de Segurança Cívica & Higienização

1. **Guardrail de Emergência Vital (Risco Letal Imediato):** Detecta menções a fios energizados no chão, postes caídos com faísca ou crateras com risco iminente de morte, instruindo contato imediato com **Corpo de Bombeiros (193)** e **Defesa Civil (199)**.
2. **Blindagem Anti-Código (Defesa de Escopo):** Bloqueia tentativas de desvio de escopo (como pedidos de scripts Python, código Java ou geração de software), mantendo o foco exclusivo em zeladoria urbana.
3. **Higienização Mobile Clean:** Elimina markdown denso e tabelas de pipes (`| col |`), formatando listas com marcadores limpos (`•`) para renderização perfeita no app móvel React Native.
4. **Conformidade LGPD:** Mascara números de CPF, telefones pessoais e e-mails que o munícipe possa digitar no relato antes da persistência no banco.

---

## 📊 7. Métricas de Homologação & Testes de Qualidade

```text
+---------------------------------------------+---------------+------------+
| Suíte de Validação Oficial                  | Casos / Testes| Resultado  |
+---------------------------------------------+---------------+------------+
| Cobertura RAG (test_knowledge_coverage.py)  | 35 cenários   | 100% OK    |
| Homologação de Ponta a Ponta (run_qa_demo)   | 10 cenários   | 100% OK    |
| Bateria de Estresse & Carga (stress_test)   | 28 testes     | 100% OK    |
| Conexão Oracle Thin (oracle.fiap.com.br)    | Real Time     | 100% OK    |
| Fallback Local Heurístico Resiliente        | Contingência  | 100% OK    |
+---------------------------------------------+---------------+------------+
```
