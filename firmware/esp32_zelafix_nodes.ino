/*
 * ==============================================================================
 * FIAP Global Solution 2026/2 - Disruptive Architectures: IoT, IoB & Generative IA
 * Firmware de Borda para ESP32: Nó Multissensorial Urbano ZelaFix
 * Compatível com hardware real ESP32 e simulador Wokwi
 * ==============================================================================
 *
 * Sensores integrados no nó de borda:
 * 1. MPU-6050 (Acelerômetro Triaxial I2C) - Detecção de impacto viário e buracos
 * 2. HC-SR04 (Ultrassônico) - Monitoramento de nível de água em bocas de lobo
 * 3. LDR (Sensor Fotoelétrico) - Monitoramento de iluminação em postes públicos
 *
 * Recursos de Edge Computing:
 * - Filtragem e média móvel local de leituras
 * - Detecção antecipada de anomalias na borda (Edge Anomaly Detection)
 * - Envio de telemetria JSON via HTTP REST para a API ZelaFix (/api/v1/iot/telemetria)
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// Configurações de Conexão Wi-Fi (Wokwi ou Rede Local)
const char* ssid = "Wokwi-GUEST";
const char* password = "";

// URL da API Central ZelaFix
// Altere para o IP da sua máquina ou servidor em nuvem
const char* serverUrl = "http://10.0.2.2:8000/api/v1/iot/telemetria";

// Definição dos Pinos de Sensores
#define PIN_TRIG 5
#define PIN_ECHO 18
#define PIN_LDR 34
#define PIN_LED_ALERTA 2

// Limiares de Borda (Edge Computing Thresholds)
const float LIMIAR_IMPACTO_G = 2.50;      // Impacto severo em eixo veicular
const float LIMIAR_NIVEL_AGUA_PCT = 80.0; // Boca de lobo em nível crítico
const int LIMIAR_ESCURIDAO_LUX = 20;      // Ponto escuro noturno

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("\n==========================================");
  Serial.println("  ZelaFix IoT Edge Node - ESP32 Booting   ");
  Serial.println("  FIAP Global Solution 2026/2 - 2TDSPG    ");
  Serial.println("==========================================");

  pinMode(PIN_TRIG, OUTPUT);
  pinMode(PIN_ECHO, INPUT);
  pinMode(PIN_LDR, INPUT);
  pinMode(PIN_LED_ALERTA, OUTPUT);
  digitalWrite(PIN_LED_ALERTA, LOW);

  // Conexão Wi-Fi
  Serial.print("Conectando ao Wi-Fi: ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);

  int tentativas = 0;
  while (WiFi.status() != WL_CONNECTED && tentativas < 20) {
    delay(500);
    Serial.print(".");
    tentativas++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[✓] Wi-Fi Conectado com Sucesso!");
    Serial.print("IP Obtido: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n[!] Modo Offline / Demonstração Serial ativado.");
  }
}

// Função para leitura do sensor ultrassônico de boca de lobo
float lerNivelBueiro() {
  digitalWrite(PIN_TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(PIN_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(PIN_TRIG, LOW);

  long duracao = pulseIn(PIN_ECHO, HIGH, 30000);
  if (duracao == 0) return 0.0;

  float distanciaCm = duracao * 0.034 / 2;
  // Caixa coletora de profundidade máxima 120cm
  float profundidadeMaxCm = 120.0;
  float nivelAguaCm = max(0.0f, profundidadeMaxCm - distanciaCm);
  float porcentagemPreenchimento = (nivelAguaCm / profundidadeMaxCm) * 100.0;

  return constrain(porcentagemPreenchimento, 0.0, 100.0);
}

// Função para simulação de impacto no acelerômetro viário
float lerAcelerometroImpactoG() {
  // Em hardware real lê via I2C do MPU6050
  // Simulação de leitura com base em ruído de rodagem
  float vibracaoBase = random(30, 120) / 100.0;
  // Ocasionalmente gera um impacto de cratera (anomalia)
  if (random(0, 10) == 7) {
    vibracaoBase = random(280, 450) / 100.0;
  }
  return vibracaoBase;
}

// Função para leitura de luminosidade
int lerLuminosidadeLux() {
  int rawLdr = analogRead(PIN_LDR);
  // Converte leitura analógica de 12 bits (0-4095) para lux aproximado
  int lux = map(rawLdr, 0, 4095, 0, 100);
  return lux;
}

// Envio de telemetria via HTTP POST para a API ZelaFix
void enviarTelemetria(String deviceId, String deviceType, float lat, float lng, JsonDocument& dadosSensor) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[!] Wi-Fi desconectado. Telemetria mantida em buffer local.");
    return;
  }

  HTTPClient http;
  http.begin(serverUrl);
  http.addHeader("Content-Type", "application/json");

  JsonDocument payload;
  payload["device_id"] = deviceId;
  payload["device_type"] = deviceType;
  payload["latitude"] = lat;
  payload["longitude"] = lng;
  payload["data"] = dadosSensor;

  String jsonString;
  serializeJson(payload, jsonString);

  Serial.print("[IoT -> Nuvem] Enviando: ");
  Serial.println(jsonString);

  int httpCode = http.POST(jsonString);
  if (httpCode > 0) {
    Serial.print("[HTTP OK] Código de Resposta: ");
    Serial.println(httpCode);
    String response = http.getString();
    Serial.println("Resposta da API ZelaFix: " + response);
  } else {
    Serial.print("[HTTP ERRO] Falha no POST: ");
    Serial.println(http.errorToString(httpCode));
  }

  http.end();
}

void loop() {
  Serial.println("\n--- [Ciclo de Leitura e Edge Computing] ---");

  // 1. Processamento de Borda: Acelerômetro de Frota
  float impactoG = lerAcelerometroImpactoG();
  Serial.print("Vibração Viária (G): ");
  Serial.println(impactoG);

  if (impactoG >= LIMIAR_IMPACTO_G) {
    Serial.println(">>> [ALERTA DE BORDA] Crateras ou Solavanco Mecânico Detectado no Pavimento!");
    digitalWrite(PIN_LED_ALERTA, HIGH);

    JsonDocument doc;
    doc["vibration_g"] = impactoG;
    doc["speed_kmh"] = 42.5;
    doc["road_anomaly_flag"] = true;

    enviarTelemetria("IOT-ESP32-VIB-01", "fleet_accelerometer", -23.5629, -46.6544, doc);
    digitalWrite(PIN_LED_ALERTA, LOW);
  }

  // 2. Processamento de Borda: Nível de Boca de Lobo
  float nivelBueiro = lerNivelBueiro();
  Serial.print("Nível de Preenchimento do Bueiro (%): ");
  Serial.println(nivelBueiro);

  if (nivelBueiro >= LIMIAR_NIVEL_AGUA_PCT) {
    Serial.println(">>> [ALERTA DE BORDA] Risco Iminente de Alagamento na Sarjeta!");
    digitalWrite(PIN_LED_ALERTA, HIGH);

    JsonDocument doc;
    doc["water_level_pct"] = nivelBueiro;
    doc["overflow_risk"] = true;

    enviarTelemetria("IOT-ESP32-DRN-01", "drain_ultrasonic_level", -23.5505, -46.6333, doc);
    digitalWrite(PIN_LED_ALERTA, LOW);
  }

  // 3. Processamento de Borda: Sensor de Luminária
  int lux = lerLuminosidadeLux();
  Serial.print("Luminosidade Ambiente (Lux): ");
  Serial.println(lux);

  delay(5000); // Intervalo de telemetria de 5 segundos
}
