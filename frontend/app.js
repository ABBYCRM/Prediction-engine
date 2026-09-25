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
    const r = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    });
    const j = await r.json();
    addBubble("engine", j.answer || j.error || "no answer");
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

refreshHealth();
