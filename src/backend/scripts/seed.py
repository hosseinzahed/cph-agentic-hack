"""Create the SQLite database and fill it with one synthetic "hack day" at CPH.

Run from the repository root:

    python src/backend/scripts/seed.py

* Idempotent: drops every table, recreates it and reseeds.
* Deterministic: a fixed random seed gives every machine the same data. Only the date
  (today in Europe/Copenhagen) and the flight statuses (relative to the time you run the
  seed) change. Re-run it to refresh the statuses.
* Timestamps are stored in UTC. All data is synthetic: no real flights, passengers or bags.
"""

from __future__ import annotations

import csv
import math
import random
import sys
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

SRC_DIR = Path(__file__).resolve().parents[2]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))  # allows `python src/backend/scripts/seed.py`

from sqlmodel import Session, SQLModel, func, select  # noqa: E402

from backend.app.db import DB_PATH, engine  # noqa: E402
from backend.app.models import (  # noqa: E402
    Airport,
    AutomationQueue,
    BagStatus,
    Checkpoint,
    Direction,
    Disruption,
    DisruptionType,
    Flight,
    FlightStatus,
    PassengerFlow,
    StandAllocation,
    Terminal,
    TransferBag,
)

RANDOM_SEED = 42
CPH_TZ = ZoneInfo("Europe/Copenhagen")
AIRPORTS_CSV = SRC_DIR / "backend" / "data" / "airports.csv"
MCT_MIN = 45  # minimum connection time used to label transfer bags

LONG_HAUL = {"EWR", "JFK", "ORD", "SFO", "BKK", "SIN", "HND", "DXB", "DOH"}
# Destination -> airlines that fly it (2-letter codes). Flight numbers are random.
AIRLINES_BY_DEST = {
    "LHR": ["SK", "BA"], "LGW": ["U2", "D8"], "DUB": ["SK", "FR"], "CDG": ["SK", "AF"],
    "AMS": ["SK", "KL"], "BRU": ["SK"], "FRA": ["SK", "LH"], "MUC": ["SK", "LH"],
    "BER": ["SK", "U2"], "HAM": ["SK"], "ZRH": ["SK", "LX"], "VIE": ["OS"], "WAW": ["LO"],
    "PRG": ["SK"], "RIX": ["BT"], "MAD": ["SK", "IB"], "BCN": ["SK", "VY"], "AGP": ["D8", "SK"],
    "LIS": ["TP"], "FCO": ["SK", "AZ"], "MXP": ["U2"], "ATH": ["SK", "A3"], "IST": ["TK"],
    "OSL": ["SK", "D8"], "BGO": ["SK", "D8"], "TRD": ["SK"], "ARN": ["SK", "D8"],
    "GOT": ["SK"], "HEL": ["AY", "SK"], "KEF": ["FI"], "AAL": ["SK", "DX"], "AAR": ["SK"],
    "BLL": ["DX"], "DXB": ["EK"], "DOH": ["QR"], "EWR": ["SK", "UA"], "JFK": ["SK"],
    "ORD": ["SK"], "SFO": ["SK"], "BKK": ["TG", "SK"], "SIN": ["SQ"], "HND": ["SK"],
}
SHORT_HAUL_TYPES = [("A320neo", 150, 180), ("A321neo", 180, 215), ("B737-800", 150, 186),
                    ("ATR72", 50, 70), ("CRJ900", 70, 90)]
LONG_HAUL_TYPES = [("A350-900", 280, 330), ("B787-9", 250, 290), ("B777-300ER", 320, 380)]

CONTACT_STANDS = (
    [f"A{n}" for n in range(4, 18)] + [f"B{n}" for n in range(1, 11)]
    + [f"C{n}" for n in range(26, 40)] + [f"D{n}" for n in range(1, 9)]
    + [f"E{n}" for n in range(20, 28)] + [f"F{n}" for n in range(1, 7)]
)


