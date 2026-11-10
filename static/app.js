// ZelaFix IA & IoT Dashboard Client

const CENARIOS = {
  buraco_critico: {
    titulo: "Cratera profunda na faixa de rolamento da Avenida Paulista",
    categoria: "Buraco na Rua",
    descricao: "Cratera aberta no asfalto com mais de 10cm de profundidade logo após o cruzamento. Motociclistas quase sofrendo quedas e ônibus desviando bruscamente.",
    fotoUrl: "https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?auto=format&fit=crop&w=800&q=80",
    apoiosCount: 38,
    iot: {
      device_id: "IOT-VIB-SP-042",
      device_type: "fleet_accelerometer",
      data: { vibration_g: 3.85, speed_kmh: 42.0, road_anomaly_flag: true }
    }
  },
  bueiro_alagamento: {
    titulo: "Boca de lobo totalmente obstruída por lixo e terra",
    categoria: "Bueiro Entupido",
    descricao: "Água da chuva subindo rápido na sarjeta e ameaçando invadir garagens de casas. Bueiro entupido com garrafas PET e folhas.",
    fotoUrl: "https://images.unsplash.com/photo-1581375922343-ac6b40caf5e3?auto=format&fit=crop&w=800&q=80",
    apoiosCount: 29,
    iot: {
      device_id: "IOT-DRAIN-SP-108",
      device_type: "drain_ultrasonic_level",
      data: { water_level_pct: 92.5, overflow_risk: true }
    }
  },
  poste_apagado: {
    titulo: "Apagão de quatro postes seguidos na travessia de pedestres",
    categoria: "Iluminação Pública",
    descricao: "Escuridão absoluta em frente à passarela da estação. Moradores relatam sensação de pânico e assaltos recorrentes à noite.",
    fotoUrl: "https://images.unsplash.com/photo-1780415493361-07c5a78dbaef?auto=format&fit=crop&w=800&q=80",
    apoiosCount: 45,
    iot: {
      device_id: "IOT-LUM-SP-789",
      device_type: "smart_luminaire_telemetry",
      data: { ambient_lux: 0.8, lamp_current_amperes: 0.0, luminaire_failed: true }
    }
  },
  arvore_fios: {
    titulo: "Galho de grande porte trincado encostando na rede de alta tensão",
    categoria: "Poda de Árvore",
    descricao: "Árvore alta estalando após vendaval. Galho pesado sobre os fios soltando faíscas perto da escola municipal.",
    fotoUrl: "https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?auto=format&fit=crop&w=800&q=80",
    apoiosCount: 52,
    iot: {
      device_id: "IOT-GRID-SP-304",
      device_type: "grid_power_monitor",
      data: { voltage_surge_detected: true, line_short_circuit_alert: true }
    }
  },
  entulho_calcada: {
    titulo: "Ponto viciado de entulho com sofás bloqueando calçada",
    categoria: "Entulho e Descarte Irregular",
    descricao: "Descarte criminoso de restos de obra e móveis. Cadeirantes e pedestres forçados a transitar pelo meio da rua entre carros.",
    fotoUrl: "https://images.unsplash.com/photo-1605600659908-0ef719419d41?auto=format&fit=crop&w=800&q=80",
    apoiosCount: 31,
    iot: null
  }
};

let cenarioAtivoIot = null;

function carregarCenario(chave) {
  const c = CENARIOS[chave];
  if (!c) return;

  document.getElementById("titulo").value = c.titulo;
  document.getElementById("categoria").value = c.categoria;
  document.getElementById("descricao").value = c.descricao;
  document.getElementById("fotoUrl").value = c.fotoUrl;
  document.getElementById("apoiosCount").value = c.apoiosCount;
  cenarioAtivoIot = c.iot;

  atualizarPreviewFoto();
}

function atualizarPreviewFoto() {
  const url = document.getElementById("fotoUrl").value;
  const img = document.getElementById("imgPreview");
  if (url && url.startsWith("http")) {
    img.src = url;
    img.style.display = "block";
  } else {
    img.style.display = "none";
  }
}

async function executarTriagem(e) {
  e.preventDefault();

  const submitBtn = document.getElementById("submitBtn");
  const loadingArea = document.getElementById("loadingArea");
  const resultsArea = document.getElementById("resultsArea");

  submitBtn.disabled = true;
  loadingArea.style.display = "block";

  const payload = {
    titulo: document.getElementById("titulo").value,
    categoria: document.getElementById("categoria").value,
    descricao: document.getElementById("descricao").value,
    fotoUrl: document.getElementById("fotoUrl").value || null,
    apoiosCount: parseInt(document.getElementById("apoiosCount").value, 10) || 0,
    localizacao: {
      logradouro: "Avenida Paulista",
      numero: "1578",
      bairro: "Bela Vista",
      cidade: "São Paulo",
      latitude: -23.5629,
      longitude: -46.6544
    },
    telemetriaIot: document.getElementById("simularIot").checked ? cenarioAtivoIot : null
  };

  try {
    const res = await fetch("/api/v1/triagem-ia/analisar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      throw new Error(`Erro na API (${res.status}): ${await res.text()}`);
    }

    const data = await res.json();
    renderizarResultados(data);
  } catch (err) {
    alert("Falha na execução da Triagem IA: " + err.message);
  } finally {
    submitBtn.disabled = false;
    loadingArea.style.display = "none";
  }
}

