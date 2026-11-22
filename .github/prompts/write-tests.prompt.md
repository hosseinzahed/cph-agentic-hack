---
name: write-tests
description: Generate pytest tests for the selected FastAPI router (or the open file) using the seeded test database.
argument-hint: "Select a router or name it, e.g. src/backend/app/routers/gates.py"
agent: agent
---

Write pytest tests for ${selection} (if nothing is selected, use the router in ${file}).

1. Read the router, `src/backend/app/models.py`, `src/backend/tests/conftest.py` and the
   existing tests (`test_airports.py` shows the style).
2. Create or extend `src/backend/tests/test_<router>.py`. Use the `client` fixture; the test
   database is seeded once with the deterministic synthetic data from
   `src/backend/scripts/seed.py`, so you can rely on it containing flights, flows, disruptions,
   stand conflicts and transfer bags at risk.
3. For each implemented route cover: happy path (status 200 and response shape), each query
   filter, empty results, and error cases (404 for missing ids, 422 for invalid enums or dates).
   Don't assert exact counts that depend on the time of day; assert properties instead (e.g.
   "every returned flight has direction DEP", "results are sorted by sched_time").
4. For routes that still return 501, leave them in `STUBS` in `test_stubs.py`; for implemented
   routes, remove them from `STUBS`.
5. One behaviour per test, arrange/act/assert, descriptive names.
6. Run `pytest` and make the tests pass without weakening them.
