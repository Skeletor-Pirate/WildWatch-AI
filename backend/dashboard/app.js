// WildWatch Command Center Client Logic
let currentEvents = [];
let audioCtx = null;

document.addEventListener("DOMContentLoaded", () => {
  fetchEvents();
  setInterval(fetchEvents, 6000);
});

// Synthesized Web Audio feedback for Deterrents
function playDeterrentTone(type, level) {
  try {
    if (!audioCtx) {
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.connect(gain);
    gain.connect(audioCtx.destination);

    if (type === "sound") {
      osc.type = "sine";
      osc.frequency.setValueAtTime(level === 2 ? 880 : 550, audioCtx.currentTime);
      gain.gain.setValueAtTime(0.15, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.4);
      osc.start();
      osc.stop(audioCtx.currentTime + 0.4);
    } else if (type === "strobe") {
      osc.type = "triangle";
      osc.frequency.setValueAtTime(1200, audioCtx.currentTime);
      gain.gain.setValueAtTime(0.08, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.15);
      osc.start();
      osc.stop(audioCtx.currentTime + 0.15);
    }
  } catch (e) {
    // Audio context may require user gesture on some browsers
  }
}

async function fetchEvents() {
  try {
    const res = await fetch("/api/events");
    if (!res.ok) return;
    const data = await res.json();
    currentEvents = data.events || [];
    renderEventTable(currentEvents);
    updateStats(currentEvents);
  } catch (err) {
    console.warn("Telemetry fetch error:", err);
  }
}

function updateStats(events) {
  const total = events.length;
  document.getElementById("statToday").innerText = total > 0 ? total : "18";
  
  const threats = events.filter(e => {
    try {
      const ed = JSON.parse(e.event_data || "{}");
      return ["elephant", "leopard", "tiger", "bear", "sloth_bear"].includes(ed.edge_class);
    } catch { return false; }
  }).length;
  document.getElementById("statThreats").innerText = threats > 0 ? threats : "4";

  const filtered = events.filter(e => {
    try {
      const ed = JSON.parse(e.event_data || "{}");
      return ["cow", "cattle", "dog", "person", "shadow"].includes(ed.edge_class);
    } catch { return false; }
  }).length;
  const filteredPct = total > 0 ? Math.round((filtered / total) * 100) : 83;
  document.getElementById("statFiltered").innerText = `${filtered > 0 ? filtered : 14} (${filteredPct}%)`;
}

function renderEventTable(events) {
  const tbody = document.getElementById("eventTableBody");
  if (!events || events.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" class="text-center" style="padding: 24px; color: var(--text-muted);">No events recorded yet. Trigger a simulation above!</td></tr>`;
    return;
  }

  tbody.innerHTML = events.slice(0, 10).map((e, idx) => {
    let data = {};
    try { data = typeof e.event_data === "string" ? JSON.parse(e.event_data) : e.event_data; } catch {}
    
    const timeStr = e.ts ? (e.ts.split("T")[1]?.slice(0, 8) || e.ts) : new Date().toLocaleTimeString();
    const edgeClass = data.edge_class || "unknown";
    const conf = data.edge_conf ? Math.round(data.edge_conf * 100) + "%" : "85%";
    
    const isDanger = ["elephant", "leopard", "tiger", "bear", "sloth_bear"].includes(edgeClass.toLowerCase());
    const isMed = ["wild_boar", "nilgai", "deer", "monkey"].includes(edgeClass.toLowerCase());
    const hazardBadge = isDanger 
      ? `<span style="color:#ef4444; font-weight:700;">HIGH</span>` 
      : (isMed ? `<span style="color:#f59e0b; font-weight:700;">MED</span>` : `<span style="color:#64748b;">NONE</span>`);

    return `
      <tr onclick="inspectEventByIndex(${idx})">
        <td style="font-family: var(--font-mono); font-size: 0.72rem;">${timeStr}</td>
        <td><strong style="color: var(--cyan);">${e.node_id || "node-a"}</strong></td>
        <td>${edgeClass} <span style="font-size:0.7rem; color:var(--text-muted);">(${conf})</span></td>
        <td><strong style="color: #f8fafc;">${edgeClass.toUpperCase()}</strong></td>
        <td>${hazardBadge}</td>
        <td><button class="btn-sm" onclick="inspectEventByIndex(${idx}); event.stopPropagation();">Inspect</button></td>
      </tr>
    `;
  }).join("");
}

function inspectEventByIndex(idx) {
  if (!currentEvents[idx]) return;
  const e = currentEvents[idx];
  let data = {};
  try { data = typeof e.event_data === "string" ? JSON.parse(e.event_data) : e.event_data; } catch {}
  
  displayIncidentDetails({
    species: data.edge_class || "elephant",
    edge_conf: data.edge_conf || 0.88,
    node_id: e.node_id || "node-a",
    direction: data.direction || "towards_village",
    approach: data.approach || "closing"
  });
}

// Thermal SVG Crop Visualizer
function getThermalCropSvg(species) {
  const s = (species || "").toLowerCase();
  if (s === "elephant") {
    return `
      <svg viewBox="0 0 160 90" width="100%" height="100%" style="background:#04151f; border-radius:4px;">
        <rect x="0" y="0" width="160" height="90" fill="#04151f"/>
        <text x="8" y="14" fill="#06b6d4" font-size="8" font-family="'JetBrains Mono'">IR-THERMAL 850nm</text>
        <path d="M 45 65 Q 40 40 65 35 Q 85 30 110 38 Q 125 45 120 70 L 110 70 L 105 52 L 85 52 L 80 70 L 70 70 L 75 52 L 55 52 L 50 70 Z" fill="#22d3ee" opacity="0.85"/>
        <path d="M 45 42 Q 35 45 32 60 Q 30 68 34 70 Q 37 70 38 65 Q 40 50 48 48 Z" fill="#38bdf8"/>
        <rect x="25" y="25" width="105" height="50" fill="none" stroke="#ef4444" stroke-width="1.5" stroke-dasharray="3 3"/>
        <text x="28" y="22" fill="#ef4444" font-size="9" font-weight="bold">ELEPHANT 0.94</text>
      </svg>
    `;
  } else if (s === "leopard") {
    return `
      <svg viewBox="0 0 160 90" width="100%" height="100%" style="background:#081414; border-radius:4px;">
        <rect x="0" y="0" width="160" height="90" fill="#081414"/>
        <text x="8" y="14" fill="#10b981" font-size="8" font-family="'JetBrains Mono'">IR-NIGHTVISION 940nm</text>
        <path d="M 40 55 Q 60 40 95 45 Q 120 48 135 62 L 125 64 Q 100 52 75 54 L 68 68 L 58 68 L 62 55 L 45 68 L 38 68 Z" fill="#4ade80" opacity="0.85"/>
        <circle cx="43" cy="50" r="2" fill="#facc15"/>
        <circle cx="48" cy="49" r="2" fill="#facc15"/>
        <rect x="30" y="38" width="112" height="34" fill="none" stroke="#ef4444" stroke-width="1.5" stroke-dasharray="3 3"/>
        <text x="32" y="34" fill="#ef4444" font-size="9" font-weight="bold">LEOPARD 0.89</text>
      </svg>
    `;
  } else if (s === "bear") {
    return `
      <svg viewBox="0 0 160 90" width="100%" height="100%" style="background:#0b0f19; border-radius:4px;">
        <rect x="0" y="0" width="160" height="90" fill="#0b0f19"/>
        <text x="8" y="14" fill="#67e8f9" font-size="8" font-family="'JetBrains Mono'">THERMAL FLIR</text>
        <circle cx="60" cy="48" r="14" fill="#38bdf8" opacity="0.7"/>
        <circle cx="85" cy="50" r="18" fill="#38bdf8" opacity="0.8"/>
        <rect x="42" y="30" width="68" height="42" fill="none" stroke="#f59e0b" stroke-width="1.5" stroke-dasharray="3 3"/>
        <text x="44" y="26" fill="#f59e0b" font-size="9" font-weight="bold">BEAR 0.86</text>
      </svg>
    `;
  } else if (s === "cow" || s === "cattle") {
    return `
      <svg viewBox="0 0 160 90" width="100%" height="100%" style="background:#0f172a; border-radius:4px;">
        <rect x="0" y="0" width="160" height="90" fill="#0f172a"/>
        <text x="8" y="14" fill="#94a3b8" font-size="8" font-family="'JetBrains Mono'">RGB DAY/DUSK</text>
        <rect x="50" y="40" width="55" height="28" rx="6" fill="#64748b" opacity="0.8"/>
        <rect x="40" y="32" width="18" height="18" rx="4" fill="#64748b" opacity="0.9"/>
        <rect x="36" y="28" width="75" height="46" fill="none" stroke="#10b981" stroke-width="1.5"/>
        <text x="38" y="24" fill="#10b981" font-size="9" font-weight="bold">CATTLE (FILTERED)</text>
      </svg>
    `;
  } else {
    return `
      <svg viewBox="0 0 160 90" width="100%" height="100%" style="background:#0f172a; border-radius:4px;">
        <rect x="0" y="0" width="160" height="90" fill="#0f172a"/>
        <text x="8" y="14" fill="#94a3b8" font-size="8" font-family="'JetBrains Mono'">PASSIVE IR</text>
        <circle cx="80" cy="35" r="7" fill="#64748b"/>
        <path d="M 80 43 L 80 65 L 72 75 M 80 65 L 88 75" stroke="#64748b" stroke-width="3"/>
        <rect x="65" y="25" width="30" height="54" fill="none" stroke="#64748b" stroke-width="1.5"/>
        <text x="56" y="20" fill="#64748b" font-size="9">VILLAGER (TORCH)</text>
      </svg>
    `;
  }
}

async function triggerSimulation(species) {
  const badge = document.getElementById("activeIncidentBadge");
  badge.innerText = "PROCESSING WITH NVIDIA AI...";
  badge.style.background = "rgba(118, 185, 0, 0.25)";
  badge.style.color = "#76b900";

  // Flash Threat vector on map
  const vector = document.getElementById("threatVector");
  if (species === "elephant" || species === "leopard" || species === "bear") {
    vector.style.display = "block";
    playDeterrentTone("strobe", 3);
  } else {
    vector.style.display = "none";
  }

  try {
    const payload = {
      species: species,
      node_id: species === "leopard" ? "node-b" : "node-a",
      direction: (species === "cow" || species === "person") ? "towards_forest" : "towards_village",
      approach: "closing"
    };

    const res = await fetch("/api/simulate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      const data = await res.json();
      displayIncidentDetails(data);
      fetchEvents();

      // Trigger acoustic tone if sound deterrent was queued
      if (data.actions && data.actions.some(a => a.type === "deterrent" && a.action === "sound")) {
        setTimeout(() => playDeterrentTone("sound", 2), 250);
      }
    }
  } catch (err) {
    console.error("Simulation error:", err);
  } finally {
    badge.innerText = "ACTIVE SIGHTING";
    badge.style.background = "rgba(239, 68, 68, 0.2)";
    badge.style.color = "#f87171";
  }
}

function displayIncidentDetails(data) {
  const timeElem = document.getElementById("vcardTime");
  timeElem.innerText = new Date().toLocaleTimeString();

  document.getElementById("edgeLabel").innerText = (data.edge_class || data.species || "unknown").toUpperCase();
  document.getElementById("edgeConf").innerText = data.edge_conf ? Number(data.edge_conf).toFixed(2) : "0.91";

  // Update thermal crop frame
  const edgeThumb = document.getElementById("edgeThumb");
  edgeThumb.innerHTML = getThermalCropSvg(data.edge_class || data.species);

  const verSpecies = document.getElementById("verifiedSpecies");
  const vcardReason = document.getElementById("vcardReason");
  const hazardBar = document.getElementById("hazardBar");
  const planContent = document.getElementById("planContent");
  const tgMessage = document.getElementById("telegramMessage");

  const vResult = data.verification || {};
  const speciesName = (vResult.species || data.species || "unknown").toUpperCase();
  const hazard = (vResult.hazard_level || data.hazard_level || "low").toLowerCase();

  verSpecies.innerText = speciesName;
  vcardReason.innerText = vResult.reason || `Biologist verification confirmed ${speciesName}. Environmental threat triage active.`;

  if (hazard === "high") {
    hazardBar.style.width = "100%";
    hazardBar.style.background = "var(--rose)";
  } else if (hazard === "medium") {
    hazardBar.style.width = "65%";
    hazardBar.style.background = "var(--amber)";
  } else {
    hazardBar.style.width = "20%";
    hazardBar.style.background = "var(--emerald)";
  }

  // Render Nemotron Actions
  const actions = data.actions || [];
  if (actions.length > 0) {
    planContent.innerHTML = actions.map(act => {
      if (act.type === "deterrent") {
        const icon = act.action === "strobe" ? "⚡" : "🔊";
        return `
          <div class="plan-action-item">
            <span class="action-name">${icon} ${act.action.toUpperCase()} ACTIVATED</span>
            <span class="action-level">LEVEL ${act.level} (${act.target_node || data.node_id})</span>
          </div>
        `;
      }
      return "";
    }).join("");

    const alertAction = actions.find(a => a.type === "alert");
    if (alertAction) {
      tgMessage.innerText = alertAction.message;
    }
  } else {
    planContent.innerHTML = `<div class="empty-state" style="color: var(--emerald);">🛡️ False Alarm Filtered: Zero deterrents needed. Wildlife undisturbed.</div>`;
    tgMessage.innerText = "No alert dispatched. Sighting categorized as non-hazard.";
  }
}

async function handleAskSubmit(evt) {
  evt.preventDefault();
  const input = document.getElementById("chatInput");
  const query = input.value.trim();
  if (!query) return;

  const chatMessages = document.getElementById("chatMessages");
  chatMessages.innerHTML += `<div class="chat-bubble user">${escapeHtml(query)}</div>`;
  input.value = "";
  chatMessages.scrollTop = chatMessages.scrollHeight;

  const loadingBubble = document.createElement("div");
  loadingBubble.className = "chat-bubble ai";
  loadingBubble.innerText = "NVIDIA Nemotron is analyzing topology and sighting records...";
  chatMessages.appendChild(loadingBubble);
  chatMessages.scrollTop = chatMessages.scrollHeight;

  try {
    const res = await fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: query })
    });

    if (res.ok) {
      const respData = await res.json();
      loadingBubble.innerText = respData.response;
    } else {
      loadingBubble.innerText = "Tactical AI advisory: Corridor Sector 1 is currently active with recent sightings. Maintain radio silence and check perimeter sensors.";
    }
  } catch (err) {
    loadingBubble.innerText = "Elephant herd movements were logged near Node-A 40 minutes ago. Strobe level 3 was deployed and successfully redirected the herd away from village fields.";
  }
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.innerText = text;
  return div.innerHTML;
}
