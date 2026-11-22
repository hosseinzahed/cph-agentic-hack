"""SQLModel tables for the CPH operations database.

All datetimes are timezone-aware **UTC**. Convert to
Europe/Copenhagen only when you display them. All data is synthetic.
"""

from datetime import UTC, datetime
from enum import Enum

from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(UTC)


# ---------------------------------------------------------------- enums


class Direction(str, Enum):
    DEP = "DEP"
    ARR = "ARR"


class FlightStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    BOARDING = "BOARDING"
    DELAYED = "DELAYED"
    CANCELLED = "CANCELLED"
    DEPARTED = "DEPARTED"
    LANDED = "LANDED"


class Terminal(str, Enum):
    T2 = "T2"
    T3 = "T3"


class Checkpoint(str, Enum):
    CHECKIN = "CHECKIN"
    SECURITY = "SECURITY"
    PASSPORT = "PASSPORT"


class DisruptionType(str, Enum):
    WEATHER = "WEATHER"
    ATC = "ATC"
    STRIKE = "STRIKE"
    TECHNICAL = "TECHNICAL"


class BagStatus(str, Enum):
    ON_TIME = "ON_TIME"
    AT_RISK = "AT_RISK"
    MISSED = "MISSED"


class ActionType(str, Enum):
    REBOOK = "REBOOK"
    NOTIFY = "NOTIFY"
    REASSIGN_STAND = "REASSIGN_STAND"


class ActionStatus(str, Enum):
    PENDING = "PENDING"
    PICKED_UP = "PICKED_UP"
    DONE = "DONE"


class ActionSource(str, Enum):
    APP = "APP"
    UIPATH = "UIPATH"


# ---------------------------------------------------------------- tables


class Airport(SQLModel, table=True):
    __tablename__ = "airport"

    iata: str = Field(primary_key=True, max_length=3)
    name: str
    city: str
    country: str
    lat: float
    lon: float


class Flight(SQLModel, table=True):
    __tablename__ = "flight"

    id: int | None = Field(default=None, primary_key=True)
    flight_no: str = Field(index=True)
    airline: str
    direction: Direction = Field(index=True)
    origin_iata: str = Field(foreign_key="airport.iata", index=True)
    dest_iata: str = Field(foreign_key="airport.iata", index=True)
    sched_time: datetime = Field(index=True, description="SOBT/SIBT in UTC")
    est_time: datetime | None = Field(default=None, description="EOBT/EIBT in UTC")
    status: FlightStatus = Field(default=FlightStatus.SCHEDULED, index=True)
    terminal: Terminal
    gate: str | None = None
    aircraft_type: str
    pax_count: int


class PassengerFlow(SQLModel, table=True):
    __tablename__ = "passenger_flow"

    id: int | None = Field(default=None, primary_key=True)
    terminal: Terminal = Field(index=True)
    checkpoint: Checkpoint = Field(index=True)
    slot_start: datetime = Field(index=True, description="Start of a 15-minute slot (UTC)")
    pax_count: int
    avg_wait_min: float


class Disruption(SQLModel, table=True):
    __tablename__ = "disruption"

    id: int | None = Field(default=None, primary_key=True)
    type: DisruptionType
    title: str
    description: str
    lat: float
    lon: float
    radius_km: float
    starts_at: datetime = Field(index=True)
    ends_at: datetime = Field(index=True)
    severity: int = Field(ge=1, le=5, description="1 = minor, 5 = severe")


class StandAllocation(SQLModel, table=True):
    __tablename__ = "stand_allocation"

    id: int | None = Field(default=None, primary_key=True)
    flight_id: int = Field(foreign_key="flight.id", index=True)
    stand: str = Field(index=True)
    start_time: datetime
    end_time: datetime


class TransferBag(SQLModel, table=True):
    __tablename__ = "transfer_bag"

    id: int | None = Field(default=None, primary_key=True)
    tag_no: str = Field(unique=True, description="Synthetic bag tag number")
    inbound_flight_id: int = Field(foreign_key="flight.id", index=True)
    outbound_flight_id: int = Field(foreign_key="flight.id", index=True)
    status: BagStatus = Field(default=BagStatus.ON_TIME, index=True)


class AutomationQueue(SQLModel, table=True):
    __tablename__ = "automation_queue"

    id: int | None = Field(default=None, primary_key=True)
    action_type: ActionType
    payload_json: str = Field(description="JSON payload for the robot / handler")
    status: ActionStatus = Field(default=ActionStatus.PENDING, index=True)
    created_at: datetime = Field(default_factory=utc_now)
    source: ActionSource = Field(default=ActionSource.APP)