function renderizarResultados(data) {
  // 1. Banner Principal
  const badge = document.getElementById("badgePrioridade");
  badge.textContent = `Prioridade: ${data.prioridade}`;
  badge.className = "status-badge";
  const banner = document.getElementById("bannerLaudo");
  banner.className = "banner-laudo";

  if (data.prioridade === "Crítica") {
    badge.classList.add("badge-critica");
    banner.classList.add("critica");
  } else if (data.prioridade === "Alta") {
    badge.classList.add("badge-alta");
  } else if (data.prioridade === "Média") {
    badge.classList.add("badge-media");
  } else {
    badge.classList.add("badge-baixa");
  }

  document.getElementById("txtSla").textContent = `SLA Regulamentar: ${data.slaSugeridoHoras} Horas`;
  document.getElementById("txtOrgao").textContent = `Órgão Responsável: ${data.orgaoResponsavel}`;
  document.getElementById("txtParecer").textContent = data.parecerIa;
  document.getElementById("txtProvedor").textContent = data.provedorGenAi;

  // 2. Visão Computacional
  if (data.analiseVisual) {
    document.getElementById("cvCategoria").textContent = data.analiseVisual.categoriaDetectada;
    document.getElementById("cvConfianca").textContent = `${(data.analiseVisual.confiancaScore * 100).toFixed(1)}%`;
    document.getElementById("cvSeveridade").textContent = data.analiseVisual.severidadeVisual;

    const feats = data.analiseVisual.caracteristicasExtraidas || {};
    document.getElementById("cvBordas").textContent = feats.edge_density || "--";
    document.getElementById("cvRugosidade").textContent = feats.texture_roughness || "--";
  }

  // 3. RAG Normativo
  document.getElementById("ragEnquadramento").textContent = data.enquadramentoLegal;
  document.getElementById("ragRisco").textContent = data.riscoPotencial;

  const chunksArea = document.getElementById("ragChunksArea");
  chunksArea.innerHTML = "";
  if (data.evidenciasRag && data.evidenciasRag.length > 0) {
    data.evidenciasRag.forEach(c => {
      const d = document.createElement("div");
      d.className = "rag-chunk";
      d.innerHTML = `<div class="source">📌 ${c.artigoOuNorma} (${(c.similaridadeScore * 100).toFixed(0)}% match)</div><div>${c.trechoRelevante}</div>`;
      chunksArea.appendChild(d);
    });
  }

  // 4. IoT
  if (data.telemetriaIot) {
    document.getElementById("iotAtivo").textContent = data.telemetriaIot.sensorPresente ? "SIM (Conectado)" : "Não disponível";
    document.getElementById("iotTipo").textContent = data.telemetriaIot.tipoSensor || "N/A";
    document.getElementById("iotAnomalia").textContent = data.telemetriaIot.anomaliaDetectada ? "SIM (Crítica!)" : "Normal";
    const diag = (data.telemetriaIot.detalhesLeitura && data.telemetriaIot.detalhesLeitura.impact_diagnosis) || "Monitoramento regular";
    document.getElementById("iotDiagnostico").textContent = diag;
  }

  // 5. IoB
  if (data.analiseIob) {
    document.getElementById("iobScore").textContent = `${data.analiseIob.socialUrgencyScore} / 10.0`;
    document.getElementById("iobApoios").textContent = `${document.getElementById("apoiosCount").value} vizinhos`;
    document.getElementById("iobEngajamento").textContent = data.analiseIob.nivelEngajamento;
    document.getElementById("iobAjuste").textContent = data.analiseIob.ajustePrioridadeComunitario ? "Prioridade Elevada pela Vizinhança" : "Padrão";
  }

  // 6. Checklist
  const checkListArea = document.getElementById("checklistArea");
  checkListArea.innerHTML = "";
  if (data.checklistVistoria && data.checklistVistoria.length > 0) {
    data.checklistVistoria.forEach(item => {
      const li = document.createElement("li");
      li.textContent = item;
      checkListArea.appendChild(li);
    });
  }
}

// Inicializa com o primeiro cenário
window.addEventListener("DOMContentLoaded", () => {
  carregarCenario("buraco_critico");
});

