"""Flight plans track: departures, arrivals and the route network from CPH.

Guide: docs/track-2-flight-plans.md
Data: ``flight`` joined with ``airport`` for coordinates.
"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlmodel import Session

from backend.app.db import get_session
from backend.app.models import Direction, FlightStatus

router = APIRouter(prefix="/api/flights", tags=["flights"])


class FlightOut(BaseModel):
    # HACK(flights): adjust this response model to what your UI needs
    id: int
    flight_no: str
    airline: str
    direction: Direction
    origin_iata: str
    dest_iata: str
    sched_time: datetime
    est_time: datetime | None
    status: FlightStatus
    terminal: str
    gate: str | None


class RouteCollectionOut(BaseModel):
    """A GeoJSON FeatureCollection of LineString features (one per route from CPH)."""

    type: str = "FeatureCollection"
    features: list[dict[str, Any]]


@router.get("", response_model=list[FlightOut])
def list_flights(
    direction: Direction | None = Query(default=None, description="DEP or ARR; omit for both"),
    from_: datetime | None = Query(default=None, alias="from", description="Start (UTC)"),
    to: datetime | None = Query(default=None, description="End (UTC)"),
    session: Session = Depends(get_session),
) -> list[FlightOut]:
    """Return flights filtered by direction and scheduled-time window, sorted by time."""
    # HACK(flights): query the flight table with the filters (departures/arrivals board)
    raise HTTPException(
        status_code=501,
        detail="HACK(flights): build GET /api/flights for the departures and arrivals board",
    )


@router.get("/routes", response_model=RouteCollectionOut)
def get_routes(session: Session = Depends(get_session)) -> RouteCollectionOut:
    """Return the CPH route network as GeoJSON for the world map."""
    # HACK(flights): build a GeoJSON FeatureCollection: one LineString per route with status props
    raise HTTPException(
        status_code=501,
        detail="HACK(flights): build GET /api/flights/routes (GeoJSON routes for the world map)",
    )
