# Firmware de Borda IoT — Nó Multissensorial ESP32
**FIAP Global Solution 2026/2 — Disruptive Architectures: IoT, IoB & Generative IA**
**Projeto:** ZelaFix — Zeladoria Urbana Inteligente

---

## 1. Visão Geral do Hardware de Borda (Edge Computing)

O firmware implementado em `esp32_zelafix_nodes.ino` é responsável por coletar dados físicos de sensores em tempo real no espaço urbano, executar filtragem de sinais e detecção de anomalias na borda (Edge Computing) e transmitir telemetrias JSON para a API REST central do ZelaFix.

### Sensores e Atuadores Mapeados:
1. **Sensor de Vibração e Impacto Mecânico (Acelerômetro):**
   - Instalado no eixo de ônibus municipais e viaturas de fiscalização.
   - Mede solavancos no pavimento viário. Se a vibração ultrapassar **2.50G**, detecta cratera no asfalto e despacha alerta de emergência.
2. **Sensor Ultrassônico (HC-SR04):**
   - Instalado sob a grelha de bocas de lobo críticas.
   - Mede a distância até a lâmina d'água na caixa coletora. Se o nível de preenchimento ultrapassar **80.0%**, sinaliza risco iminente de alagamento por obstrução de galeria.
3. **Sensor de Luminosidade (LDR / Fotocélula):**
   - Instalado no topo de luminárias públicas.
   - Detecta apagões noturnos em áreas de alta circulação de pedestres.
4. **LED de Alerta Local (Atuador):**
   - Pisca em vermelho ao registrar anomalia crítica na borda.

---

## 2. Pinagem e Ligações do ESP32 (Pinout)

| Componente | Pino do Componente | Pino do ESP32 | Função |
| :--- | :---: | :---: | :--- |
| **HC-SR04** | VCC | 5V / VIN | Alimentação do sensor ultrassônico |
| **HC-SR04** | GND | GND | Aterramento comum |
| **HC-SR04** | TRIG | GPIO 5 | Disparo do pulso sonoro (Trigger) |
| **HC-SR04** | ECHO | GPIO 18 | Recepção do eco (Echo) |
| **Sensor LDR** | VCC | 3V3 | Alimentação do sensor fotoelétrico |
| **Sensor LDR** | GND | GND | Aterramento |
| **Sensor LDR** | AO (Analógico) | GPIO 34 (ADC1_CH6) | Leitura da tensão fotoelétrica proporcional aos Lux |
| **LED Alerta** | Ânodo (+) | GPIO 2 | Sinal de ativação de emergência na borda |
| **LED Alerta** | Cátodo (-) | Resistor 220Ω -> GND | Limitação de corrente |

---

## 3. Como Executar a Simulação no Wokwi

1. Acesse o simulador online gratuito: [https://wokwi.com](https://wokwi.com).
2. Crie um novo projeto selecionando **ESP32**.
3. Substitua o conteúdo do arquivo `diagram.json` pelo conteúdo do nosso [`firmware/diagram.json`](diagram.json).
4. Substitua o código do `sketch.ino` pelo código de [`firmware/esp32_zelafix_nodes.ino`](esp32_zelafix_nodes.ino).
5. Adicione a biblioteca `ArduinoJson` na aba *Library Manager* do Wokwi.
6. Clique no botão verde de **Play** (Iniciar Simulação).
7. Acompanhe as leituras e diagnósticos de borda em tempo real no Monitor Serial a 115200 baud!
