"""
Seed helpers.
- seed_master_data(): inserts workers + workstations (idempotent).
- seed_events(): clears events then inserts a NEW synthetic shift each run.

Now generates dynamic timestamps + randomized production
so dashboard metrics change every time evaluators click
"Generate Dummy Shift".
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.crud import (
    create_worker,
    create_station,
    delete_all_events,
    insert_event,
)

# ---------------------------------------------------------------------------
# Master data
# ---------------------------------------------------------------------------

WORKERS = [
    ("W1", "Alice Chen", "Assembly", "Morning"),
    ("W2", "Bob Martinez", "QA Inspector", "Morning"),
    ("W3", "Carol Singh", "Assembly", "Morning"),
    ("W4", "David Kim", "Machine Operator", "Morning"),
    ("W5", "Emma Patel", "Packaging", "Afternoon"),
    ("W6", "Frank Okonkwo", "Assembly", "Afternoon"),
]

STATIONS = [
    ("S1", "Assembly Line A", "Assembly", "Line 1"),
    ("S2", "Assembly Line B", "Assembly", "Line 1"),
    ("S3", "QA Station", "Quality Control", "Line 2"),
    ("S4", "CNC Machine 1", "Machining", "Line 2"),
    ("S5", "Packaging Unit", "Packaging", "Line 3"),
    ("S6", "Sub-Assembly Bay", "Assembly", "Line 3"),
]

WORKER_STATION_MAP = {
    "W1": "S1",
    "W2": "S3",
    "W3": "S2",
    "W4": "S4",
    "W5": "S5",
    "W6": "S6",
}


def seed_master_data(db: Session) -> None:
    for worker_id, name, role, shift in WORKERS:
        create_worker(db, worker_id, name, role, shift)

    for station_id, name, station_type, line in STATIONS:
        create_station(db, station_id, name, station_type, line)


# ---------------------------------------------------------------------------
# Synthetic shift generator
# ---------------------------------------------------------------------------

def _build_shift_events(
    worker_id: str,
    station_id: str,
    base_time: datetime,
    shift_hours: int,
    rng: random.Random,
) -> list[dict]:

    events: list[dict] = []

    t = base_time
    shift_end = base_time + timedelta(hours=shift_hours)

    while t < shift_end:

        # working period
        work_duration = timedelta(minutes=rng.randint(6, 22))
        segments = rng.randint(2, 7)

        for i in range(segments):
            events.append(
                {
                    "timestamp": t + (work_duration / segments) * i,
                    "worker_id": worker_id,
                    "workstation_id": station_id,
                    "event_type": "working",
                    "confidence": round(rng.uniform(0.82, 0.99), 2),
                    "count": 0,
                }
            )

        t += work_duration

        # production output
        events.append(
            {
                "timestamp": t,
                "worker_id": worker_id,
                "workstation_id": station_id,
                "event_type": "product_count",
                "confidence": 0.99,
                "count": rng.randint(1, 6),   # dynamic production
            }
        )

        # idle chance
        if rng.random() < 0.35:

            idle_duration = timedelta(minutes=rng.randint(3, 12))
            idle_segments = rng.randint(1, 3)

            for i in range(idle_segments):
                events.append(
                    {
                        "timestamp": t + (idle_duration / idle_segments) * i,
                        "worker_id": worker_id,
                        "workstation_id": station_id,
                        "event_type": "idle",
                        "confidence": round(rng.uniform(0.75, 0.95), 2),
                        "count": 0,
                    }
                )

            t += idle_duration

    return events


# ---------------------------------------------------------------------------
# Seed events
# ---------------------------------------------------------------------------

def seed_events(db: Session, clear_first: bool = True) -> int:

    if clear_first:
        delete_all_events(db)

    # ✅ NEW SHIFT EVERY TIME
    now = datetime.now(timezone.utc)

    # shift started sometime in last 4 hours
    base_time = now - timedelta(hours=random.randint(1, 4))

    shift_hours = random.randint(7, 9)

    # different randomness each run
    rng = random.Random()

    all_events: list[dict] = []

    for worker_id, station_id in WORKER_STATION_MAP.items():
        all_events.extend(
            _build_shift_events(
                worker_id,
                station_id,
                base_time,
                shift_hours,
                rng,
            )
        )

    all_events.sort(key=lambda e: e["timestamp"])

    inserted = 0

    for ev in all_events:
        _, is_dup = insert_event(db, ev)
        if not is_dup:
            inserted += 1

    return inserted