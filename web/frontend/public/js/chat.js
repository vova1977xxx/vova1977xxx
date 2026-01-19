(function () {
  const out = document.getElementById("chatOut");
  const inp = document.getElementById("chatIn");
  const sendBtn = document.getElementById("sendBtn");
  const clearBtn = document.getElementById("clearBtn");
  const statusEl = document.getElementById("chatStatus");

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, (m) => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#039;",
    }[m]));
  }

  function addMsg(role, text) {
    const box = document.createElement("div");
    box.className = "neon-card";
    box.innerHTML =
      `<div class="neon-title" style="font-size:12px">${role}</div>` +
      `<div class="neon-subtitle" style="white-space:pre-wrap;margin-top:6px">${escapeHtml(text)}</div>`;
    out.appendChild(box);
    window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });
  }

  async function send() {
    const msg = (inp.value || "").trim();
    if (!msg) return;

    addMsg("YOU", msg);
    inp.value = "";
    statusEl.textContent = "⏳ thinking...";

    try {
      const r = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ role: "user_chat", prompt: msg }),
      });

      if (!r.ok) {
        const t = await r.text();
        throw new Error("HTTP " + r.status + " " + t);
      }

      const j = await r.json();
      const answer = j.answer || j.text || j.response || JSON.stringify(j);

      addMsg("GEMIVAS", answer);
      statusEl.textContent = "✅ done";
    } catch (e) {
      addMsg("ERROR", String(e));
      statusEl.textContent = "❌ error";
    }
  }

  sendBtn.addEventListener("click", send);
  clearBtn.addEventListener("click", () => { out.innerHTML = ""; statusEl.textContent = ""; });

  inp.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  });
})();
