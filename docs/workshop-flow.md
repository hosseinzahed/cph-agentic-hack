# Workshop flow (120 minutes)

← [Docs index](README.md)

| Time | Step | Copilot capability |
|---|---|---|
| 0–10 | Setup check (`src/scripts/check_env.py`), app running, map visible | Copilot Chat, agent mode, `/explain-this-repo` |
| 10–25 | Review and tweak instructions; pull one more from awesome-copilot | Custom instructions |
| 25–40 | Use `@architect` to plan your track, draw its flow and create issues and branches | Custom agents, GitHub MCP, Microsoft Learn MCP, draw.io MCP |
| 40–75 | Build your track's endpoints and visualisation | Agent mode, skills, prompt files, (optional) assign an issue to the Copilot coding agent |
| 75–95 | Expose your track's data as a Copilot SDK tool and turn on the assistant | Copilot SDK, `copilot-sdk-tool` skill |
| 95–110 | Tests, `@reviewer`, open a PR and request Copilot code review | Prompt files, custom agent, code review |
| 110–120 | Demos | — |

Each track guide breaks these blocks into numbered steps with prompts, hints and checkpoints.

---

## 0–10 · Setup check

Run from the repository root:

```bash
python src/scripts/check_env.py
uvicorn backend.app.main:app --app-dir src --reload
```

Open http://localhost:8000 and http://localhost:8000/docs.

💬 **Prompts**
- `/explain-this-repo` (prompt file; pick your track when asked)
- "Which files do I touch for the `<track>` track? List every `HACK(<track>)` marker with a link."

✅ **You're on track if…** the map is centred on CPH with airport markers, the header says
"API ok · data seeded", `pytest` is green and you know your track's files.

## 10–25 · Custom instructions

Open `.github/copilot-instructions.md` and the files in `.github/instructions/`. Notice how
`applyTo` targets `src/backend/**/*.py`, `src/frontend/**` and the assistant folder.

💬 **Prompts**
- "Summarise the rules Copilot will follow when I edit `src/frontend/tracks/flights.js`. Which instruction files apply?"
- "Add a rule to `.github/instructions/frontend.instructions.md`: times are shown as HH:MM in Europe/Copenhagen time."

Then browse [awesome-copilot instructions](https://github.com/github/awesome-copilot/tree/main/instructions)
and add **one** that helps your track (keep the attribution and fix its `applyTo` to a `src/` path).
Ideas: a Chart.js or testing guide, a performance or security checklist.

✅ **You're on track if…** you can explain which instructions apply to which files, and you
committed one small instruction change.

## 25–40 · Plan with `@architect`

Select **architect** in the agent picker (it uses the GitHub, Microsoft Learn and draw.io MCP
servers from `.vscode/mcp.json`; start them when VS Code asks).

💬 **Prompts**
- "Plan the `<track>` track for a team of `<n>`. Propose the API contract and task breakdown."
- "Draw the end-to-end flow for the `<track>` track: UI → FastAPI → SQLite → Copilot SDK tool → automation_queue. Save it to docs/diagrams/."
- "Looks good. Create the issues and the branch `track/<track>`."

✅ **You're on track if…** there is a `docs/diagrams/<track>-flow.drawio` file, 3–6 issues in
GitHub and a branch you've checked out.

## 40–75 · Build

Work issue by issue in **agent mode**. Use `/new-endpoint` and `/write-tests`, the
`@map-builder` agent or `leaflet-map` skill for map layers, and the `seed-data-generator` skill
if you need more data. Optional: assign one well-scoped issue to the **Copilot coding agent**
on GitHub and keep working locally while it opens a PR.

💬 **Prompts**
- `/new-endpoint GET /api/<...>` (see your track guide for the exact endpoint)
- "@map-builder Draw `<layer>` from `GET /api/<...>` with a legend."

✅ **You're on track if…** your endpoints return data (no 501) and are tested, your tab shows a
real visualisation, and your KPI tile shows a number.

## 75–95 · Copilot SDK tool

Follow [assistant-and-finale.md](assistant-and-finale.md). One person per room wires the shared
client (`start_client`, `ask`, `POST /api/assistant/chat`); every track adds its tool.

💬 **Prompts**
- "Use the copilot-sdk-tool skill to expose `<function>` as the Copilot SDK tool `<tool_name>`."
- In the chat drawer: "What should a duty manager know about `<your track>` right now?"

✅ **You're on track if…** the chat drawer is enabled and answers a question using your tool.

## 95–110 · Tests, review and PR

💬 **Prompts**
- `/write-tests` on your router.
- "@reviewer Review my changes for the `<track>` track."
- "Fix the 🔴 and 🟠 findings from the review."

Then push, open a PR (link your issues), and **request a review from Copilot** in the PR's
Reviewers menu. Address its comments.

✅ **You're on track if…** `pytest` is green, `@reviewer` says **Ready for PR**, and Copilot has
reviewed your pull request.

## 110–120 · Demos

Two minutes per team: show the visualisation, one assistant question, and one Copilot moment
that surprised you. If there's time, try the cross-track finale question in
[assistant-and-finale.md](assistant-and-finale.md).
