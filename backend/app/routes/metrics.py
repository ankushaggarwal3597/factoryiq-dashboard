from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.crud import (
    get_all_workers,
    get_all_stations,
    get_activity_events_for_worker,
    get_total_units_for_worker,
    get_activity_events_for_station,
    get_total_units_for_station,
    get_event_count,
    get_event_type_breakdown,
)
from app.database import get_session
from app.calculator import (
    compute_worker_metrics,
    compute_station_metrics,
    compute_factory_metrics,
)
from app.schemas import FactoryMetrics, StationMetrics, WorkerMetrics

router = APIRouter(prefix="/metrics", tags=["Metrics"])


def _worker_metrics(db: Session, worker) -> WorkerMetrics:
    activity = get_activity_events_for_worker(db, worker.worker_id)
    units = get_total_units_for_worker(db, worker.worker_id)
    computed = compute_worker_metrics(activity, units)
    return WorkerMetrics(**worker.to_dict(), **computed)


def _station_metrics(db: Session, station) -> StationMetrics:
    activity = get_activity_events_for_station(db, station.station_id)
    units = get_total_units_for_station(db, station.station_id)
    computed = compute_station_metrics(activity, units)
    return StationMetrics(**station.to_dict(), **computed)


@router.get("/workers", response_model=list[WorkerMetrics])
def worker_metrics(
    worker_id: Optional[str] = Query(default=None),
    db: Session = Depends(get_session),
):
    workers = get_all_workers(db)
    if worker_id:
        workers = [w for w in workers if w.worker_id == worker_id]
    return [_worker_metrics(db, w) for w in workers]


@router.get("/workstations", response_model=list[StationMetrics])
def station_metrics(
    station_id: Optional[str] = Query(default=None),
    db: Session = Depends(get_session),
):
    stations = get_all_stations(db)
    if station_id:
        stations = [s for s in stations if s.station_id == station_id]
    return [_station_metrics(db, s) for s in stations]


@router.get("/factory", response_model=FactoryMetrics)
def factory_metrics(db: Session = Depends(get_session)):
    workers = get_all_workers(db)
    stations = get_all_stations(db)

    w_metrics = [_worker_metrics(db, w).model_dump() for w in workers]
    s_metrics = [_station_metrics(db, s).model_dump() for s in stations]

    return compute_factory_metrics(
        w_metrics,
        s_metrics,
        get_event_count(db),
        get_event_type_breakdown(db),
    )