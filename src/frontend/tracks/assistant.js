// CPH Ops Assistant chat drawer. Guide: docs/assistant-and-finale.md
//
// The drawer stays disabled until POST /api/assistant/chat is implemented. On page load it
// sends an EMPTY message as a probe: the stub answers 501, a real implementation answers
// 400/422 for an empty message (or 2xx). Only those answers switch the chat on; 501, 503
// (SDK client not running), 401, 404, 500 and network errors leave it off.
import { api } from "../app.js";

let sessionId = null;
let pending = false;

export function initAssistant() {
  const drawer = document.getElementById("chat-drawer");
  const toggle = document.getElementById("chat-toggle");
  const close = document.getElementById("chat-close");
  const form = document.getElementById("chat-form");
  const input = document.getElementById("chat-input");
  const send = document.getElementById("chat-send");

  // Native modal dialog: the browser traps focus, makes the page inert and closes on Escape.
  toggle.addEventListener("click", () => {
    drawer.showModal();
    toggle.setAttribute("aria-expanded", "true");
    (input.disabled ? close : input).focus();
  });
  close.addEventListener("click", () => drawer.close());
  drawer.addEventListener("click", (event) => {
    if (event.target === drawer) drawer.close(); // a click on the backdrop
  });
  drawer.addEventListener("close", () => {
    toggle.setAttribute("aria-expanded", "false");
    toggle.focus();
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const message = input.value.trim();
    if (!message || pending) return;
    pending = true;
    send.disabled = true;
    input.value = "";
    addMessage("user", message);
    try {
      const reply = await api("/api/assistant/chat", { method: "POST", body: { message, session_id: sessionId } });
      sessionId = reply.session_id;
      addMessage("assistant", reply.reply);
    } catch (error) {
      addMessage("assistant", `Sorry, something went wrong: ${error.message}`);
    } finally {
      pending = false;
      send.disabled = false;
    }
  });

  probe();
}

async function probe() {
  try {
    await api("/api/assistant/chat", { method: "POST", body: { message: "" } });
    enable();
  } catch (error) {
    if (error.status === 400 || error.status === 422) enable();
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
