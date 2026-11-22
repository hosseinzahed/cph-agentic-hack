"""CPH Ops Assistant: Copilot SDK skeleton (NOT wired up yet).

The plan
--------
1. One ``CopilotClient`` is started once, when the app starts, from the FastAPI
   ``lifespan`` in ``backend/app/main.py`` (``start_client``) and stopped on shutdown.
2. Each chat conversation gets its own Copilot *session*. ``POST /api/assistant/chat``
   calls ``ask(message, session_id)``; the session id is returned to the UI so the next
   message continues the same conversation.
3. Each track exposes one read-only app function as a Copilot SDK *tool* (for example
   ``get_flights_at_risk``, ``get_active_disruptions`` or ``get_pax_connections``). The
   model calls these tools to answer questions about CPH operations.

Rules
-----
* The SDK is **optional at start-up**. Import it lazily inside functions so the app runs
  even when the SDK, the runtime or a Copilot sign-in is missing.
* Pinned package: ``github-copilot-sdk==1.0.34`` (public preview). Use ONLY the API in the
  official README for that version: https://github.com/github/copilot-sdk/tree/main/python
  (now hosted at https://github.com/microsoft/copilot-sdk), plus the repo's
  ``.github/instructions/copilot-sdk-python.instructions.md`` and the
  ``.github/skills/copilot-sdk-tool`` skill.
* Tools must be read-only and must never return personal data. All data is synthetic.

Guide: docs/assistant-and-finale.md
"""

from __future__ import annotations

import importlib.util
from typing import Any

SYSTEM_MESSAGE = """\
You are the CPH Ops Assistant, an operations co-pilot for Copenhagen Airport (CPH).
You help duty managers understand flights, passenger queues, disruptions, stands and
transfer baggage. Use the provided tools for facts; never invent flight data. Answer
briefly, use local Copenhagen time, and say which tool your answer is based on.
All data in this system is synthetic workshop data."""

_client: Any | None = None  # the running CopilotClient, once started
_sessions: dict[str, Any] = {}  # chat session id -> Copilot session


def sdk_installed() -> bool:
    """Return True when the ``copilot`` package can be imported (no runtime check)."""
    return importlib.util.find_spec("copilot") is not None


async def start_client() -> None:
    """Start the shared Copilot client. Call once from the FastAPI lifespan."""
    # HACK(assistant): TODO 1 - start the client.
    #   from copilot import CopilotClient
    #   global _client
    #   _client = CopilotClient()          # uses your signed-in GitHub/Copilot user
    #   await _client.start()
    #   Wrap it in try/except: log a warning and leave _client = None if it fails,
    #   so the rest of the app keeps working without the assistant.
    raise NotImplementedError("HACK(assistant): start the Copilot client")


async def stop_client() -> None:
    """Stop the shared Copilot client on shutdown (safe to call when it never started)."""
    # HACK(assistant): disconnect sessions in _sessions, then `await _client.stop()`.
    return None


def build_tools() -> list[Any]:
    """Return the Copilot SDK tools exposed to the assistant. Empty until tracks add theirs."""
    # HACK(assistant): TODO 3 - register tools. Each track adds ONE read-only tool, e.g.:
    #   from copilot import define_tool
    #   from pydantic import BaseModel, Field
    #
    #   class FlightsAtRiskParams(BaseModel):            # define at module level
    #       hours: int = Field(default=2, description="Look-ahead window in hours")
    #
    #   @define_tool(description="List CPH flights at risk of delay in the next hours",
    #                skip_permission=True)               # OK for read-only tools only
    #   async def get_flights_at_risk(params: FlightsAtRiskParams) -> str:
    #       ...query the DB, return compact JSON text...
    #
    #   Planned tools: get_queue_forecast (onboarding), get_flights (flights),
    #   get_disruption_impact (disruptions), get_bags_at_risk (gates), plus cross-track
    #   helpers such as get_flights_at_risk, get_active_disruptions, get_pax_connections.
    return []


async def ask(message: str, session_id: str | None = None) -> tuple[str, str]:
    """Send ``message`` to the assistant and return ``(reply_text, session_id)``."""
    # HACK(assistant): TODO 2 - create (or reuse) a session with the system message:
    #   session = await _client.create_session(
    #       on_permission_request=<a handler that only approves your own tools>,
    #       model=os.environ.get("COPILOT_MODEL") or None,   # optional, see .env.example
    #       system_message={"mode": "append", "content": SYSTEM_MESSAGE},
    #       tools=build_tools(),
    #   )
    #   Keep it in _sessions under a new id (uuid4) when session_id is None.
    #   Never auto-approve built-in shell or file-write tools for a chat assistant.
    #
    # HACK(assistant): TODO 4 - collect (or stream) the reply:
    #   event = await session.send_and_wait(message, timeout=60)
    #   reply = event.data.content if event else "(no reply)"
    #   For streaming, pass streaming=True to create_session and handle
    #   assistant.message_delta events via session.on(...) - see the SDK README.
    raise NotImplementedError("HACK(assistant): send the message through a Copilot session")
