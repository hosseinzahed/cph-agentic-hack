---
applyTo: "src/backend/**/*.py"
description: "Python, FastAPI, SQLModel and pytest conventions for the CPH Agentic Hack backend."
---
<!-- Written for this repo: github/awesome-copilot has no general Python instructions file.
     TODO: replace or extend with an upstream file if one is published. -->

# Python backend conventions

## Style
- Python 3.11+. Type hints on every function, including return types. Use `X | None`, not `Optional[X]`.
- Docstring on every public function and route: one line on what it returns.
- Small functions with clear names. No metaclasses, decorators or abstractions that a newcomer
  cannot read in a minute.
- Absolute imports from the `backend` package: `from backend.app.models import Flight`.
- Resolve file paths from `__file__` (`Path(__file__).resolve()`), never from the working directory.

## FastAPI routes
- Copy the pattern in `src/backend/app/routers/airports.py`.
- One `APIRouter` per track file with a `prefix` and `tags`.
- Declare a Pydantic `response_model` and return the matching data (or SQLModel rows).
- Inject the DB with `session: Session = Depends(get_session)`.
- Validate inputs with `Query(...)` / `Path(...)` and enums from `models.py`.
- Raise `HTTPException(404, ...)` for missing items and `HTTPException(400, ...)` for bad input.
- Keep business logic in plain functions (easy to unit-test and to reuse as a Copilot SDK tool);
  the route only parses input and returns the result.

## SQLModel and SQLite
- Query with `session.exec(select(Model).where(...))`. Never build SQL with f-strings or `%`.
- Datetimes are timezone-aware UTC. Compare against `datetime.now(UTC)`.
- Join tables explicitly (`select(StandAllocation, Flight).join(Flight)`).
- The data model is fixed by `models.py`; if you add a column, update `seed.py` too.

## Synthetic data and privacy
- All data is synthetic. Never add real names, bag tags, booking references or personal data.
- Tools exposed to the Copilot SDK are read-only and return aggregated, non-personal data.

## Tests (pytest)
- Tests live in `src/backend/tests/` and use the `client` fixture from `conftest.py`
  (a seeded throwaway database).
- Arrange / act / assert, one behaviour per test, descriptive names
  (`test_get_unknown_airport_returns_404`).
- Test the happy path, filters, empty results and error cases (404/400).
- When a stub is implemented, remove it from `STUBS` in `test_stubs.py`.
- Run with `pytest` from the repository root.
