# Track 4 · Gates & baggage (`gates`)

← [Docs index](README.md) · [Workshop flow](workshop-flow.md) · Next: [Assistant & finale](assistant-and-finale.md)

> Jump to the **[step-by-step walkthrough](#step-by-step-walkthrough)** once you've skimmed sections 1–10.

## 1. Goal

Visualise today's stand allocations as a Gantt chart, detect conflicting allocations, and find
the transfer bags at risk of missing their connection.

## 2. Why it matters at CPH

Two aircraft planned on the same stand at the same time means a last-minute tow, a bus
boarding or a delay. Transfer bags on tight connections are the most common reason for
mishandled baggage. Spotting both early lets stand planners and baggage handlers act first.

## 3. Data you have

Table `stand_allocation` (about 275 rows):

| Column | Type | Notes |
|---|---|---|
| `id` | int | Primary key |
| `flight_id` | int → `flight.id` | Join to get `flight_no`, `direction`, `status` |
| `stand` | str | Contact stands `A4`–`A17`, `B1`–`B10`, `C26`–`C39`, `D1`–`D8`, `E20`–`E27`, `F1`–`F6`; remote `R81`+ only if every contact stand is busy |
| `start_time`, `end_time` | datetime (UTC) | Departures: 60–90 min before SOBT until 10 min after. Arrivals: 10 min before SIBT until 45–75 min after. |

The seed injects **3–5 deliberate conflicts** (two allocations overlapping on the same stand);
it prints the number as `stand_conflicts`.

Table `transfer_bag` (500 rows, about 60 `AT_RISK` and 30 `MISSED`):

| Column | Type | Notes |
|---|---|---|
| `tag_no` | str | Synthetic, e.g. `SYN0000042` |
| `inbound_flight_id`, `outbound_flight_id` | int → `flight.id` | Arrival into CPH → departure from CPH |
| `status` | `ON_TIME` / `AT_RISK` / `MISSED` | Pre-computed by the seed from connection time vs. **MCT = 45 min** |

Use `flight.sched_time` / `est_time` to (re)compute the connection time:
outbound EOBT (or SOBT) − inbound EIBT (or SIBT).

## 4. Endpoints to implement

File: `src/backend/app/routers/gates.py`

| Method and path | Returns | Notes |
|---|---|---|
| `GET /api/gates/allocations?date=` | `list[StandAllocationOut]` | Allocations for one day (default today, Copenhagen), joined with `flight_no`. |
| `GET /api/gates/conflicts` | `list[StandConflictOut]` | Pairs (or groups) of allocations that overlap on the same stand, with the overlap window. |
| `GET /api/baggage/at-risk` | `list[BagAtRiskOut]` | Transfer bags with connection time below MCT (or a delayed/cancelled outbound), sorted by connection time. |

## 5. UI to build

File: `src/frontend/tracks/gates.js` (tab **Gates & baggage**). This track has no header KPI
tile; show your headline numbers inside the tab.

- **Stand Gantt chart** (Chart.js horizontal floating bars): one row per stand, one bar per
  allocation, conflicting bars in `--status-critical` **with a label**.
- **Conflict list**: stand, the two flights, overlap window (local time).
- **Bags at risk**: a big count plus a table (tag, inbound → outbound, connection minutes,
  status chip).

## 6. Assistant tool to expose

`get_bags_at_risk(limit: int = 20, max_connection_min: int = 45)` returns transfer bags at risk
with flights, connection minutes and status as compact JSON. It lets the assistant answer
"Which outbound flights have the most bags at risk?".

## 7. Copilot capabilities to try

| Capability | Use it for |
|---|---|
| `@architect` agent | Conflict-detection approach, `docs/diagrams/gates-flow.drawio`. |
| `/new-endpoint`, `/write-tests` prompt files | Three endpoints with tests (overlap edge cases!). |
| `frontend.instructions.md` | Chart.js defaults, theme colours, accessible tables. |
| `seed-data-generator` skill | Optional: add more conflicts or a remote-stand scenario. |
| `copilot-sdk-tool` skill | Expose `get_bags_at_risk`. |
| Copilot coding agent | Good candidate: assign the "bags at risk" endpoint issue. |

Example prompts:
- `/new-endpoint GET /api/gates/conflicts: overlapping allocations on the same stand`
- "Write tests for interval overlap: touching intervals (end == start) are not a conflict."
- "Render a Chart.js Gantt of stand allocations in gates.js: horizontal floating bars, one row per stand, conflicts in --status-critical."

## 8. Definition of done

- [ ] All three endpoints return data and are tested (including the overlap edge cases); removed from `STUBS`.
- [ ] The Gantt chart shows stands and allocations in local time; conflicts are highlighted and labelled.
- [ ] The conflict list matches `GET /api/gates/conflicts` (3–5 conflicts).
- [ ] The bags-at-risk count and table render with labelled status chips.
- [ ] `get_bags_at_risk` is a Copilot SDK tool the assistant uses.
- [ ] All `HACK(gates)` markers are gone; `pytest` green; `@reviewer` says Ready for PR.

## 9. Stretch goals

- **Reassignment proposals**: for each conflict, suggest a free stand on the same pier and
  explain why; queue it as `REASSIGN_STAND` in `automation_queue` (see [uipath-handoff.md](uipath-handoff.md)).
- **Handler task list**: group bags at risk by outbound flight and gate into a printable task
  list for baggage handlers.
- **Pier filter**: filter the Gantt by pier (A–F) and zoom to a time window.

## 10. `HACK` markers

| File | Marker (what to build) |
|---|---|
| `src/backend/app/routers/gates.py` | `StandAllocationOut`: adjust this response model to what your UI needs |
| `src/backend/app/routers/gates.py` | `StandConflictOut`: adjust this response model to what your UI needs |
| `src/backend/app/routers/gates.py` | `BagAtRiskOut`: adjust this response model to what your UI needs |
| `src/backend/app/routers/gates.py` | `list_allocations`: return stand allocations for the day, joined with flight_no (and its 501 detail) |
| `src/backend/app/routers/gates.py` | `list_conflicts`: detect overlapping allocations on the same stand (and its 501 detail) |
| `src/backend/app/routers/gates.py` | `list_bags_at_risk`: return transfer bags at risk (and its 501 detail) |
| `src/frontend/tracks/gates.js` | build the stand Gantt chart, the conflict list and the bags-at-risk count here |

---

## Step-by-step walkthrough

Times follow [workshop-flow.md](workshop-flow.md). Suggested split: one person on stands
(allocations + conflicts), one on baggage, one on the UI.

### Step 0 · Get running (0–10 min)

1. `python src/scripts/check_env.py`, then `uvicorn backend.app.main:app --app-dir src --reload`.
2. Open the **Gates & baggage** tab and http://localhost:8000/docs: `GET /api/gates/conflicts` → **501**.
3. Note the `stand_conflicts` number printed by the seed script.

💬 `/explain-this-repo` (track: `gates`)

💬 "List every HACK(gates) marker with a link and one line on what to build."

✅ You can name the 7 markers in section 10.

### Step 1 · Tune Copilot for this track (10–25 min)

1. Read the glossary in `.github/copilot-instructions.md` (stand vs. gate, MCT) and
   `.github/instructions/python.instructions.md`.
2. Add a rule, e.g. "Time intervals are half-open `[start, end)`: touching intervals don't
   overlap. MCT at CPH is 45 minutes."
3. Add one instruction file from awesome-copilot (attribution kept, `applyTo` under `src/`).

💬 "Explain the difference between a stand and a gate using this repo's data model."

✅ One small instruction change committed.

### Step 2 · Plan with `@architect` (25–40 min)

1. Select **architect**; start the MCP servers when asked.
2. 💬 "Plan the gates track for a team of 3. Propose the API contract for /api/gates/allocations, /api/gates/conflicts and /api/baggage/at-risk with example JSON, and how to detect conflicts efficiently."
3. 💬 "Draw the end-to-end flow for the gates track: UI Gantt and bag list → FastAPI gates router → stand_allocation, flight and transfer_bag tables → get_bags_at_risk Copilot SDK tool → automation_queue (REASSIGN_STAND). Save it to docs/diagrams/gates-flow.drawio."
4. 💬 "Create the issues and the branch track/gates." Check out the branch.

💡 Conflict detection: group allocations by stand, sort by `start_time`, and compare each one
with the following ones while they still start before it ends. Two intervals overlap when
`a.start < b.end and b.start < a.end`.

✅ Diagram saved, issues on GitHub, branch checked out.

### Step 3 · Explore the data (40–45 min)

💬 "Write a throwaway snippet (not committed) that prints the busiest stands, the overlapping allocations per stand, and the transfer bag counts per status."

✅ Your snippet finds the same number of conflicts the seed printed.

### Step 4 · Build `GET /api/gates/allocations` and `GET /api/gates/conflicts` (45–55 min)

💬 `/new-endpoint GET /api/gates/allocations?date= joined with flight_no`

💬 `/new-endpoint GET /api/gates/conflicts: overlapping allocations on the same stand with the overlap window`

💬 `/write-tests` with `gates.py` selected, including: touching intervals are not conflicts,
the seeded data has 3–5 conflicts.

💡 The `date` parameter is a Copenhagen calendar day: convert its start and end to UTC before
filtering. The stub uses `date_` with `alias="date"` because `date` is also the type name.

✅ `pytest` green; conflicts endpoint returns 3–5 items.

### Step 5 · Build `GET /api/baggage/at-risk` (55–62 min)

💬 `/new-endpoint GET /api/baggage/at-risk: transfer bags whose connection (outbound EOBT or SOBT minus inbound EIBT or SIBT) is below MCT 45 minutes, or whose outbound is cancelled, sorted by connection time`

💡 Join `transfer_bag` to `flight` twice (inbound and outbound) using aliases
(`sqlalchemy.orm.aliased(Flight)`). Return synthetic tag numbers only.

🤖 Optional: assign this issue to the **Copilot coding agent** and build the UI meanwhile.

✅ About 90 bags are returned (AT_RISK + MISSED), tightest connections first.

### Step 6 · Gantt chart, conflict list and bags (62–72 min)

1. 💬 "In gates.js render a Chart.js Gantt from /api/gates/allocations: indexAxis 'y', floating bars [start, end] in minutes since midnight Copenhagen time, one row per stand, conflicts from /api/gates/conflicts in --status-critical with a label. Destroy the old chart before re-rendering."
2. 💬 "Below it, add the conflict list and a bags-at-risk count and table from /api/baggage/at-risk with .chip status labels."

💡 Chart.js time axes need a date adapter; a **linear axis in minutes** with a tick callback
that prints `HH:MM` avoids an extra library. Show only stands that have allocations, or filter
by pier, so the chart stays readable. Give the canvas an `aria-label` and keep the tables as
the accessible alternative.

✅ Gantt, conflicts and bag table render; colours come from the theme.

### Step 7 · Headline numbers and clean-up (72–75 min)

💬 "Add a summary row at the top of the gates tab: number of conflicts and bags at risk, using .kpi styling. Remove the matching HACK(gates) comments."

✅ Only unfinished `HACK(gates)` markers remain.

### Step 8 · Expose `get_bags_at_risk` to the assistant (75–95 min)

1. Read [assistant-and-finale.md](assistant-and-finale.md).
2. 💬 "Use the copilot-sdk-tool skill to expose my bags-at-risk function as the read-only Copilot SDK tool get_bags_at_risk (params: limit, max_connection_min) and register it in build_tools()."
3. Ask: "Which outbound flights have the most transfer bags at risk, and from which gates?"

✅ The answer matches your table.

### Step 9 · Tests, review and PR (95–110 min)

💬 `/write-tests` on `gates.py` · "@reviewer Review the gates track changes." · "Fix the 🔴 and 🟠 findings."

Push, open a PR, request a **Copilot code review**, address comments.

✅ `pytest` green, reviewer **Ready for PR**.

### Step 10 · Demo (110–120 min)

Show the Gantt with a highlighted conflict, the bags-at-risk list and the assistant answering
a baggage question.

### Troubleshooting

| Symptom | Fix |
|---|---|
| "This method is not implemented: Check that a complete date adapter is provided" | You used a Chart.js `time` axis: switch to a linear axis in minutes. |
| Conflicts count is 0 | Check the overlap test (`a.start < b.end and b.start < a.end`) and that you compare allocations on the same stand. Re-run the seed and check `stand_conflicts`. |
| Join returns wrong flights | Use two aliases of `Flight` for inbound and outbound. |
| Gantt unreadable | Filter to one pier or the next 6 hours. |
