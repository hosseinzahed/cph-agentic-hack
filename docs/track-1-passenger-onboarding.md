# Track 1 · Passenger onboarding (`onboarding`)

← [Docs index](README.md) · [Workshop flow](workshop-flow.md) · Next: [Assistant & finale](assistant-and-finale.md)

> Jump to the **[step-by-step walkthrough](#step-by-step-walkthrough)** once you've skimmed sections 1–10.

## 1. Goal

Show how busy check-in, security and passport control are in T2 and T3, and forecast the
security wait for the coming hours.

## 2. Why it matters at CPH

Security wait time is the number passengers see first on cph.dk. Duty managers use queue
forecasts to open lanes and desks before a peak, not after it. A clear forecast means fewer
missed flights, calmer terminals and better use of staff.

## 3. Data you have

Table `passenger_flow` (see `src/backend/app/models.py`), 456 rows:

| Column | Type | Notes |
|---|---|---|
| `id` | int | Primary key |
| `terminal` | `T2` / `T3` | |
| `checkpoint` | `CHECKIN` / `SECURITY` / `PASSPORT` | `PASSPORT` = non-Schengen passport control |
| `slot_start` | datetime (UTC) | Start of a 15-minute slot, 04:00–22:45 Copenhagen time, today |
| `pax_count` | int | Passengers through the checkpoint in that slot |
| `avg_wait_min` | float | Average wait in minutes |

The data has a **morning peak around 07:00–08:00** and an **evening peak around 17:00–18:00**;
T3 is busier than T2. Optional extra signal: `flight.pax_count`, `flight.terminal` and
`flight.sched_time` for departures (passengers arrive at security roughly 60–120 minutes before
departure).

## 4. Endpoints to implement

File: `src/backend/app/routers/onboarding.py`

| Method and path | Returns | Notes |
|---|---|---|
| `GET /api/onboarding/queues?terminal=&from=&to=` | `list[QueueSlotOut]` | All slots, filtered by terminal (`T2`/`T3`) and a UTC time window. Sorted by `slot_start`. |
| `GET /api/onboarding/forecast?terminal=` | `list[QueueForecastOut]` | Predicted `avg_wait_min` per terminal and checkpoint for the next slots (for example the next 3 hours). |

## 5. UI to build

File: `src/frontend/tracks/onboarding.js` (tab **Passenger onboarding**).

- A **queue heatmap**: rows = terminal × checkpoint (6 rows), columns = 15-minute slots, cell
  colour from the status colours (for example < 10 min ok, 10–20 warn, > 20 critical) **plus**
  the number in each cell.
- A **wait-time forecast** line chart (Chart.js) for security in T2 and T3, with a "now" marker.
- **KPI tiles** "Security wait T2" and "Security wait T3" in `src/frontend/index.html`
  (`data-kpi="security-wait-t2"` / `"security-wait-t3"`): the forecast for the current slot.

## 6. Assistant tool to expose

`get_queue_forecast(terminal: "T2" | "T3" | None, checkpoint: "SECURITY" | ... = "SECURITY", hours: int = 3)`
returns the forecast per slot (local time, minutes) and the expected peak, as compact JSON.
It lets the assistant answer "How long is the security queue in T3 at 17:30?".

## 7. Copilot capabilities to try

| Capability | Use it for |
|---|---|
| `@architect` agent | Plan the API contract and draw `docs/diagrams/onboarding-flow.drawio`. |
| `/new-endpoint`, `/write-tests` prompt files | Scaffold `queues` and `forecast` with tests. |
| `frontend.instructions.md` + `a11y.instructions.md` | An accessible heatmap and chart in theme colours. |
| `seed-data-generator` skill | Optional: add synthetic staffing data (open lanes per slot). |
| `copilot-sdk-tool` skill | Expose `get_queue_forecast`. |
| `@reviewer` agent | Check accessibility (colour + number in every cell) and tests. |

Example prompts:
- "Explain the shape of the passenger_flow data: when are the peaks per terminal and checkpoint?"
- `/new-endpoint GET /api/onboarding/queues?terminal=&from=&to=`
- "Build an accessible heatmap of passenger_flow in onboarding.js: rows terminal × checkpoint, columns 15-minute slots, theme status colours with the minutes shown in each cell."

## 8. Definition of done

- [ ] `GET /api/onboarding/queues` and `GET /api/onboarding/forecast` return data and are tested; both removed from `STUBS` in `test_stubs.py`.
- [ ] The tab shows a heatmap and a forecast chart, using `theme.css` colours only.
- [ ] Every coloured cell also shows its value; the chart has a caption or `aria-label`.
- [ ] "Security wait T2" and "Security wait T3" KPI tiles show minutes.
- [ ] `get_queue_forecast` is registered as a Copilot SDK tool and the assistant uses it.
- [ ] All `HACK(onboarding)` markers are gone; `pytest` is green; `@reviewer` says Ready for PR.

## 9. Stretch goals

- **Staffing advice**: how many security lanes must open to keep the wait under 10 minutes?
  (Assume one lane handles about 170 passengers per 15 minutes.)
- **Peak alert**: when the forecast passes 20 minutes, queue a `NOTIFY` action in
  `automation_queue` (see [uipath-handoff.md](uipath-handoff.md)).
- **Flight-driven forecast**: derive expected security load from departing `pax_count` per
  terminal 60–120 minutes before SOBT and compare it with `passenger_flow`.

## 10. `HACK` markers

| File | Marker (what to build) |
|---|---|
| `src/backend/app/routers/onboarding.py` | `QueueSlotOut`: adjust this response model to what your UI needs |
| `src/backend/app/routers/onboarding.py` | `QueueForecastOut`: adjust this response model to what your UI needs |
| `src/backend/app/routers/onboarding.py` | `get_queues`: query passenger_flow with the filters and return the slots (and its 501 detail) |
| `src/backend/app/routers/onboarding.py` | `get_forecast`: forecast avg_wait_min for the next slots (and its 501 detail) |
| `src/frontend/tracks/onboarding.js` | build the queue heatmap and wait-time forecast here |
| `src/frontend/index.html` | fill "Security wait T2" from GET /api/onboarding/forecast |
| `src/frontend/index.html` | fill "Security wait T3" from GET /api/onboarding/forecast |

---

## Step-by-step walkthrough

Times follow [workshop-flow.md](workshop-flow.md). Split the team: one person on the API, one on
the UI, then pair on the assistant tool.

### Step 0 · Get running (0–10 min)

> **First, get the code:** 🍴 **fork** or 📥 **clone** the repo and run the setup script, as
> described in [getting-started.md](getting-started.md). Your choice decides where your issues,
> branch and pull request go in steps 2 and 9.

🎯 App running, everyone knows the track's files.

1. From the repository root: `python src/scripts/check_env.py`, then
   `uvicorn backend.app.main:app --app-dir src --reload` and open http://localhost:8000.
2. Open the **Passenger onboarding** tab: you should see the 🚧 placeholder.
3. Open http://localhost:8000/docs and try `GET /api/onboarding/queues`: it returns **501** with
   a `HACK(onboarding)` message.

💬 `/explain-this-repo` (answer `onboarding` when asked for the track)

💬 "List every HACK(onboarding) marker in this repo with a link and one line on what to build."

✅ Map visible, `pytest` green, you can name the 7 markers in section 10.

### Step 1 · Tune Copilot for this track (10–25 min)

🎯 Copilot knows the conventions you care about.

1. Read `.github/copilot-instructions.md` (glossary: T2/T3, pax, checkpoints) and
   `.github/instructions/frontend.instructions.md` (theme rules, Chart.js defaults).
2. Add one rule that matters for this track, for example in `frontend.instructions.md`:
   "Wait-time thresholds: under 10 minutes ok, 10–20 warn, over 20 critical."
3. Browse [awesome-copilot instructions](https://github.com/github/awesome-copilot/tree/main/instructions)
   and add one more (keep the attribution, set `applyTo` to a `src/` path).

💬 "Which instruction files apply when I edit src/frontend/tracks/onboarding.js? Summarise their rules in 5 bullets."

✅ One small instruction change committed.

### Step 2 · Plan with `@architect` (25–40 min)

🎯 An agreed API contract, a diagram and issues.

1. Pick **architect** in the agent picker. Start the MCP servers when VS Code asks.
2. 💬 "Plan the onboarding track for a team of 3. Propose the API contract for /api/onboarding/queues and /api/onboarding/forecast with example JSON, and a task breakdown."
3. 💬 "Draw the end-to-end flow for the onboarding track: UI heatmap and KPI tiles → FastAPI onboarding router → passenger_flow table → get_queue_forecast Copilot SDK tool. Save it to docs/diagrams/onboarding-flow.drawio."
4. Review the plan. Decide your forecast method now (see the hint).
5. Create the issues and the branch. The prompt depends on your path ([getting-started.md](getting-started.md)):
   - 🍴 Fork: 💬 "Create the issues and the branch track/onboarding in <you>/cph-agentic-hack."
   - 📥 Clone with write access: 💬 "We are team <team>. Create the issues and the branch <team>/onboarding in hosseinzahed/cph-agentic-hack."
   - 📥 Clone, local only: skip the issues and run `git switch -c track/onboarding`.

   Then `git fetch` and check out the branch.

💡 **Forecast options (pick the simplest that demos well):**
- *A. Read-ahead*: the seed already contains the whole day, so slots after "now" are your
  "planned" flow; return them as the forecast.
- *B. Smoothed*: a moving average of the last few slots blended with the day's profile.
- *C. Flight-driven*: departing passengers per terminal shifted 60–120 minutes earlier.

✅ `docs/diagrams/onboarding-flow.drawio` exists (open it with the Draw.io extension) and the
issues are on GitHub.

### Step 3 · Explore the data (40–45 min)

🎯 You know what the rows look like before writing the API.

💬 "Using the project's SQLModel models and the existing engine, write a throwaway Python snippet I can run from the repo root that prints the 5 busiest SECURITY slots per terminal in Copenhagen local time. Don't add it to the repo."

💡 Times are stored in UTC; convert with `ZoneInfo("Europe/Copenhagen")` when you display them.

✅ You can say when the T3 security peak is and how long its wait gets.

### Step 4 · Build `GET /api/onboarding/queues` (45–55 min)

🎯 First endpoint, tested, following the `airports.py` pattern.

1. 💬 `/new-endpoint GET /api/onboarding/queues?terminal=&from=&to= for the onboarding track`
2. Check the result at http://localhost:8000/docs.
3. 💬 `/write-tests` with `onboarding.py` selected.

💡 `from` is a Python keyword, so the stub uses `from_` with `alias="from"`; keep it.
Filters are optional: build the `select()` step by step and only add `where` clauses for the
parameters that were given.

✅ `pytest` green; `queues` no longer in `STUBS`; `/docs` returns slots sorted by time.

### Step 5 · Build `GET /api/onboarding/forecast` (55–62 min)

🎯 The forecast your KPI tiles and chart will use.

💬 `/new-endpoint GET /api/onboarding/forecast?terminal= using forecast option <A|B|C> from docs/track-1-passenger-onboarding.md`

💡 Put the forecast in a plain function (e.g. `forecast_waits(session, terminal, hours)`): the
route calls it now, and the Copilot SDK tool calls it in step 8. Decide what "now" means when
the workshop runs outside 04:00–23:00 (clamp to the first or last slot).

🤖 Optional: assign the "forecast" issue to the **Copilot coding agent** on GitHub and
continue with the UI while it works.

✅ Forecast returns rows for both terminals and the three checkpoints; tests cover the
`terminal` filter.

### Step 6 · Build the heatmap and chart (62–72 min)

🎯 The tab shows real data.

1. 💬 "In src/frontend/tracks/onboarding.js, fetch /api/onboarding/queues and render an accessible heatmap: a table or CSS grid with rows terminal × checkpoint and columns per 15-minute slot, theme status colours and the minutes in each cell. Keep the placeholder if the API returns 501."
2. 💬 "Below the heatmap add a Chart.js line chart of the SECURITY forecast for T2 and T3 from /api/onboarding/forecast, using chartPalette() and an aria-label."

💡 Chart.js has no built-in heatmap: an HTML table with coloured cells is simpler and more
accessible. `render(panel)` runs every time the tab opens: destroy the previous chart first.
Use `.chip--ok/warn/critical` or `cssVar("--status-…")`, never hex values.

✅ Heatmap and chart render, the page has no console errors and the colours match the theme.

### Step 7 · KPI tiles and clean-up (72–75 min)

🎯 "Security wait T2/T3" show live numbers.

💬 "Fill the Security wait T2 and T3 KPI tiles in index.html from /api/onboarding/forecast when the page loads, and refresh them every 60 seconds. Remove the matching HACK(onboarding) comments."

✅ Both tiles show minutes; `grep HACK(onboarding)` shows only markers you haven't finished.

### Step 8 · Expose `get_queue_forecast` to the assistant (75–95 min)

🎯 The CPH Ops Assistant can answer queue questions.

1. Read [assistant-and-finale.md](assistant-and-finale.md); coordinate with the person wiring the shared client.
2. 💬 "Use the copilot-sdk-tool skill to expose forecast_waits as the read-only Copilot SDK tool get_queue_forecast (params: terminal, checkpoint, hours) and register it in build_tools() in copilot_agent.py."
3. Ask in the chat drawer: "How long will the security queue in T3 be at the evening peak?"

✅ The answer matches your forecast endpoint and mentions the tool.

### Step 9 · Tests, review and PR (95–110 min)

💬 `/write-tests` on `onboarding.py` (fill any gaps).

💬 "@reviewer Review the onboarding track changes."

💬 "Fix the 🔴 and 🟠 findings."

Push the branch, open a PR that closes your issues, and request a **Copilot code review**.
The push and PR commands depend on your path: see the table in
[workshop-flow.md](workshop-flow.md#95110--tests-review-and-pr). 🍴 **Fork users:** set the PR's
**base repository** to your fork (GitHub defaults to the original repo).

✅ `pytest` green locally, reviewer verdict **Ready for PR**, Copilot review addressed.

### Step 10 · Demo (110–120 min)

Show: the heatmap at the morning peak, the KPI tiles, and the assistant answering a queue
question. Mention one Copilot feature that saved you time.

### Troubleshooting

| Symptom | Fix |
|---|---|
| Heatmap empty | Check the time window: `slot_start` is UTC; omit `from`/`to` to get the whole day. |
| Chart draws twice / grows | Destroy the old `Chart` before creating a new one in `render()`. |
| Forecast is empty in the evening | "Now" is after 22:45 local: fall back to the last slots of the day. |
| 422 on `terminal=t3` | The enum is case-sensitive: use `T3`. |
