# Assistant & finale: the Copilot SDK step

← [Docs index](README.md) · [Workshop flow](workshop-flow.md)

Every track ends here (75–95 min). The **CPH Ops Assistant** is a chat drawer in the UI backed
by the GitHub Copilot SDK for Python. Each track gives it **one read-only tool**; together they
let it answer questions that span the whole airport.

## How it fits together

```
Chat drawer (src/frontend/tracks/assistant.js)
   │  POST /api/assistant/chat {message, session_id}
   ▼
FastAPI router (src/backend/app/routers/assistant.py)
   │  ask(message, session_id)
   ▼
copilot_agent.py ── one CopilotClient (started in the FastAPI lifespan)
   │                 one Copilot session per chat (system message: "CPH Ops Assistant")
   ▼
Tools from build_tools():  get_queue_forecast · get_flights · get_disruption_impact · get_bags_at_risk
   │
   ▼
Your plain Python functions → SQLite (synthetic data)
```

The SDK is **optional at start-up**: the app must keep running when the SDK, its runtime or a
Copilot sign-in is missing. Import it inside functions and catch start-up errors.

## Before you start

- Run `python src/scripts/check_env.py`: the last check starts a Copilot client and sends a
  trivial prompt. If it fails, sign in to GitHub in VS Code, the GitHub Copilot app or the
  Copilot CLI (or set `GH_TOKEN`), and check your Copilot licence and proxy.
- Read the [`copilot-sdk-tool` skill](../.github/skills/copilot-sdk-tool/SKILL.md), the
  [`copilot-sdk-python` instructions](../.github/instructions/copilot-sdk-python.instructions.md)
  (note the repo note at the top) and the official SDK README:
  https://github.com/github/copilot-sdk/tree/main/python (moving to
  https://github.com/microsoft/copilot-sdk). This repo pins **`github-copilot-sdk==1.0.34`**
  (public preview). The SDK is being renamed to `microsoft-copilot-sdk` (2.x) with a different
  API; don't upgrade during the hack.

## Step A · Wire the shared client (one person per room or team)

File: `src/backend/app/assistant/copilot_agent.py`, then `src/backend/app/main.py` and
`src/backend/app/routers/assistant.py`.

1. 💬 "Implement TODO 1 in copilot_agent.py: start_client() and stop_client() with the pinned github-copilot-sdk 1.0.34 API from the official README. If starting fails, log a warning and leave the client unset."
2. 💬 "Call start_client() and stop_client() from the FastAPI lifespan in main.py so the app still starts without the SDK, and make /api/health report copilot_sdk 'ready' when the client started."
3. 💬 "Implement TODO 2 and TODO 4 in copilot_agent.py: ask(message, session_id) creates or reuses a session with SYSTEM_MESSAGE and build_tools(), uses a permission handler that only approves our own tools, and returns the reply text and session id."
4. 💬 "Wire POST /api/assistant/chat to ask(). Return 400 for an empty message and 503 when the client isn't running."

💡 The chat drawer probes the endpoint with an **empty message** on page load: the stub
answers 501, so the drawer stays off. Once you return **400** for an empty message, the drawer
switches on automatically. Only 2xx, 400 or 422 switch it on; 503 (client not running) and
other errors keep it off. Never auto-approve shell or file-write tools for a chat assistant.

✅ Reload the page: the drawer says "Assistant connected". Asking "What can you do?" returns a reply.

## Step B · Add your track's tool (every track)

| Track | Tool | Returns |
|---|---|---|
| [Passenger onboarding](track-1-passenger-onboarding.md) | `get_queue_forecast` | Forecast wait per slot and the expected peak |
| [Flight plans](track-2-flight-plans.md) | `get_flights` | Flights by direction, time window and status |
| [Disruptions](track-3-disruptions.md) | `get_disruption_impact` | A disruption with affected flights and connections |
| [Gates & baggage](track-4-gates-and-baggage.md) | `get_bags_at_risk` | Transfer bags at risk with flights and connection minutes |

💬 "Use the copilot-sdk-tool skill to expose `<function>` as the read-only Copilot SDK tool `<tool_name>` and register it in build_tools()."

💡 Reuse the plain function behind your endpoint so the tool and the API always agree. Keep
results small (≤ 50 rows) and in Copenhagen local time. Cross-track helper tools mentioned in
`copilot_agent.py` (`get_flights_at_risk`, `get_active_disruptions`, `get_pax_connections`) are
good stretch goals.

✅ The assistant answers a question about your track and the answer matches your endpoint.

## Cross-track finale

With several tracks' tools registered, ask the assistant a question that spans them:

> **"If Frankfurt closes for 2 hours, which departures, stands and transfer bags are affected, and what should we do?"**

A good answer combines `get_disruption_impact` (or a what-if disruption), `get_flights`,
`get_bags_at_risk` and stand information, and ends with concrete actions (rebook, notify,
reassign stands). Stretch: let it propose `REBOOK` / `NOTIFY` / `REASSIGN_STAND` actions for
`automation_queue` (a human confirms; see [uipath-handoff.md](uipath-handoff.md)).

More finale questions:
- "What's the riskiest hour this afternoon for passengers connecting through CPH?"
- "Should we open another security lane in T3 before the evening peak? Why?"

## `HACK(assistant)` markers

| File | Marker (what to build) |
|---|---|
| `src/backend/app/assistant/copilot_agent.py` | TODO 1: start the client (plus its `NotImplementedError` message) |
| `src/backend/app/assistant/copilot_agent.py` | `stop_client`: disconnect sessions, then stop the client |
| `src/backend/app/assistant/copilot_agent.py` | TODO 3: register tools (`build_tools`) |
| `src/backend/app/assistant/copilot_agent.py` | TODO 2: create or reuse a session with the system message |
| `src/backend/app/assistant/copilot_agent.py` | TODO 4: collect (or stream) the reply (plus its `NotImplementedError` message) |
| `src/backend/app/main.py` | start the Copilot SDK client in the lifespan |
| `src/backend/app/main.py` | report "ready" in `/api/health` once the client has started |
| `src/backend/app/routers/assistant.py` | call `copilot_agent.ask(...)` and return the reply (and its 501 detail) |
| `src/frontend/index.html` | "Assistant not connected yet – HACK(assistant)" status text in the chat drawer |
