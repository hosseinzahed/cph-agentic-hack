"""Automation hand-off: actions for a robot (for example UiPath) to pick up.

Guide: docs/uipath-handoff.md
Data: ``automation_queue``. The app writes PENDING actions; a robot polls, then marks them DONE.
"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlmodel import Session

from backend.app.db import get_session
from backend.app.models import ActionSource, ActionStatus, ActionType

router = APIRouter(prefix="/api/automation", tags=["automation"])


class ActionIn(BaseModel):
    action_type: ActionType
    payload: dict[str, Any]


class ActionOut(BaseModel):
    id: int
    action_type: ActionType
    payload_json: str
    status: ActionStatus
    created_at: datetime
    source: ActionSource


@router.post("/actions", response_model=ActionOut, status_code=201)
def create_action(action: ActionIn, session: Session = Depends(get_session)) -> ActionOut:
    """Queue an action (REBOOK, NOTIFY or REASSIGN_STAND) in automation_queue as PENDING."""
    # HACK(disruptions): write the action to automation_queue (e.g. rebooking priorities)
    raise HTTPException(
        status_code=501,
        detail="HACK(disruptions): build POST /api/automation/actions (write to automation_queue)",
    )


@router.get("/actions", response_model=list[ActionOut])
def list_actions(
    status: ActionStatus | None = Query(default=None, description="Filter, e.g. PENDING"),
    session: Session = Depends(get_session),
) -> list[ActionOut]:
    """List queued actions, optionally filtered by status (robots poll status=PENDING)."""
    # HACK(disruptions): list automation_queue rows, newest first
    raise HTTPException(
        status_code=501,
        detail="HACK(disruptions): build GET /api/automation/actions (read automation_queue)",
    )
