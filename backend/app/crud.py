"""
CRUD layer — all database queries in one place.
Every function receives a SQLAlchemy Session and returns ORM objects or plain dicts.
No raw SQL strings; SQLAlchemy handles dialect differences between PostgreSQL and SQLite.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func, select, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Event, Worker, Workstation


# ---------------------------------------------------------------------------
# Workers
# ---------------------------------------------------------------------------

def get_all_workers(db: Session) -> list[Worker]:
    return db.execute(select(Worker).order_by(Worker.worker_id)).scalars().all()


def get_worker(db: Session, worker_id: str) -> Optional[Worker]:
    return db.get(Worker, worker_id)


def create_worker(db: Session, worker_id: str, name: str, role: str, shift: str) -> Worker:
    worker = Worker(worker_id=worker_id, name=name, role=role, shift=shift)
    db.merge(worker)   # INSERT … ON CONFLICT DO NOTHING equivalent via merge
    db.commit()
    return worker


# ---------------------------------------------------------------------------
# Workstations
# ---------------------------------------------------------------------------

def get_all_stations(db: Session) -> list[Workstation]:
    return db.execute(select(Workstation).order_by(Workstation.station_id)).scalars().all()


def get_station(db: Session, station_id: str) -> Optional[Workstation]:
    return db.get(Workstation, station_id)


def create_station(
    db: Session, station_id: str, name: str, station_type: str, line: str
) -> Workstation:
    station = Workstation(station_id=station_id, name=name, station_type=station_type, line=line)
    db.merge(station)
    db.commit()
    return station


# ---------------------------------------------------------------------------
# Events — write
# ---------------------------------------------------------------------------

def insert_event(db: Session, data: dict) -> tuple[Event, bool]:
    """
    Insert a single event.
    Returns (event, is_duplicate).
    Uses merge-on-conflict pattern safe for PostgreSQL.
    """
    event = Event(
        event_id=data.get("event_id"),
        timestamp=data["timestamp"],
        worker_id=data["worker_id"],
        workstation_id=data["workstation_id"],
        event_type=data["event_type"],
        confidence=data.get("confidence", 1.0),
        count=data.get("count", 0),
        model_version=data.get("model_version", "v1.0"),
        received_at=datetime.now(timezone.utc),
    )
    db.add(event)
    try:
        db.flush()
        db.refresh(event)
        return event, False
    except IntegrityError:
        db.rollback()
        return None, True  # duplicate event_id


def delete_all_events(db: Session) -> None:
    db.execute(delete(Event))
    db.commit()


# ---------------------------------------------------------------------------
# Events — read
# ---------------------------------------------------------------------------

def get_recent_events(
    db: Session,
    limit: int = 50,
    worker_id: Optional[str] = None,
    station_id: Optional[str] = None,
) -> list[dict]:
    stmt = (
        select(Event, Worker.name.label("worker_name"), Workstation.name.label("station_name"))
        .join(Worker, Event.worker_id == Worker.worker_id)
        .join(Workstation, Event.workstation_id == Workstation.station_id)
        .order_by(Event.timestamp.desc())
        .limit(limit)
    )
    if worker_id:
        stmt = stmt.where(Event.worker_id == worker_id)
    if station_id:
        stmt = stmt.where(Event.workstation_id == station_id)

    rows = db.execute(stmt).all()
    return [
        {**row.Event.to_dict(), "worker_name": row.worker_name, "station_name": row.station_name}
        for row in rows
    ]


def get_event_count(db: Session) -> int:
    return db.execute(select(func.count()).select_from(Event)).scalar_one()


def get_event_type_breakdown(db: Session) -> dict[str, int]:
    rows = db.execute(
        select(Event.event_type, func.count().label("cnt")).group_by(Event.event_type)
    ).all()
    return {row.event_type: row.cnt for row in rows}


# ---------------------------------------------------------------------------
# Raw data for metric computation
# ---------------------------------------------------------------------------

def get_activity_events_for_worker(db: Session, worker_id: str) -> list[dict]:
    """Return working/idle/absent events sorted by timestamp ASC."""
    rows = db.execute(
        select(Event.timestamp, Event.event_type, Event.confidence)
        .where(Event.worker_id == worker_id)
        .where(Event.event_type != "product_count")
        .order_by(Event.timestamp.asc())
    ).all()
    return [{"timestamp": r.timestamp.isoformat(), "event_type": r.event_type} for r in rows]


def get_total_units_for_worker(db: Session, worker_id: str) -> int:
    result = db.execute(
        select(func.coalesce(func.sum(Event.count), 0))
        .where(Event.worker_id == worker_id)
        .where(Event.event_type == "product_count")
    ).scalar_one()
    return int(result)


def get_activity_events_for_station(db: Session, station_id: str) -> list[dict]:
    rows = db.execute(
        select(Event.timestamp, Event.event_type)
        .where(Event.workstation_id == station_id)
        .where(Event.event_type != "product_count")
        .order_by(Event.timestamp.asc())
    ).all()
    return [{"timestamp": r.timestamp.isoformat(), "event_type": r.event_type} for r in rows]


def get_total_units_for_station(db: Session, station_id: str) -> int:
    result = db.execute(
        select(func.coalesce(func.sum(Event.count), 0))
        .where(Event.workstation_id == station_id)
        .where(Event.event_type == "product_count")
    ).scalar_one()
    return int(result)