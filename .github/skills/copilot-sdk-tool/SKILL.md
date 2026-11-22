---
name: copilot-sdk-tool
description: Expose a backend function as a GitHub Copilot SDK tool for the CPH Ops Assistant - name, description, JSON-schema parameters via Pydantic, safe read-only defaults, registration in copilot_agent.py and testing. Use in the assistant step of any track or when wiring POST /api/assistant/chat.
---

# Copilot SDK tool

Each track exposes **one read-only function** as a tool so the CPH Ops Assistant can answer
questions with real (synthetic) data. Tools are registered in
`src/backend/app/assistant/copilot_agent.py` (`build_tools()`).

> **Exact API:** this repo pins `github-copilot-sdk==1.0.34` (public preview). Check the
> official README before writing SDK calls: https://github.com/github/copilot-sdk/tree/main/python
> (moving to https://github.com/microsoft/copilot-sdk), plus the awesome-copilot cookbook
> https://github.com/github/awesome-copilot/tree/main/cookbook/copilot-sdk/python and
> `.github/instructions/copilot-sdk-python.instructions.md`. Don't guess method names.

## 1. Start from a plain function
Put the logic in a normal, testable function (e.g. in your router module or a small
`services` function), returning plain data:

```python
def bags_at_risk(session: Session, limit: int = 20) -> list[dict]:
    ...  # SQLModel query, returns aggregated, synthetic, non-personal fields
```

## 2. Design the tool
| Part | Guidance |
|---|---|
| **Name** | `snake_case` verb phrase from your track guide: `get_queue_forecast`, `get_flights`, `get_disruption_impact`, `get_bags_at_risk`. |
| **Description** | One or two sentences: what it returns, units, time zone, when to use it. The model chooses tools from this text. |
| **Parameters** | A Pydantic model; every field has a type, a default where sensible and a `Field(description=...)`. Use enums/`Literal` for fixed values and bounds (`ge`, `le`) for numbers. This becomes the JSON schema. |
| **Result** | Compact JSON text (`json.dumps(..., default=str)`), at most ~50 rows. Include units and local CPH times. |
| **Safety** | Read-only. No personal data. Validate inputs. Catch errors and return a short message instead of raising. |

## 3. Define it with the SDK (1.0.34 API)

```python
import json
from pydantic import BaseModel, Field
from copilot import define_tool          # import inside build_tools() to keep the SDK optional
from sqlmodel import Session
from backend.app.db import engine


class BagsAtRiskParams(BaseModel):       # module level (required with `from __future__ import annotations`)
    limit: int = Field(default=20, ge=1, le=50, description="Maximum number of bags to return")


@define_tool(
    name="get_bags_at_risk",
    description="List CPH transfer bags at risk of missing their connection today (synthetic data). "
                "Times are Europe/Copenhagen.",
    skip_permission=True,                # OK only because the tool is read-only
)
async def get_bags_at_risk(params: BagsAtRiskParams) -> str:
    with Session(engine) as session:
        return json.dumps(bags_at_risk(session, params.limit), default=str)
```

Return it from `build_tools()` and pass the list to `client.create_session(..., tools=build_tools())`.

## 4. Safe session defaults
- Use a permission handler that **rejects** anything except your own tools; never
  `PermissionHandler.approve_all` for the chat assistant (it could run shell or file tools).
- Add a `system_message={"mode": "append", "content": SYSTEM_MESSAGE}` describing the CPH Ops
  Assistant (already in `copilot_agent.py`).
- Start the client once in the FastAPI lifespan; if it fails, log a warning and keep the app up.

## 5. Test it
1. **Unit-test the plain function** with pytest (`src/backend/tests/`), using the seeded test DB.
2. **Test the registration**: assert that `build_tools()` contains a tool whose `.name` is
   `get_bags_at_risk` and whose `.parameters` (the generated JSON schema) has the fields you expect.
   This needs the SDK installed but no sign-in.
3. **Manual end-to-end**: run `python src/scripts/check_env.py` (SDK check), start the app, open
   the chat drawer and ask "Which transfer bags are at risk right now?". Check the answer cites
   the tool and matches `GET /api/baggage/at-risk`.
4. Run `@reviewer` on `copilot_agent.py` before opening the PR.
