# Track 3 · Potential disruptions (`disruptions`)

← [Docs index](README.md) · [Workshop flow](workshop-flow.md) · Next: [Assistant & finale](assistant-and-finale.md)

> Jump to the **[step-by-step walkthrough](#step-by-step-walkthrough)** once you've skimmed sections 1–10.

## 1. Goal

Show active disruptions (weather, ATC, strikes, technical) on the map and work out which
flights and transfer connections each one affects.

## 2. Why it matters at CPH

A thunderstorm over Frankfurt or a slot restriction at Heathrow ripples back to CPH as delays,
missed connections and stand congestion. Seeing the impact early lets the operations centre
re-plan, rebook and inform passengers before the queues build up.

## 3. Data you have

Table `disruption` (6 synthetic scenarios today, times in Copenhagen local time):

| Title | Type | Where | Radius | Window (local) | Severity |
|---|---|---|---|---|---|
| Fog at CPH | `WEATHER` | CPH | 25 km | 04:00–09:30 | 3 |
| Snow and de-icing at OSL | `WEATHER` | OSL | 40 km | 06:00–12:00 | 2 |
| ATC flow restriction at LHR | `ATC` | LHR | 60 km | 07:00–21:00 | 3 |
| Ground-handling strike (scenario) at CDG | `STRIKE` | CDG | 15 km | 10:00–18:00 | 4 |
| Baggage sorter degraded at CPH T3 | `TECHNICAL` | CPH T3 | 2 km | 11:00–15:00 | 2 |
| Thunderstorms near FRA | `WEATHER` | near FRA | 90 km | 13:00–19:00 | 4 |

Columns: `id`, `type`, `title`, `description`, `lat`, `lon`, `radius_km`, `starts_at`, `ends_at`
(UTC), `severity` (1–5).

Related tables: `flight` (route, times, status), `airport` (coordinates), `transfer_bag`
(connections: `inbound_flight_id` → `outbound_flight_id`, `status`), and `automation_queue`
(actions such as `REBOOK` or `NOTIFY` for a robot or handler).

## 4. Endpoints to implement

Files: `src/backend/app/routers/disruptions.py` and `src/backend/app/routers/automation.py`

| Method and path | Returns | Notes |
|---|---|---|
| `GET /api/disruptions/active` | `list[DisruptionOut]` | Disruptions where `starts_at <= now < ends_at`. |
| `GET /api/disruptions/{id}/impact` | `DisruptionImpactOut` | Flights whose other airport lies inside the circle during the window (or whose route crosses it), plus affected connections; 404 for unknown ids. |
| `POST /api/automation/actions` | `ActionOut` (201) | Queue a `REBOOK`/`NOTIFY` action as `PENDING` (optional, for the UiPath hand-off). |
| `GET /api/automation/actions?status=` | `list[ActionOut]` | List queued actions (optional). |

## 5. UI to build

File: `src/frontend/tracks/disruptions.js` (tab **Disruptions**).

- **Disruption circles** on the map, coloured by severity with the status colours, semi-transparent,
  with a **legend** and popups (layer `disruptions:circles`).
- **Affected routes turn red**: draw routes that cross an active circle in `--status-critical`
  on your own layer (`disruptions:affected-routes`).
- **Impact list**: per disruption, the affected flights (time, flight, route, status) and the
  number of transfer connections at risk.
- **KPI tile** "Active disruptions" (`data-kpi="active-disruptions"`).

## 6. Assistant tool to expose

`get_disruption_impact(disruption_id: int | None, airport_iata: str | None)` returns the
disruption, the affected flights and connections, as compact JSON. It lets the assistant answer
"What does the Frankfurt thunderstorm mean for our departures?".

## 7. Copilot capabilities to try

| Capability | Use it for |
|---|---|
| `@architect` agent + Microsoft Learn MCP | Plan the impact algorithm; draw `docs/diagrams/disruptions-flow.drawio` including `automation_queue`. |
| `/new-endpoint`, `/write-tests` prompt files | `active` and `impact` with tests (time windows are good test cases). |
| `@map-builder` agent + `leaflet-map` skill | Circles, red affected routes, legend (`drawDisruptions`, `routeCrossesCircle`). |
| `seed-data-generator` skill | Add your own disruption scenario (e.g. crosswind at CPH). |
| `copilot-sdk-tool` skill | Expose `get_disruption_impact`. |

Example prompts:
- "Plan the disruptions track. Draw the end-to-end flow for the disruptions track: UI → FastAPI → SQLite → Copilot SDK tool → automation_queue."
- `/new-endpoint GET /api/disruptions/{id}/impact`
- "@map-builder Draw active disruptions as circles coloured by severity with a legend."

## 8. Definition of done

- [ ] `GET /api/disruptions/active` and `GET /api/disruptions/{id}/impact` return data and are tested (including 404); removed from `STUBS`.
- [ ] Circles and red affected routes render with a legend; popups escape text.
- [ ] The impact list shows affected flights and connections.
- [ ] "Active disruptions" KPI shows a number.
- [ ] `get_disruption_impact` is a Copilot SDK tool the assistant uses.
- [ ] All `HACK(disruptions)` markers you worked on are gone (the automation ones only if you built the hand-off); `pytest` green; `@reviewer` says Ready for PR.

## 9. Stretch goals

- **Rebooking priorities**: rank affected passengers' connections (by connection time and
  severity) and `POST` them to `/api/automation/actions` as `REBOOK` actions; show the
  pending queue (see [uipath-handoff.md](uipath-handoff.md)).
