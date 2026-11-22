---
name: seed-data-generator
description: Extend src/backend/scripts/seed.py with new realistic, synthetic and deterministic Copenhagen Airport data (flights, queues, disruptions, stands, bags or new tables). Use when a track needs more or different seed data, or when adding a column or table to models.py.
---

# Seed data generator

`src/backend/scripts/seed.py` builds one synthetic "hack day" at CPH. Every machine must get the
**same data** and the data must **never contain real personal information**.

## Rules
1. **Deterministic.** Use only the `rng` (`random.Random(RANDOM_SEED)`) passed into the
   `make_*` functions. Never call `random.random()`, `uuid4()` or `datetime.now()` for data
   values. Only the date and the flight statuses depend on when the seed runs.
2. **Append, don't reorder.** Add new random draws *after* the existing ones (at the end of
   `seed_database()`), otherwise every existing row changes for everyone.
3. **Synthetic only.** No real names, e-mails, booking references or bag tags. Use clearly
   fake identifiers (e.g. `SYN0000123`, `PAX-000123`) and aggregate counts, not individuals.
4. **UTC in the database.** Build local CPH times with `local_to_utc(day, hour)`.
5. **Idempotent.** The script drops and recreates all tables; don't add migrations.
6. **Realistic, not real.** Use airports from `airports.csv`, plausible airlines/aircraft,
   morning (≈07:00) and evening (≈17:30) peaks via `peak_curve(hour)`.

## Steps
1. If you need a new column or table, add it to `src/backend/app/models.py` first (SQLModel,
   `__tablename__`, indexes on columns you filter by, foreign keys).
2. Write a `make_<thing>(rng, ...) -> list[Model]` function in `seed.py`, next to the others.
   Keep it short; put constants (lists of values, weights) at the top of the file.
3. Call it at the end of `seed_database()` and add the model to the `tables` list so its row
   count is printed.
4. If you want *deliberate* edge cases (conflicts, tight connections, severe disruptions), make
   them explicit and count them in the summary, like `stand_conflicts`.
5. Run `python src/backend/scripts/seed.py` twice and check the counts are identical.
6. Run `pytest`. Tests seed their own throwaway database with the same function.
7. Mention new data in your track guide section "Data you have" if other teams need it.

## Example: add a "crosswind" weather disruption

```python
# in make_disruptions(day): append, don't reorder
d(DisruptionType.WEATHER, "Strong crosswind at CPH", "Runway 04L/22R closed; single-runway ops.",
  55.618, 12.656, 15, 15.0, 17.0, 3),
```

## Example: a new table with aggregated, non-personal data

```python
class CheckinCounter(SQLModel, table=True):
    __tablename__ = "checkin_counter"
    id: int | None = Field(default=None, primary_key=True)
    terminal: Terminal = Field(index=True)
    slot_start: datetime = Field(index=True)
    open_counters: int
```

```python
def make_checkin_counters(rng: random.Random, day: date) -> list[CheckinCounter]:
    return [
        CheckinCounter(terminal=t, slot_start=local_to_utc(day, slot / 4),
                       open_counters=max(2, int(12 * peak_curve(slot / 4) * rng.uniform(0.8, 1.1))))
        for t in Terminal for slot in range(4 * 4, 23 * 4)
    ]
```
