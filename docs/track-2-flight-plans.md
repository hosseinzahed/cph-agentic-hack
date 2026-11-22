# Track 2 · Flight plans (`flights`)

← [Docs index](README.md) · [Workshop flow](workshop-flow.md) · Next: [Assistant & finale](assistant-and-finale.md)

> Jump to the **[step-by-step walkthrough](#step-by-step-walkthrough)** once you've skimmed sections 1–10.

## 1. Goal

Draw today's CPH route network on the world map, colour-coded by flight status, and build the
departures and arrivals board with a working flight search.

## 2. Why it matters at CPH

CPH is the Nordic hub: about 300 movements a day connect Scandinavia with Europe, the Gulf,
Asia and North America. A live network view shows at a glance where delays and cancellations
cluster, and the board is what passengers and staff check every few minutes.

## 3. Data you have

Table `flight` (300 rows: 150 departures, 150 arrivals, about 30 long-haul):

| Column | Type | Notes |
|---|---|---|
| `id` | int | Primary key |
| `flight_no`, `airline` | str | Synthetic numbers, e.g. `SK1415`; airline code `SK` |
| `direction` | `DEP` / `ARR` | |
| `origin_iata`, `dest_iata` | str → `airport.iata` | One end is always `CPH` |
| `sched_time` | datetime (UTC) | SOBT for departures, SIBT for arrivals |
| `est_time` | datetime (UTC) or null | EOBT/EIBT, set when delayed |
| `status` | `SCHEDULED` / `BOARDING` / `DELAYED` / `CANCELLED` / `DEPARTED` / `LANDED` | Relative to when the seed ran (re-run it to refresh) |
| `terminal`, `gate` | str | `T2`/`T3`; gate = contact stand label (e.g. `C33`) or null |
| `aircraft_type`, `pax_count` | str, int | |

Table `airport` (43 rows): `iata`, `name`, `city`, `country`, `lat`, `lon`, already served by the
reference endpoint `GET /api/airports`.

## 4. Endpoints to implement

File: `src/backend/app/routers/flights.py`

| Method and path | Returns | Notes |
|---|---|---|
| `GET /api/flights?direction=&from=&to=` | `list[FlightOut]` | Filter by `DEP`/`ARR` and a UTC time window on `sched_time`; sorted by time. |
| `GET /api/flights/routes` | `RouteCollectionOut` (GeoJSON) | A `FeatureCollection` with one `LineString` per route from CPH; `properties` such as `dest_iata`, `city`, `flights`, `status`. |

## 5. UI to build

File: `src/frontend/tracks/flights.js` (tab **Flight plans**), plus the search box and KPI tile in
`src/frontend/index.html`.

- **World route map**: great-circle lines from CPH, colour-coded by status (on time, delayed,
  cancelled) with a **legend**. Layer name `flights:routes`.
- **Departures and arrivals board**: a `.board` table (Midnight Blue header, zebra rows) with
  time (local), flight, destination/origin, gate, and a status **chip with a text label**;
  a DEP/ARR toggle.
- **Flight search box** ("Find departures and arrivals"): enable it and filter the board by
  flight number or city.
- **KPI tile** "Departures next hour" (`data-kpi="departures-next-hour"`).

## 6. Assistant tool to expose

`get_flights(direction: "DEP" | "ARR" | None, hours_ahead: int = 2, status: str | None)` returns
the matching flights (flight number, local time, other airport, status, gate) as compact JSON.
It lets the assistant answer "Which departures to London are delayed this afternoon?".

## 7. Copilot capabilities to try

| Capability | Use it for |
|---|---|
| `@architect` agent | API contract for the board and GeoJSON, `docs/diagrams/flights-flow.drawio`. |
| `/new-endpoint`, `/write-tests` prompt files | Scaffold both endpoints with tests. |
| `@map-builder` agent + `leaflet-map` skill | Great-circle routes, legend, popups. |
| `frontend.instructions.md` | Board styling with `.board` and `.chip`, local time formatting. |
| `copilot-sdk-tool` skill | Expose `get_flights`. |
| Copilot coding agent | Good candidate: assign the "flight search box" issue. |

Example prompts:
- `/new-endpoint GET /api/flights/routes returning a GeoJSON FeatureCollection, one LineString per route from CPH`
- "@map-builder Draw /api/flights/routes as great-circle lines coloured by status with a legend."
- "Render a departures board in flights.js from /api/flights?direction=DEP using the .board and .chip styles."

## 8. Definition of done

- [ ] `GET /api/flights` and `GET /api/flights/routes` return data and are tested; both removed from `STUBS`.
- [ ] Routes are drawn as great-circle lines in status colours with a legend.
- [ ] The board shows departures and arrivals in Copenhagen time with labelled status chips.
- [ ] The flight search filters the board and is keyboard-accessible.
- [ ] "Departures next hour" shows a number.
- [ ] `get_flights` is a Copilot SDK tool the assistant uses.
- [ ] All `HACK(flights)` markers are gone; `pytest` green; `@reviewer` says Ready for PR.

## 9. Stretch goals

- **Auto-refresh**: refresh the board and KPI every 60 seconds without redrawing the whole map.
- **Route explorer**: click a route to filter the board to that destination; show flights per
  day and airlines in the popup.
- **CO₂ estimate**: estimated CO₂ per route from great-circle distance (see idea 5 in
  [hack-ideas.md](hack-ideas.md)).

## 10. `HACK` markers

| File | Marker (what to build) |
|---|---|
| `src/backend/app/routers/flights.py` | `FlightOut`: adjust this response model to what your UI needs |
| `src/backend/app/routers/flights.py` | `list_flights`: query the flight table with the filters (and its 501 detail) |
| `src/backend/app/routers/flights.py` | `get_routes`: build a GeoJSON FeatureCollection (and its 501 detail) |
| `src/frontend/tracks/flights.js` | build the world route map here (routes, board, KPI) |
| `src/frontend/index.html` | fill "Departures next hour" from GET /api/flights |
| `src/frontend/index.html` | enable the flight search (filter the board by flight number or destination) |

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

Times follow [workshop-flow.md](workshop-flow.md). Suggested split: one person on the API, one on
the map, one on the board and search.

### Step 0 · Get running (0–10 min)

> **First, get the code:** 🍴 **fork** or 📥 **clone** the repo and run the setup script, as
> described in [getting-started.md](getting-started.md). Your choice decides where your issues,
> branch and pull request go in steps 2 and 9.

🎯 App running, everyone knows the track's files.

1. `python src/scripts/check_env.py`, then `uvicorn backend.app.main:app --app-dir src --reload`
   and open http://localhost:8000.
2. Open the **Flight plans** tab: "🚧 HACK(flights): build the world route map here".
3. In http://localhost:8000/docs, `GET /api/flights` returns **501**.

💬 `/explain-this-repo` (track: `flights`)

💬 "List every HACK(flights) marker with a link and one line on what to build."

✅ You can name the 6 markers in section 10 and find `addLayer` and `cssVar` in `app.js`.

### Step 1 · Tune Copilot for this track (10–25 min)

1. Read `.github/copilot-instructions.md` (glossary: SOBT/EOBT, stand vs. gate) and
   `.github/instructions/frontend.instructions.md`.
2. Add a rule that matters for you, e.g. in `frontend.instructions.md`: "Flight times are shown
   as HH:MM Copenhagen time; delayed flights show the scheduled time struck through and the new time."
3. Add one instruction file from awesome-copilot (attribution kept, `applyTo` under `src/`).

💬 "What does the glossary in copilot-instructions.md say about SOBT, EOBT and gates? How does that map to the flight table?"

✅ One small instruction change committed.

### Step 2 · Plan with `@architect` (25–40 min)

1. Select **architect**; start the MCP servers when asked.
2. 💬 "Plan the flights track for a team of 3. Propose the API contract for /api/flights and the GeoJSON shape of /api/flights/routes with example JSON, and a task breakdown."
3. 💬 "Draw the end-to-end flow for the flights track: UI map, board and search → FastAPI flights router → flight and airport tables → get_flights Copilot SDK tool. Save it to docs/diagrams/flights-flow.drawio."
4. Create the issues and the branch. The prompt depends on your path ([getting-started.md](getting-started.md)):
   - 🍴 Fork: 💬 "Create the issues and the branch track/flights in <you>/cph-agentic-hack."
   - 📥 Clone with write access: 💬 "We are team <team>. Create the issues and the branch <team>/flights in hosseinzahed/cph-agentic-hack."
   - 📥 Clone, local only: skip the issues and run `git switch -c track/flights`.

   Then `git fetch` and check out the branch.

💡 Agree on the GeoJSON `properties` now (e.g. `dest_iata`, `city`, `flights`, `delayed`,
`cancelled`, `status`): the map and the backend depend on the same names.

✅ Diagram saved, issues on GitHub, branch checked out.

### Step 3 · Explore the data (40–45 min)

💬 "Write a throwaway snippet (not committed) using the project's SQLModel engine that prints departures per destination, the long-haul destinations, and how many flights are DELAYED or CANCELLED."

💡 Long-haul routes (EWR, JFK, ORD, SFO, BKK, SIN, HND, DXB, DOH) make the world map look good;
zoom out to see them.

✅ You know the top destinations and that one end of every flight is CPH.

### Step 4 · Build `GET /api/flights` (45–55 min)

💬 `/new-endpoint GET /api/flights?direction=&from=&to= for the flights track`

💬 `/write-tests` with `flights.py` selected.

💡 `from` is a keyword: the stub uses `from_` with `alias="from"`. Add `where` clauses only for
the filters that were given, and sort by `sched_time`. Return UTC; convert in the UI.

✅ `pytest` green; `/api/flights?direction=DEP` returns only departures, in time order.

### Step 5 · Build `GET /api/flights/routes` (55–62 min)

💬 `/new-endpoint GET /api/flights/routes: a GeoJSON FeatureCollection with one LineString per destination from CPH, properties dest_iata, city, flights, delayed, cancelled and a summary status`

💡 GeoJSON coordinates are **`[lon, lat]`** (Leaflet uses `[lat, lon]`). Group flights by the
non-CPH airport. A two-point LineString is fine on the server; the client can turn it into a
great circle. Pick the "worst" status per route for the colour.

🤖 Optional: assign the "flight search box" issue to the **Copilot coding agent**.

✅ The response validates as GeoJSON (paste it into https://geojson.io to check) and has one
feature per destination.

### Step 6 · Draw routes and the board (62–72 min)

1. 💬 "@map-builder In flights.js fetch /api/flights/routes and draw great-circle lines from CPH coloured by status with a legend, using the leaflet-map skill snippets. Layer name flights:routes."
2. 💬 "Add a departures/arrivals board below it: a .board table from /api/flights with a DEP/ARR toggle, local HH:MM times, gate, and .chip status labels."

💡 `greatCircle()` and `splitAtAntimeridian()` are in `.github/skills/leaflet-map/snippets.js`.
Colours via `statusColour()` / `cssVar()`. Escape popup text. Status chips need text, not just
colour.

✅ Routes and board render; no console errors; colours match the legend.

### Step 7 · Search box, KPI tile and clean-up (72–75 min)

💬 "Enable the flight search in index.html: filter the board in flights.js by flight number or city as the user types (debounced), keep it keyboard-accessible, and fill the Departures next hour KPI tile from /api/flights. Remove the matching HACK(flights) comments."

✅ Typing `SK` or `London` filters the board; the KPI shows a number.

### Step 8 · Expose `get_flights` to the assistant (75–95 min)

1. Read [assistant-and-finale.md](assistant-and-finale.md).
2. 💬 "Use the copilot-sdk-tool skill to expose my flight query function as the read-only Copilot SDK tool get_flights (params: direction, hours_ahead, status) and register it in build_tools()."
3. Ask the assistant: "Which departures in the next two hours are delayed, and to where?"

✅ The answer matches the board.

### Step 9 · Tests, review and PR (95–110 min)

💬 `/write-tests` on `flights.py` · "@reviewer Review the flights track changes." · "Fix the 🔴 and 🟠 findings."

Push, open a PR that closes your issues, request a **Copilot code review**, address comments.
The push and PR commands depend on your path: see the table in
[workshop-flow.md](workshop-flow.md#95110--tests-review-and-pr). 🍴 **Fork users:** set the PR's
**base repository** to your fork (GitHub defaults to the original repo).

✅ `pytest` green, reviewer **Ready for PR**.

### Step 10 · Demo (110–120 min)

Show the world map zoomed out, filter the board with the search box, and ask the assistant a
flight question.

### Troubleshooting

| Symptom | Fix |
|---|---|
| Routes appear in the wrong place (Africa/ocean) | Swapped coordinates: GeoJSON `[lon, lat]` vs Leaflet `[lat, lon]`. |
| Long-haul line wraps around the world | Split at the antimeridian, or use great-circle points. |
| All statuses `SCHEDULED` or all `DEPARTED` | Statuses depend on when the seed ran: `python src/backend/scripts/seed.py`. |
| Times are 1 hour off | You displayed UTC. Use `timeZone: "Europe/Copenhagen"`. |
