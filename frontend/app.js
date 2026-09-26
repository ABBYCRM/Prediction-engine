const transcript = document.getElementById("transcript");
const form = document.getElementById("composer");
const queryEl = document.getElementById("query");
const statusEl = document.getElementById("status");
const healthEl = document.getElementById("health");

function addBubble(role, text) {
  const div = document.createElement("div");
  div.className = `bubble ${role}`;
  div.textContent = text;
  transcript.appendChild(div);
  transcript.scrollTop = transcript.scrollHeight;
}

async function refreshHealth() {
  try {
    const r = await fetch("/health");
    const j = await r.json();
    const xai = j.xai_available ? "xai-on" : "xai-off";
    healthEl.textContent = j.ok ? `healthy · ${xai}` : "down";
    healthEl.classList.toggle("ok", !!j.ok);
  } catch {
    healthEl.textContent = "unreachable";
  }
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const query = queryEl.value.trim();
  if (!query) return;
  addBubble("user", query);
  queryEl.value = "";
  statusEl.textContent = "thinking…";
  try {
    const house = (document.getElementById("house") || {}).value || "";
    const r = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, house: house || undefined }),
    });
    const j = await r.json();
    const raw = j.answer || j.error || "no answer";
    const labeled = raw.startsWith("[prediction]") ? raw : `[prediction] ${raw}`;
    addBubble("engine", labeled);
  } catch (err) {
    addBubble("engine", String(err));
  } finally {
    statusEl.textContent = "";
  }
});

queryEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    form.requestSubmit();
  }
});

document.getElementById("facts").addEventListener("click", async () => {
  const r = await fetch("/facts");
  const j = await r.json();
  const lines = (j.facts || []).map((f) => `${f.id}: ${f.title}`).join("\n");
  addBubble("engine", `Playbook index (${j.count})\n${lines}`);
});

const contractsBtn = document.getElementById("contracts");
if (contractsBtn) {
  contractsBtn.addEventListener("click", async () => {
    const r = await fetch("/contracts");
    const j = await r.json();
    const lines = (j.contracts || [])
      .map((c) => `${c.id}: ${c.product} (${(c.fields || []).length} fields)`)
      .join("\n");
    addBubble("engine", `Portable contracts (${j.count})\n${lines}`);
  });
}

const analogsBtn = document.getElementById("analogs");
if (analogsBtn) {
  analogsBtn.addEventListener("click", async () => {
    const house = (document.getElementById("house") || {}).value || "";
    const qs = house ? `?house=${encodeURIComponent(house)}` : "";
    const r = await fetch(`/analogs${qs}`);
    const j = await r.json();
    const lines = (j.hits || [])
      .map((h) => `${h.ts || ""} house=${h.house || "-"} n=${(h.hits || []).length}`)
      .join("\n");
    addBubble("engine", `Analog log (${j.count})\n${lines || "(empty)"}`);
  });
}

const pubsBtn = document.getElementById("publishers");
if (pubsBtn) {
  pubsBtn.addEventListener("click", async () => {
    const r = await fetch("/publishers");
    const j = await r.json();
    addBubble("engine", `Publishers live_fetch=${j.live_fetch}\n${(j.hosts || []).join("\n")}`);
  });
}

refreshHealth();
