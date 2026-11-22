---
name: new-endpoint
description: Scaffold a FastAPI endpoint, its Pydantic response model and pytest tests, following the airports.py reference pattern.
argument-hint: "e.g. GET /api/flights?direction=DEP for the flights track"
agent: agent
---

Implement the endpoint described here: **${input:endpoint:e.g. GET /api/flights?direction=DEP}**.

Follow these steps:

1. Read `src/backend/app/routers/airports.py` (the reference pattern), `src/backend/app/models.py`
   and the track guide in `docs/` for this endpoint. Find its stub and `HACK(<track>)` marker in
   `src/backend/app/routers/`.
2. Keep the existing route path, query parameters and function name. Refine the stub's Pydantic
   response model if needed (type hints, field descriptions).
3. Put the query logic in a small plain function (reusable later as a Copilot SDK tool) and
   call it from the route. Use SQLModel `select()` with bound parameters, timezone-aware UTC
   datetimes and `HTTPException(404/400)` for missing items or bad input.
4. Replace the `raise HTTPException(status_code=501, ...)` and remove the endpoint's
   `HACK(<track>)` comment.
5. Tests in `src/backend/tests/test_<track>.py`: happy path, each filter, empty result and
   error cases, using the `client` fixture. Remove the endpoint's row from `STUBS` in
   `src/backend/tests/test_stubs.py`.
6. Run `pytest` and fix failures. Then show a sample response from http://localhost:8000/docs.

Rules: synthetic data only, no new dependencies, small readable functions.
