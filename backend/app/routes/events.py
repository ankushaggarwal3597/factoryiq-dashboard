from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.crud import (
    get_worker,
    get_station,
    insert_event,
    get_recent_events,
    delete_all_events,
)
from app.database import get_session
from app.schemas import (
    BulkEventsIn,
    BulkIngestResponse,
    EventIn,
    EventIngestResponse,
)

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("", response_model=EventIngestResponse, status_code=201)
def ingest_event(event: EventIn, db: Session = Depends(get_session)):
    """Ingest a single AI-generated CCTV event."""
    if not get_worker(db, event.worker_id):
        raise HTTPException(404, f"Worker '{event.worker_id}' not found")
    if not get_station(db, event.workstation_id):
        raise HTTPException(404, f"Workstation '{event.workstation_id}' not found")

    new_event, is_dup = insert_event(db, event.model_dump())
    if is_dup:
        return EventIngestResponse(status="duplicate", message="Already processed")
    return EventIngestResponse(status="ok", id=new_event.id)


@router.post("/bulk", response_model=BulkIngestResponse, status_code=201)
def ingest_bulk(payload: BulkEventsIn, db: Session = Depends(get_session)):
    """Ingest multiple events (replay / catch-up after connectivity loss)."""
    accepted, duplicates, errors = 0, 0, []

    for ev in payload.events:
        try:
            result = ingest_event(ev, db)
            if result.status == "duplicate":
                duplicates += 1
            else:
                accepted += 1
        except HTTPException as exc:
            errors.append({"event": ev.model_dump(), "error": exc.detail})

    return BulkIngestResponse(accepted=accepted, duplicates=duplicates, errors=errors)


@router.get("/recent")
def recent_events(
    limit: int = Query(default=50, le=500),
    worker_id: Optional[str] = Query(default=None),
    station_id: Optional[str] = Query(default=None),
    db: Session = Depends(get_session),
):
    return get_recent_events(db, limit=limit, worker_id=worker_id, station_id=station_id)


@router.delete("", status_code=200)
def clear_events(db: Session = Depends(get_session)):
    delete_all_events(db)
    return {"status": "ok", "message": "All events deleted"}