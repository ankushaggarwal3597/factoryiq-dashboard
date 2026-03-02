from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

VALID_EVENT_TYPES = {"working", "idle", "absent", "product_count"}


# ---------------------------------------------------------------------------
# Inbound (request) schemas
# ---------------------------------------------------------------------------

class EventIn(BaseModel):
    timestamp: datetime = Field(..., description="ISO 8601 UTC timestamp")
    worker_id: str = Field(..., description="e.g. 'W1'")
    workstation_id: str = Field(..., description="e.g. 'S3'")
    event_type: str = Field(..., description="working | idle | absent | product_count")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    count: int = Field(default=0, ge=0, description="Units produced (product_count only)")
    event_id: Optional[str] = Field(default=None, description="Optional UUID for deduplication")
    model_version: Optional[str] = Field(default="v1.0")

    @field_validator("event_type")
    @classmethod
    def validate_event_type(cls, v: str) -> str:
        if v not in VALID_EVENT_TYPES:
            raise ValueError(f"event_type must be one of {VALID_EVENT_TYPES}")
        return v


class BulkEventsIn(BaseModel):
    events: list[EventIn]


# ---------------------------------------------------------------------------
# Outbound (response) schemas
# ---------------------------------------------------------------------------

class EventIngestResponse(BaseModel):
    status: str
    id: Optional[int] = None
    message: Optional[str] = None


class BulkIngestResponse(BaseModel):
    accepted: int
    duplicates: int
    errors: list[dict]


class WorkerOut(BaseModel):
    worker_id: str
    name: str
    role: str
    shift: str

    model_config = {"from_attributes": True}


class StationOut(BaseModel):
    station_id: str
    name: str
    station_type: str
    line: str

    model_config = {"from_attributes": True}


class WorkerMetrics(BaseModel):
    worker_id: str
    name: str
    role: str
    shift: str
    active_time_secs: int
    idle_time_secs: int
    utilization_pct: float
    total_units: int
    units_per_hour: float


class StationMetrics(BaseModel):
    station_id: str
    name: str
    station_type: str
    line: str
    occupancy_time_secs: int
    utilization_pct: float
    total_units: int
    throughput_rate: float


class FactoryMetrics(BaseModel):
    total_active_time_secs: int
    total_production_count: int
    avg_production_rate: float
    avg_worker_utilization_pct: float
    avg_station_utilization_pct: float
    total_events_processed: int
    event_breakdown: dict[str, int]


class SeedResponse(BaseModel):
    status: str
    events_seeded: int


class HealthResponse(BaseModel):
    status: str
    version: str
    db: str