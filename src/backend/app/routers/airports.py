"""Airports API: the ONE implemented reference endpoint.

Copy this pattern for every track endpoint:

* a Pydantic response model (``AirportOut``),
* type hints and a docstring on every route,
* the database session injected with ``Depends(get_session)``,
* ``HTTPException(404)`` for missing items,
* a test in ``src/backend/tests/`` (see ``test_airports.py``).
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from backend.app.db import get_session
from backend.app.models import Airport

router = APIRouter(prefix="/api", tags=["airports"])


class AirportOut(BaseModel):
    iata: str
    name: str
    city: str
    country: str
    lat: float
    lon: float


@router.get("/airports", response_model=list[AirportOut])
def list_airports(session: Session = Depends(get_session)) -> list[Airport]:
    """Return every airport with its coordinates, sorted by IATA code."""
    return list(session.exec(select(Airport).order_by(Airport.iata)).all())


@router.get("/airports/{iata}", response_model=AirportOut)
def get_airport(iata: str, session: Session = Depends(get_session)) -> Airport:
    """Return one airport by its 3-letter IATA code (case-insensitive), or 404."""
    airport = session.get(Airport, iata.upper())
    if airport is None:
        raise HTTPException(status_code=404, detail=f"Airport {iata.upper()} not found")
    return airport