def local_to_utc(day: date, hour: float) -> datetime:
    """Convert a fractional local hour on `day` (Copenhagen) to a timezone-aware UTC datetime."""
    local = datetime.combine(day, time(0, 0), tzinfo=CPH_TZ) + timedelta(hours=hour)
    return local.astimezone(UTC)


def utc_now() -> datetime:
    return datetime.now(UTC)


def load_airports() -> list[Airport]:
    with AIRPORTS_CSV.open(encoding="utf-8") as f:
        rows = csv.DictReader(line for line in f if not line.startswith("#"))
        return [
            Airport(iata=r["iata"], name=r["name"], city=r["city"], country=r["country"],
                    lat=float(r["lat"]), lon=float(r["lon"]))
            for r in rows
        ]


def peak_curve(hour: float) -> float:
    """Relative traffic level (0..1+) with a morning and an evening peak."""
    morning = math.exp(-((hour - 7.0) ** 2) / 4.5)
    evening = 0.8 * math.exp(-((hour - 17.5) ** 2) / 6.0)
    return 0.15 + morning + evening


def make_flights(rng: random.Random, day: date, destinations: list[str], now: datetime) -> list[Flight]:
    flights: list[Flight] = []
    used_numbers: set[str] = set()
    long_haul = [d for d in destinations if d in LONG_HAUL]
    short_haul = [d for d in destinations if d not in LONG_HAUL]

    for direction in (Direction.DEP, Direction.ARR):
        for _ in range(150):
            other = rng.choice(long_haul) if rng.random() < 0.08 else rng.choice(short_haul)
            airline = rng.choice(AIRLINES_BY_DEST.get(other, ["SK"]))
            flight_no = f"{airline}{rng.randint(100, 2999)}"
            while flight_no in used_numbers:
                flight_no = f"{airline}{rng.randint(100, 2999)}"
            used_numbers.add(flight_no)

            # Busier around the peaks: sample an hour, keep it with probability ~ peak_curve.
            while True:
                hour = rng.uniform(5.5, 23.0)
                if rng.random() < peak_curve(hour) / 1.2:
                    break
            hour = round(hour * 12) / 12  # 5-minute grid
            sched = local_to_utc(day, hour)

            types = LONG_HAUL_TYPES if other in LONG_HAUL else SHORT_HAUL_TYPES
            aircraft, pax_min, pax_max = rng.choice(types)
            pax = rng.randint(int(pax_min * 0.6), pax_max)

            roll = rng.random()
            delay_min = rng.choice([15, 20, 30, 45, 60, 90, 120]) if roll < 0.15 else 0
            cancelled = 0.15 <= roll < 0.18
            est = sched + timedelta(minutes=delay_min) if delay_min else None
            status = flight_status(direction, sched, est, cancelled, now)

            flights.append(Flight(
                flight_no=flight_no, airline=airline, direction=direction,
                origin_iata="CPH" if direction == Direction.DEP else other,
                dest_iata=other if direction == Direction.DEP else "CPH",
                sched_time=sched, est_time=est, status=status,
                terminal=rng.choice([Terminal.T2, Terminal.T3, Terminal.T3]),
                gate=None, aircraft_type=aircraft, pax_count=pax,
            ))
    flights.sort(key=lambda f: f.sched_time)
    return flights


def flight_status(direction: Direction, sched: datetime, est: datetime | None,
                  cancelled: bool, now: datetime) -> FlightStatus:
    """Status as seen at `now` (the moment you run the seed)."""
    if cancelled:
        return FlightStatus.CANCELLED
    actual = est or sched
    if direction == Direction.DEP:
        if actual <= now:
            return FlightStatus.DEPARTED
        if actual - now <= timedelta(minutes=30):
            return FlightStatus.BOARDING
    elif actual <= now:
        return FlightStatus.LANDED
    return FlightStatus.DELAYED if est else FlightStatus.SCHEDULED


