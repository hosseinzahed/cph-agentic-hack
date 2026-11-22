"""Passenger onboarding track: queues and wait-time forecasts at CPH checkpoints.

Guide: docs/track-1-passenger-onboarding.md
Data: ``passenger_flow`` (15-minute slots per terminal and checkpoint).
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlmodel import Session

from backend.app.db import get_session
from backend.app.models import Checkpoint, Terminal

router = APIRouter(prefix="/api/onboarding", tags=["onboarding"])


class QueueSlotOut(BaseModel):
    # HACK(onboarding): adjust this response model to what your UI needs
    terminal: Terminal
    checkpoint: Checkpoint
    slot_start: datetime
    pax_count: int
    avg_wait_min: float


class QueueForecastOut(BaseModel):
    # HACK(onboarding): adjust this response model to what your UI needs
    terminal: Terminal
    checkpoint: Checkpoint
    slot_start: datetime
    predicted_wait_min: float


@router.get("/queues", response_model=list[QueueSlotOut])
def get_queues(
    terminal: Terminal | None = Query(default=None, description="T2 or T3; omit for both"),
    from_: datetime | None = Query(default=None, alias="from", description="Start (UTC)"),
    to: datetime | None = Query(default=None, description="End (UTC)"),
    session: Session = Depends(get_session),
) -> list[QueueSlotOut]:
    """Return passenger-flow slots, filtered by terminal and time window."""
    # HACK(onboarding): query passenger_flow with the filters and return the slots
    raise HTTPException(
        status_code=501,
        detail="HACK(onboarding): build GET /api/onboarding/queues from the passenger_flow table",
    )


@router.get("/forecast", response_model=list[QueueForecastOut])
def get_forecast(
    terminal: Terminal | None = Query(default=None, description="T2 or T3; omit for both"),
    session: Session = Depends(get_session),
) -> list[QueueForecastOut]:
    """Return a wait-time forecast for the coming hours per terminal and checkpoint."""
    # HACK(onboarding): forecast avg_wait_min for the next slots (start simple: moving average)
    raise HTTPException(
        status_code=501,
        detail="HACK(onboarding): build GET /api/onboarding/forecast (wait-time forecast per checkpoint)",
    )
