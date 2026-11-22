"""Gates & baggage track: stand allocations, conflicts and transfer bags at risk.

Guide: docs/track-4-gates-and-baggage.md
Data: ``stand_allocation``, ``flight`` and ``transfer_bag``.
"""

from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlmodel import Session

from backend.app.db import get_session
from backend.app.models import BagStatus

router = APIRouter(prefix="/api", tags=["gates"])


class StandAllocationOut(BaseModel):
    # HACK(gates): adjust this response model to what your UI needs
    id: int
    flight_id: int
    flight_no: str
    stand: str
    start_time: datetime
    end_time: datetime


class StandConflictOut(BaseModel):
    # HACK(gates): adjust this response model to what your UI needs
    stand: str
    allocation_ids: list[int]
    overlap_start: datetime
    overlap_end: datetime


class BagAtRiskOut(BaseModel):
    # HACK(gates): adjust this response model to what your UI needs
    tag_no: str
    inbound_flight_no: str
    outbound_flight_no: str
    connection_min: int
    status: BagStatus


@router.get("/gates/allocations", response_model=list[StandAllocationOut])
def list_allocations(
    date_: date | None = Query(default=None, alias="date", description="Day (YYYY-MM-DD); default today"),
    session: Session = Depends(get_session),
) -> list[StandAllocationOut]:
    """Return stand allocations for one day (for the Gantt chart)."""
    # HACK(gates): return stand allocations for the day, joined with flight_no
    raise HTTPException(
        status_code=501,
        detail="HACK(gates): build GET /api/gates/allocations for the stand Gantt chart",
    )


@router.get("/gates/conflicts", response_model=list[StandConflictOut])
def list_conflicts(session: Session = Depends(get_session)) -> list[StandConflictOut]:
    """Return pairs of allocations that overlap on the same stand."""
    # HACK(gates): detect overlapping allocations on the same stand
    raise HTTPException(
        status_code=501,
        detail="HACK(gates): build GET /api/gates/conflicts (overlapping stand allocations)",
    )


@router.get("/baggage/at-risk", response_model=list[BagAtRiskOut])
def list_bags_at_risk(session: Session = Depends(get_session)) -> list[BagAtRiskOut]:
    """Return transfer bags whose connection is shorter than the minimum connection time."""
    # HACK(gates): return transfer bags at risk (short connections vs. MCT, delayed inbound)
    raise HTTPException(
        status_code=501,
        detail="HACK(gates): build GET /api/baggage/at-risk (transfer bags on tight connections)",
    )
