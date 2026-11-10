# Relatório de Avaliação Quantitativa e Evidências da IA
**FIAP Global Solution 2026/2 — Disruptive Architectures: IoT, IoB & Generative IA**
**Data de Execução:** 10/11/2026 12:21:27
**Tema:** ZelaFix Mobile — Zeladoria Urbana Colaborativa (ODS 11 da ONU)

---

## 1. Resumo Executivo das Métricas

| Métrica de Avaliação | Resultado Obtido | Meta Mínima de Engenharia | Status |
| :--- | :---: | :---: | :---: |
| **Acurácia de Severidade (Accuracy)** | **96.43%** | > 85.0% | **APROVADO** |
| **F1-Score Ponderado (Severidade)** | **96.44%** | > 85.0% | **APROVADO** |
| **Precisão Ponderada (Precision)** | **96.60%** | > 80.0% | **APROVADO** |
| **Revocação Ponderada (Recall)** | **96.43%** | > 80.0% | **APROVADO** |
| **Acurácia de Categorização Visual** | **100.00%** | > 80.0% | **APROVADO** |
| **Latência Média de Inferência** | **3.11 ms** | < 250 ms | **EXCELENTE** |
| **Latência P95 (Percentil 95)** | **4.39 ms** | < 500 ms | **EXCELENTE** |

---

## 2. Matriz de Confusão (Severidade Urbana)

Distribuição das classificações reais vs preditas pelo sistema:

```
     Baixa     Média      Alta   Crítica
     Baixa        25         2         0         0
     Média         0        16         0         1
      Alta         0         0        12         0
   Crítica         0         0         0        28
```

---

## 3. Avaliação de Casos de Falha e Testes de Resiliência (Critério 05)

Foram executados testes adversariais para verificar o comportamento do sistema diante de entradas ruidosas ou degradadas:

### Caso `SMP-FAIL-01`
- **Motivo do Teste:** Texto extremamente vago sem detalhes e imagem totalmente escura com ruído de sensor.
- **Status do Pipeline:** `SUCESSO`
- **Prioridade Atribuída com Segurança:** `Média`
- **Órgão Encaminhado:** `Subprefeitura Local — Coordenadoria de Manutenção da Infraestrutura Urbana (Usina de Asfalto e Equipe de Tapa-Buraco).`
- **Comportamento Observado:** Sucesso - Fallback suave ativado sem interrupção do sistema

### Caso `SMP-FAIL-02`
- **Motivo do Teste:** Descrição textual vazia, foto superexposta e sensor IoT com valor de leitura ruidoso/corrompido.
- **Status do Pipeline:** `SUCESSO`
- **Prioridade Atribuída com Segurança:** `Média`
- **Órgão Encaminhado:** `Subprefeitura Local — Coordenadoria de Manutenção da Infraestrutura Urbana (Usina de Asfalto e Equipe de Tapa-Buraco).`
- **Comportamento Observado:** Sucesso - Fallback suave ativado sem interrupção do sistema

---

## 4. Análise Crítica das Limitações da IA (Item 06 do Edital)

1. **Condições Climáticas Extremas e Iluminação Noturna:**
   - Em períodos de chuvas torrenciais noturnas ou com ausência total de iluminação pública, as imagens capturadas por câmeras de smartphones sofrem com ruído de sensor (ISO elevado) e subexposição severa. O sistema mitiga isso ativando o alerta de baixa qualidade visual e transferindo o peso decisório para a telemetria física dos sensores IoT (acelerômetros e hidrômetros) e engajamento comunitário (IoB).

2. **Oclusão Parcial de Bocas de Lobo e Galerias Subterrâneas:**
   - A visão computacional consegue inspecionar somente a superfície externa da grelha do bueiro. Quando a obstrução ocorre a metros de profundidade no ramal de galeria, a imagem fotográfica pode parecer normal. Por essa razão, a arquitetura integra o sensor ultrassônico IoT de nível e vazão, garantindo a detecção precisa antes do transbordamento.

3. **Viés Comportamental de Densidade Populacional (IoB):**
   - Vias de bairros centrais de alto tráfego acumulam apoios (+1) mais rapidamente do que ruas de bairros periféricos de menor fluxo peatonal. Para evitar que bairros periféricos sejam preteridos, o algoritmo calcula o *Social Urgency Score* normalizado com o histórico de assertividade do relator, assegurando que um relato individual bem detalhado em uma periferia receba prioridade Crítica mesmo com poucos apoios no início.