def make_passenger_flow(rng: random.Random, day: date) -> list[PassengerFlow]:
    rows: list[PassengerFlow] = []
    base = {Checkpoint.CHECKIN: 260, Checkpoint.SECURITY: 420, Checkpoint.PASSPORT: 120}
    capacity = {Checkpoint.CHECKIN: 110, Checkpoint.SECURITY: 170, Checkpoint.PASSPORT: 60}
    for terminal in (Terminal.T2, Terminal.T3):
        scale = 0.8 if terminal == Terminal.T2 else 1.0
        for slot in range(4 * 4, 23 * 4):  # 04:00 .. 22:45 local, 15-minute slots
            hour = slot / 4
            for checkpoint in Checkpoint:
                pax = int(base[checkpoint] * scale * peak_curve(hour) * rng.uniform(0.85, 1.15))
                load = pax / (capacity[checkpoint] * 2.5)  # ~2.5 lanes/desks open per slot
                wait = max(1.0, 2.0 + 32.0 * max(0.0, load - 0.4) ** 1.2 + rng.uniform(-1, 1))
                rows.append(PassengerFlow(
                    terminal=terminal, checkpoint=checkpoint,
                    slot_start=local_to_utc(day, hour), pax_count=pax,
                    avg_wait_min=round(wait, 1),
                ))
    return rows


def make_disruptions(day: date) -> list[Disruption]:
    def d(kind, title, desc, lat, lon, radius, start_h, end_h, sev) -> Disruption:
        return Disruption(type=kind, title=title, description=desc, lat=lat, lon=lon,
                          radius_km=radius, starts_at=local_to_utc(day, start_h),
                          ends_at=local_to_utc(day, end_h), severity=sev)

    return [
        d(DisruptionType.WEATHER, "Fog at CPH", "Low visibility procedures, reduced arrival rate.",
          55.618, 12.656, 25, 4.0, 9.5, 3),
        d(DisruptionType.ATC, "ATC flow restriction at LHR", "Arrival slots reduced by 20 percent.",
          51.470, -0.462, 60, 7.0, 21.0, 3),
        d(DisruptionType.WEATHER, "Thunderstorms near FRA", "Convective weather, holding and diversions likely.",
          50.20, 8.40, 90, 13.0, 19.0, 4),
        d(DisruptionType.STRIKE, "Ground-handling strike (scenario) at CDG",
          "Synthetic scenario: reduced ramp handling capacity.", 49.010, 2.548, 15, 10.0, 18.0, 4),
        d(DisruptionType.TECHNICAL, "Baggage sorter degraded at CPH T3",
          "One sorter line offline; transfer bags slower.", 55.629, 12.648, 2, 11.0, 15.0, 2),
        d(DisruptionType.WEATHER, "Snow and de-icing at OSL", "De-icing queues add 20-30 minutes.",
          60.194, 11.100, 40, 6.0, 12.0, 2),
    ]


def overlaps(a: StandAllocation, b: StandAllocation) -> bool:
    return a.start_time < b.end_time and b.start_time < a.end_time


def count_conflicts(allocs: list[StandAllocation]) -> int:
    by_stand: dict[str, list[StandAllocation]] = {}
    for a in allocs:
        by_stand.setdefault(a.stand, []).append(a)
    return sum(
        1 for group in by_stand.values()
        for i, a in enumerate(group) for b in group[i + 1:] if overlaps(a, b)
    )


