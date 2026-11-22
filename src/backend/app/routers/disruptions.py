"""Disruptions track: active disruptions and their impact on flights and connections.

Guide: docs/track-3-disruptions.md
Data: ``disruption``, ``flight``, ``airport`` and ``transfer_bag``.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session

from backend.app.db import get_session
from backend.app.models import DisruptionType

router = APIRouter(prefix="/api/disruptions", tags=["disruptions"])


class DisruptionOut(BaseModel):
    # HACK(disruptions): adjust this response model to what your UI needs
    id: int
    type: DisruptionType
    title: str
    description: str
    lat: float
    lon: float
    radius_km: float
    starts_at: datetime
    ends_at: datetime
    severity: int


class DisruptionImpactOut(BaseModel):
    # HACK(disruptions): adjust this response model to what your UI needs
    disruption_id: int
    affected_flight_ids: list[int]
    affected_connections: int
    summary: str


@router.get("/active", response_model=list[DisruptionOut])
def list_active_disruptions(session: Session = Depends(get_session)) -> list[DisruptionOut]:
    """Return disruptions that are active now (starts_at <= now < ends_at)."""
    # HACK(disruptions): return active disruptions (for map circles and the KPI tile)
    raise HTTPException(
        status_code=501,
        detail="HACK(disruptions): build GET /api/disruptions/active",
    )


@router.get("/{disruption_id}/impact", response_model=DisruptionImpactOut)
def get_disruption_impact(
    disruption_id: int, session: Session = Depends(get_session)
) -> DisruptionImpactOut:
    """Return flights and connections affected by one disruption, or 404."""
    # HACK(disruptions): find flights whose route/airport is inside the circle during the window
    raise HTTPException(
        status_code=501,
        detail="HACK(disruptions): build GET /api/disruptions/{id}/impact (flights and connections affected)",
    )
