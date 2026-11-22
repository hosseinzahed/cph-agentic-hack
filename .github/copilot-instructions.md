# Copilot instructions: CPH Agentic Hack

This repo is the starter for **CPH Agentic Hack with GitHub Copilot**: a three-tier airport
operations app for Copenhagen Airport (CPH). Teams build one track each in about 2 hours.

## Architecture

- **UI**: static HTML, CSS and vanilla JavaScript ES modules in `src/frontend/`. Leaflet with
  OpenStreetMap tiles for maps, Chart.js for charts. No framework and no build step.
- **API**: Python 3.11+ and FastAPI in `src/backend/app/`. FastAPI also serves the UI
  (`StaticFiles` mounted at `/`), so everything runs as one process on port 8000.
- **Database**: SQLite through SQLModel (`src/backend/app/models.py`, file `src/backend/data/cph.db`).
- **Intelligence**: the GitHub Copilot SDK for Python (`src/backend/app/assistant/copilot_agent.py`),
  exposing read-only app functions as tools to the "CPH Ops Assistant" chat.

## Where things live

| Path | Purpose |
|---|---|
| `src/backend/app/routers/` | One router per track. `airports.py` is the implemented reference pattern; the others are 501 stubs. |
| `src/backend/scripts/seed.py` | Deterministic synthetic data for one "hack day". |
| `src/backend/tests/` | pytest tests (health, airports, stubs). |
| `src/frontend/tracks/*.js` | One render function per track tab. |
| `src/frontend/theme.css` | The ONLY place colours and fonts are defined. |
| `docs/` | Workshop guide. `getting-started.md` (fork or clone), `copilot-app.md` (GitHub Copilot app instead of VS Code), then **one file per track** (`docs/track-*.md`). |
| `docs/diagrams/` | draw.io diagrams created by `@architect`. |

**Before working on a track, read its guide**: `docs/track-1-passenger-onboarding.md`,
`docs/track-2-flight-plans.md`, `docs/track-3-disruptions.md` or `docs/track-4-gates-and-baggage.md`
(and `docs/assistant-and-finale.md` for the Copilot SDK step).

## Commands (run from the repository root)

- Set up: `.\src\scripts\setup.ps1` (Windows) or `./src/scripts/setup.sh` (macOS/Linux)
- Reseed: `python src/backend/scripts/seed.py`
- Run: `uvicorn backend.app.main:app --app-dir src --reload`, then open http://localhost:8000
- Test: `pytest`
- Readiness check: `python src/scripts/check_env.py`

## Coding conventions

- Follow the pattern in `src/backend/app/routers/airports.py`: type hints, a Pydantic response
  model, a docstring, `Depends(get_session)` and `HTTPException(404)` for missing items.
- Keep functions small. Prefer clear code over clever abstractions; hackers must read it fast.
- Every endpoint gets tests in `src/backend/tests/`. When you implement a stub, remove its row
  from `STUBS` in `test_stubs.py` and add real tests.
- Use absolute imports (`from backend.app.db import get_session`). Resolve paths from `__file__`.
- Datetimes are timezone-aware UTC in the database and API; show Europe/Copenhagen time in the UI.
- Use SQLModel `select()` with bound parameters. Never build SQL with string formatting.

## Rules

- **Synthetic data only.** Never add real passenger, staff or personal data (GDPR).
- **Keep the UI free of frameworks.** Vanilla JS modules, Leaflet for maps, Chart.js for charts.
- **Use only `theme.css` variables for colours and fonts. Never hard-code hex values in components.**
  Read them in JS with `cssVar("--cph-horizon-blue")` from `src/frontend/app.js`.
- Every status colour also carries a text label or icon, never colour alone.
- Insert untrusted text with `textContent` (or `escapeHtml()` from `app.js`), never raw `innerHTML`.
- **Keep `HACK(<track>)` markers** until that feature is complete, then remove them.
- Teams either **fork** or **clone** this repo (`docs/getting-started.md`). Create issues, branches
  and PRs in the repo `origin` points to. In a fork, never target `upstream`
  (`hosseinzahed/cph-agentic-hack`). On the shared repo, prefix branches with the team name.
- Copilot SDK tools are read-only. Never auto-approve shell or file-write tools for the chat assistant.
- No secrets in code. Use `.env` (git-ignored); `.env.example` documents the variables.

## Domain glossary

- **SOBT / EOBT**: Scheduled / Estimated Off-Block Time, when a departing aircraft leaves its
  stand. (SIBT / EIBT are the in-block equivalents for arrivals.) In this repo `flight.sched_time`
  is SOBT/SIBT and `flight.est_time` is EOBT/EIBT.
- **Stand vs. gate**: the **stand** is where the aircraft parks; the **gate** is where passengers
  board. At contact stands they share a label (e.g. `A12`); remote stands (`R81`…) use buses.
- **MCT**: Minimum Connection Time, the shortest legal transfer time. This repo uses 45 minutes.
- **T2 / T3**: CPH passenger terminals 2 and 3 (they share one security area at CPH; here they
  are modelled separately to make the data more interesting).
- **Pax**: passengers. `pax_count` is a number of passengers.
- **Checkpoints**: `CHECKIN`, `SECURITY` and `PASSPORT` (non-Schengen passport control).
