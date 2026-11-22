// CPH Ops Assistant chat drawer. Guide: docs/assistant-and-finale.md
//
// The drawer stays disabled while POST /api/assistant/chat returns 501. On page load it
// sends an EMPTY message as a probe: the stub answers 501, a real implementation should
// answer 400/422 for an empty message (or 200), and any non-501 answer switches the chat on.
import { api } from "../app.js";

let sessionId = null;

export function initAssistant() {
  const drawer = document.getElementById("chat-drawer");
  const toggle = document.getElementById("chat-toggle");
  const close = document.getElementById("chat-close");
  const form = document.getElementById("chat-form");
  const input = document.getElementById("chat-input");

  const setOpen = (open) => {
    drawer.hidden = !open;
    toggle.setAttribute("aria-expanded", String(open));
    if (!open) toggle.focus();
    else if (input.disabled) close.focus();
    else input.focus();
  };
  toggle.addEventListener("click", () => setOpen(drawer.hidden));
  close.addEventListener("click", () => setOpen(false));
  drawer.addEventListener("keydown", (event) => {
    if (event.key === "Escape") setOpen(false);
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const message = input.value.trim();
    if (!message) return;
    input.value = "";
    addMessage("user", message);
    try {
      const reply = await api("/api/assistant/chat", { method: "POST", body: { message, session_id: sessionId } });
      sessionId = reply.session_id;
      addMessage("assistant", reply.reply);
    } catch (error) {
      addMessage("assistant", `Sorry, something went wrong: ${error.message}`);
    }
  });

  probe();
}

async function probe() {
  try {
    await api("/api/assistant/chat", { method: "POST", body: { message: "" } });
    enable();
  } catch (error) {
    if (error.status && error.status !== 501) enable();
  }
}

function enable() {
  document.getElementById("chat-input").disabled = false;
  document.getElementById("chat-send").disabled = false;
  document.getElementById("chat-status").textContent = "Assistant connected. Ask about today's operations.";
}

/** Append a chat bubble. Uses textContent so model output can never inject HTML. */
function addMessage(role, text) {
  const bubble = document.createElement("p");
  bubble.className = `msg msg--${role}`;
  bubble.textContent = text;
  const log = document.getElementById("chat-log");
  log.append(bubble);
  log.scrollTop = log.scrollHeight;
}