def make_stand_allocations(rng: random.Random, flights: list[Flight]) -> list[StandAllocation]:
    allocs: list[StandAllocation] = []
    busy_until: dict[str, datetime] = {s: datetime.min.replace(tzinfo=UTC) for s in CONTACT_STANDS}
    remote = 0
    for f in flights:
        if f.status == FlightStatus.CANCELLED or rng.random() < 0.05:
            continue  # most flights, not all, get a stand
        t = f.est_time or f.sched_time
        if f.direction == Direction.DEP:
            start, end = t - timedelta(minutes=rng.choice([60, 75, 90])), t + timedelta(minutes=10)
        else:
            start, end = t - timedelta(minutes=10), t + timedelta(minutes=rng.choice([45, 60, 75]))
        free = [s for s in CONTACT_STANDS if busy_until[s] <= start]
        if free:
            stand = rng.choice(free)
            busy_until[stand] = end
            f.gate = stand
        else:
            remote += 1
            stand = f"R{80 + remote}"
        allocs.append(StandAllocation(flight_id=f.id, stand=stand, start_time=start, end_time=end))

    # Inject deliberate conflicts: move an allocation onto another stand at the same time.
    flights_by_id = {f.id: f for f in flights}
    target = rng.randint(3, 5)
    conflicts = count_conflicts(allocs)
    attempts = 0
    while conflicts < target and attempts < 1000:
        attempts += 1
        a, b = rng.sample(allocs, 2)
        if a.stand == b.stand or b.stand.startswith("R") or not overlaps(a, b):
            continue
        added = sum(1 for x in allocs if x.stand == a.stand and overlaps(b, x))
        if conflicts + added <= 5:
            b.stand = a.stand
            flights_by_id[b.flight_id].gate = a.stand
            conflicts = count_conflicts(allocs)
    return allocs


def make_transfer_bags(rng: random.Random, flights: list[Flight]) -> list[TransferBag]:
    arrivals = [f for f in flights if f.direction == Direction.ARR and f.status != FlightStatus.CANCELLED]
    departures = [f for f in flights if f.direction == Direction.DEP]
    bags: list[TransferBag] = []
    while len(bags) < 500:
        inbound = rng.choice(arrivals)
        short = rng.random() < 0.12  # deliberately tight connections
        window = (20, MCT_MIN - 1) if short else (MCT_MIN, 240)
        candidates = [
            d for d in departures
            if window[0] <= (d.sched_time - inbound.sched_time).total_seconds() / 60 <= window[1]
        ]
        if not candidates:
            continue
        outbound = rng.choice(candidates)
        inbound_on_blocks = inbound.est_time or inbound.sched_time
        outbound_off_blocks = outbound.est_time or outbound.sched_time
        connection = (outbound_off_blocks - inbound_on_blocks).total_seconds() / 60
        if outbound.status == FlightStatus.CANCELLED or connection < 15:
            status = BagStatus.MISSED
        elif connection < MCT_MIN:
            status = BagStatus.AT_RISK
        else:
            status = BagStatus.ON_TIME
        bags.append(TransferBag(
            tag_no=f"SYN{len(bags) + 1:07d}",  # obviously synthetic tag numbers
            inbound_flight_id=inbound.id, outbound_flight_id=outbound.id, status=status,
        ))
    return bags


def seed_database() -> dict[str, int]:
    """Drop, recreate and fill every table. Returns row counts per table."""
    rng = random.Random(RANDOM_SEED)
    day = datetime.now(CPH_TZ).date()
    now = utc_now()

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        airports = load_airports()
        session.add_all(airports)
        session.commit()

        destinations = [a.iata for a in airports if a.iata != "CPH"]
        flights = make_flights(rng, day, destinations, now)
        session.add_all(flights)
        session.commit()  # assigns flight ids

        allocs = make_stand_allocations(rng, flights)
        session.add_all(allocs)
        session.add_all(flights)  # gate numbers were set during allocation
        session.add_all(make_passenger_flow(rng, day))
        session.add_all(make_disruptions(day))
        session.add_all(make_transfer_bags(rng, flights))
        session.commit()

        tables = [Airport, Flight, PassengerFlow, Disruption, StandAllocation, TransferBag, AutomationQueue]
        counts = {t.__tablename__: session.exec(select(func.count()).select_from(t)).one() for t in tables}
        counts["stand_conflicts"] = count_conflicts(allocs)
    return counts


def main() -> None:
    counts = seed_database()
    print(f"Seeded {DB_PATH} with synthetic data for {datetime.now(CPH_TZ).date()} (Europe/Copenhagen):")
    for name, n in counts.items():
        print(f"  {name:<18} {n:>5}")


if __name__ == "__main__":
    main()
