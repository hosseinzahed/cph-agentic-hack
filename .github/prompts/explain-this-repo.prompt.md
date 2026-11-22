---
name: explain-this-repo
description: A 5-minute guided tour of the CPH Agentic Hack repo for newcomers.
agent: ask
---

Give me a **5-minute guided tour** of this repository for a developer joining the CPH Agentic
Hack. Read `README.md`, `.github/copilot-instructions.md`, `docs/README.md`,
`docs/workshop-flow.md`, `src/backend/app/main.py`, `src/backend/app/routers/airports.py`,
`src/backend/app/models.py`, `src/frontend/index.html` and `src/frontend/app.js`.

Structure the answer as:

1. **What we're building** (3 lines): the three tiers and the Copilot SDK assistant.
2. **Request flow**: what happens from opening http://localhost:8000 to airport markers on the
   map (files and functions, with links).
3. **The data**: the seven tables in `models.py`, one line each, and how `seed.py` creates them.
4. **The reference pattern**: what to copy from `airports.py` and `test_airports.py`.
5. **Where the gaps are**: list the `HACK(<track>)` markers grouped by track
   (`onboarding`, `flights`, `disruptions`, `gates`, `assistant`) with file links.
6. **Copilot features in this repo**: instructions, agents (`@architect`, `@map-builder`,
   `@reviewer`), skills, prompt files and MCP servers, one line each on when to use them.
7. **Your first 3 steps** for the track ${input:track:onboarding | flights | disruptions | gates},
   pointing to its guide in `docs/`.

Keep it skimmable: short bullets, file links, no code changes.