- **Time travel**: add an optional `at=` query parameter so you can demo any time of day.
- **What-if**: "If Frankfurt closes for 2 hours…" create a temporary disruption and recompute
  the impact (this is also the [finale](assistant-and-finale.md#cross-track-finale) question).

## 10. `HACK` markers

| File | Marker (what to build) |
|---|---|
| `src/backend/app/routers/disruptions.py` | `DisruptionOut`: adjust this response model to what your UI needs |
| `src/backend/app/routers/disruptions.py` | `DisruptionImpactOut`: adjust this response model to what your UI needs |
| `src/backend/app/routers/disruptions.py` | `list_active_disruptions`: return active disruptions (and its 501 detail) |
| `src/backend/app/routers/disruptions.py` | `get_disruption_impact`: find flights inside the circle during the window (and its 501 detail) |
| `src/backend/app/routers/automation.py` | `create_action`: write the action to automation_queue (and its 501 detail) |
| `src/backend/app/routers/automation.py` | `list_actions`: list automation_queue rows, newest first (and its 501 detail) |
| `src/frontend/tracks/disruptions.js` | draw disruption circles, red affected routes, impact list, KPI |
| `src/frontend/index.html` | fill "Active disruptions" from GET /api/disruptions/active |

---

## Step-by-step walkthrough

> 🖥️ **Using the GitHub Copilot app?** All steps work there too ([copilot-app.md](copilot-app.md)).
> Start your session with **Workspace: Current checkout**. Pick agents (`architect`, `map-builder`,
> `reviewer`) in the agent picker or with `/agent`. Replace the prompt-file shortcuts:
> `/explain-this-repo` → "Follow `.github/prompts/explain-this-repo.prompt.md`",
> `/new-endpoint X` → "Follow `.github/prompts/new-endpoint.prompt.md` for X", and
> `/write-tests` → "Follow `.github/prompts/write-tests.prompt.md` for `<router>`".
> To see the app, ask "Open http://localhost:8000 in a browser canvas". To open the pull
> request, use **Create PR**.

Times follow [workshop-flow.md](workshop-flow.md). Suggested split: one person on `active` +
map circles, one on `impact`, one on the impact list and (later) the automation hand-off.

### Step 0 · Get running (0–10 min)

> **First, get the code:** 🍴 **fork** or 📥 **clone** the repo and run the setup script, as
> described in [getting-started.md](getting-started.md). Your choice decides where your issues,
> branch and pull request go in steps 2 and 9.

1. With the venv activated ([getting-started](getting-started.md#both-paths-set-up-and-run)):
   `python src/scripts/check_env.py`, then `uvicorn backend.app.main:app --app-dir src --reload`.
2. Open the **Disruptions** tab and http://localhost:8000/docs: `GET /api/disruptions/active` → **501**.

💬 `/explain-this-repo` (track: `disruptions`)

💬 "List every HACK(disruptions) marker with a link and one line on what to build."

✅ You can name the 8 markers in section 10.

### Step 1 · Tune Copilot for this track (10–25 min)

1. Read `.github/copilot-instructions.md` and `.github/instructions/python.instructions.md`.
2. Add a rule, e.g. in `python.instructions.md`: "Distances use the haversine formula in
   kilometres; time windows are half-open `[starts_at, ends_at)`."
3. Add one instruction file from awesome-copilot (attribution kept, `applyTo` under `src/`).

💬 "Which instruction files apply to src/backend/app/routers/disruptions.py?"

✅ One small instruction change committed.

### Step 2 · Plan with `@architect` (25–40 min)

1. Select **architect**; start the MCP servers when asked.
2. 💬 "Plan the disruptions track for a team of 3. Propose the API contract for /api/disruptions/active and /api/disruptions/{id}/impact with example JSON. Define 'affected flight' precisely."
3. 💬 "Draw the end-to-end flow for the disruptions track: UI → FastAPI → SQLite → Copilot SDK tool → automation_queue. Save it to docs/diagrams/disruptions-flow.drawio."
4. Create the issues and the branch. The prompt depends on your path ([getting-started.md](getting-started.md)):
   - 🍴 Fork: 💬 "Create the issues and the branch track/disruptions in <you>/cph-agentic-hack."
   - 📥 Clone with write access: 💬 "We are team <team>. Create the issues and the branch <team>/disruptions in hosseinzahed/cph-agentic-hack."
   - 📥 Clone, local only: skip the issues and run `git switch -c track/disruptions`.

   Then `git fetch` and check out the branch.

💡 **Define "affected" before coding.** A simple, demo-friendly rule: a flight is affected if
its *other* airport (not CPH) lies inside the circle **and** its scheduled time falls within
the window (± 1 hour). For CPH-based disruptions (fog, baggage sorter), every CPH flight in
the window is affected. A richer rule samples points along the great-circle route.

✅ Diagram saved, a written definition of "affected", issues on GitHub.

### Step 3 · Explore the data (40–45 min)

💬 "Write a throwaway snippet (not committed) that prints each disruption with its local start/end time, and how many flights go to an airport within its radius."

💡 Most windows are during the day. If you work early or late, nothing may be "active":
plan for an `at=` parameter (stretch goal) or test with fixed times.

✅ You know which disruptions are active at the time of your demo.

### Step 4 · Build `GET /api/disruptions/active` (45–55 min)

💬 `/new-endpoint GET /api/disruptions/active`

💬 `/write-tests` with `disruptions.py` selected.

💡 Compare against `datetime.now(UTC)` (database times are timezone-aware UTC). In tests,
don't depend on the clock: test the plain function with a fixed `now` argument.

✅ `pytest` green; `active` removed from `STUBS`.

### Step 5 · Build `GET /api/disruptions/{id}/impact` (55–62 min)

💬 `/new-endpoint GET /api/disruptions/{id}/impact using the 'affected flight' rule from our plan: haversine distance from the other airport to the disruption centre, and the time window ± 1 hour. Count affected connections from transfer_bag.`

💡 Haversine in Python needs only `math` (radius 6371 km). Load airports into a dict by IATA
code once per request. Connections at risk = transfer bags whose inbound **or** outbound
flight is affected. Return 404 when the id doesn't exist.

🤖 Optional: assign the automation hand-off issue (`POST/GET /api/automation/actions`) to the
**Copilot coding agent**.

✅ FRA thunderstorms affect Frankfurt flights in the afternoon; unknown ids return 404; tested.

### Step 6 · Circles, red routes and impact list (62–72 min)

1. 💬 "@map-builder In disruptions.js fetch /api/disruptions/active and draw circles coloured by severity with a legend (layer disruptions:circles), using drawDisruptions from the leaflet-map skill."
2. 💬 "For each active disruption, fetch its impact and draw the affected routes from CPH in --status-critical on layer disruptions:affected-routes; list affected flights and connections in the panel."

💡 `routeCrossesCircle(greatCircle(cph, dest), disruption)` from the skill's `snippets.js`
gives the visual check. Keep your layers separate from the flights track (`flights:routes`).
Severity needs a text label in the legend and the list, not just colour.

✅ Circles and red routes appear; the list matches the API; no console errors.

### Step 7 · KPI tile and clean-up (72–75 min)

💬 "Fill the Active disruptions KPI tile from /api/disruptions/active on page load and every 60 seconds. Remove the matching HACK(disruptions) comments."

✅ The tile shows the count; only unfinished markers remain.

### Step 8 · Expose `get_disruption_impact` to the assistant (75–95 min)

1. Read [assistant-and-finale.md](assistant-and-finale.md).
2. 💬 "Use the copilot-sdk-tool skill to expose my impact function as the read-only Copilot SDK tool get_disruption_impact (params: disruption_id or airport_iata) and register it in build_tools()."
3. Ask: "What does the Frankfurt thunderstorm mean for our departures and connections?"

✅ The answer lists the same flights as your impact endpoint.

### Step 9 · Tests, review and PR (95–110 min)

💬 `/write-tests` on `disruptions.py` · "@reviewer Review the disruptions track changes." · "Fix the 🔴 and 🟠 findings."

Push, open a PR, request a **Copilot code review**, address comments.
The push and PR commands depend on your path: see the table in
[workshop-flow.md](workshop-flow.md#95110--tests-review-and-pr). 🍴 **Fork users:** set the PR's
**base repository** to your fork (GitHub defaults to the original repo).

✅ `pytest` green, reviewer **Ready for PR**.

### Step 10 · Demo (110–120 min)

Show the circles and red routes, open one impact list, and ask the assistant the Frankfurt
question. If another team has the assistant wired up, try the cross-track finale.

### Troubleshooting

| Symptom | Fix |
|---|---|
| `active` is empty | Outside all windows. Add `at=` or re-seed and check local times in section 3. |
| Circles are tiny or huge | `L.circle` radius is in **metres**: `radius_km * 1000`. |
| `TypeError: can't compare offset-naive and offset-aware datetimes` | Use `datetime.now(UTC)`, not `datetime.now()` or `utcnow()`. |
| Every flight is "affected" by CPH fog | Expected for CPH-based disruptions; filter by the time window. |
