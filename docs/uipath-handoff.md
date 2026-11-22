# UiPath hand-off (optional)

← [Docs index](README.md)

The app can hand work to robots or people through the **`automation_queue`** table. This is
how an agentic app triggers real-world actions without calling other systems directly.

## The contract

| Column | Values |
|---|---|
| `action_type` | `REBOOK`, `NOTIFY`, `REASSIGN_STAND` |
| `payload_json` | JSON with what the robot needs (synthetic ids only) |
| `status` | `PENDING` → `PICKED_UP` → `DONE` |
| `created_at` | UTC timestamp |
| `source` | `APP` (written by this app) or `UIPATH` (written by a robot) |

Endpoints (stubs in `src/backend/app/routers/automation.py`, marked `HACK(disruptions)`):

- `POST /api/automation/actions` with `{"action_type": "REBOOK", "payload": {...}}` → writes a
  `PENDING` row and returns it (201).
- `GET /api/automation/actions?status=PENDING` → what a robot polls.
- Stretch: `PATCH /api/automation/actions/{id}` with `{"status": "DONE"}` so a robot can close it.

Example payloads:

```json
{"action_type": "REBOOK", "payload": {"flight_no": "SK1415", "reason": "Thunderstorms near FRA", "priority": 1}}
{"action_type": "NOTIFY", "payload": {"audience": "T3 security", "message": "Open 2 extra lanes at 16:45"}}
{"action_type": "REASSIGN_STAND", "payload": {"allocation_id": 42, "from": "C33", "to": "C35"}}
```

## With UiPath

If your team has UiPath access, build a robot that:

1. Polls `GET http://<your-machine>:8000/api/automation/actions?status=PENDING` every minute.
2. Performs the action (e.g. posts a Teams message for `NOTIFY`, or fills a form for `REBOOK`).
3. Marks the action `DONE` (via the stretch `PATCH` endpoint).

Run uvicorn with `--host 0.0.0.0` if the robot runs on another machine, and only on a trusted
network: the starter app has no authentication.

## Without UiPath

Show the queue in the UI as **"Pending robot actions"**: a small list or badge in your track's
tab, fed by `GET /api/automation/actions?status=PENDING`. The demo story is the same: the
assistant or the user proposes an action, a human confirms it, and it lands in the queue.

## Ground rules

- Synthetic data only in payloads: flight numbers, stand ids, counts. No passenger names.
- A human confirms every action the assistant proposes before it's written to the queue.
