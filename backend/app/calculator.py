"""
Pure metric computation — zero DB calls, zero FastAPI imports.
Input: plain Python lists/dicts. Output: plain dicts.
Easily unit-testable in isolation.

Assumptions:
  - Duration of an event = time until the NEXT event for the same entity.
  - Last event in a session → DEFAULT_LAST_DURATION_MIN (5 min).
  - Duration capped at MAX_SEGMENT_MIN (30 min) to prevent stale-session
    inflation when a camera goes offline.
  - product_count events contribute to unit totals only; zero duration.
  - Station utilization denominator = SHIFT_HOURS (8-hour shift).
"""

from __future__ import annotations
from datetime import datetime, timezone

MAX_SEGMENT_MIN = 30
DEFAULT_LAST_DURATION_MIN = 5
SHIFT_HOURS = 8


def _parse_ts(ts: str) -> datetime:
    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    # Ensure timezone-aware for safe subtraction
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _segment_duration_secs(rows: list[dict], index: int) -> float:
    if index + 1 < len(rows):
        delta = (
            _parse_ts(rows[index + 1]["timestamp"]) - _parse_ts(rows[index]["timestamp"])
        ).total_seconds()
        return min(max(delta, 0), MAX_SEGMENT_MIN * 60)
    return DEFAULT_LAST_DURATION_MIN * 60


# ---------------------------------------------------------------------------
# Worker
# ---------------------------------------------------------------------------

def compute_worker_metrics(activity_events: list[dict], total_units: int) -> dict:
    active_secs = 0.0
    idle_secs = 0.0

    for i, row in enumerate(activity_events):
        dur = _segment_duration_secs(activity_events, i)
        if row["event_type"] == "working":
            active_secs += dur
        elif row["event_type"] in ("idle", "absent"):
            idle_secs += dur

    total_secs = active_secs + idle_secs
    utilization = (active_secs / total_secs * 100) if total_secs > 0 else 0.0
    active_hours = active_secs / 3600
    units_per_hour = (total_units / active_hours) if active_hours > 0 else 0.0

    return {
        "active_time_secs": round(active_secs),
        "idle_time_secs": round(idle_secs),
        "utilization_pct": round(utilization, 1),
        "total_units": total_units,
        "units_per_hour": round(units_per_hour, 2),
    }


# ---------------------------------------------------------------------------
# Station
# ---------------------------------------------------------------------------

def compute_station_metrics(activity_events: list[dict], total_units: int) -> dict:
    occupancy_secs = 0.0

    for i, row in enumerate(activity_events):
        if row["event_type"] == "working":
            occupancy_secs += _segment_duration_secs(activity_events, i)

    shift_secs = SHIFT_HOURS * 3600
    utilization = min(occupancy_secs / shift_secs * 100, 100.0)
    occupancy_hours = occupancy_secs / 3600
    throughput = (total_units / occupancy_hours) if occupancy_hours > 0 else 0.0

    return {
        "occupancy_time_secs": round(occupancy_secs),
        "utilization_pct": round(utilization, 1),
        "total_units": total_units,
        "throughput_rate": round(throughput, 2),
    }


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def compute_factory_metrics(
    worker_metrics: list[dict],
    station_metrics: list[dict],
    total_events: int,
    event_breakdown: dict[str, int],
) -> dict:
    total_active_secs = sum(m["active_time_secs"] for m in worker_metrics)
    total_units = sum(m["total_units"] for m in worker_metrics)

    avg_worker_util = (
        sum(m["utilization_pct"] for m in worker_metrics) / len(worker_metrics)
        if worker_metrics else 0.0
    )
    avg_station_util = (
        sum(m["utilization_pct"] for m in station_metrics) / len(station_metrics)
        if station_metrics else 0.0
    )
    active_hours = total_active_secs / 3600
    avg_rate = (total_units / active_hours) if active_hours > 0 else 0.0

    return {
        "total_active_time_secs": round(total_active_secs),
        "total_production_count": total_units,
        "avg_production_rate": round(avg_rate, 2),
        "avg_worker_utilization_pct": round(avg_worker_util, 1),
        "avg_station_utilization_pct": round(avg_station_util, 1),
        "total_events_processed": total_events,
        "event_breakdown": event_breakdown,
    }