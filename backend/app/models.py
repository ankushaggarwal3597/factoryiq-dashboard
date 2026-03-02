"""
ORM table definitions.

Notes on PostgreSQL compatibility:
  - Primary keys use server_default=text("gen_random_uuid()") where UUIDs are
    needed; integer PKs use Identity() which maps to SERIAL/IDENTITY in PG.
  - No SQLite-isms: no AUTOINCREMENT keyword, no PRAGMA, no strftime().
  - Timestamps stored as DateTime(timezone=True) → TIMESTAMPTZ in PostgreSQL
    (stores UTC, reads back as UTC-aware datetime objects).
  - Index names are explicit to avoid Alembic migration conflicts.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# ---------------------------------------------------------------------------
# Workers
# ---------------------------------------------------------------------------

class Worker(Base):
    __tablename__ = "workers"

    worker_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(100), nullable=False)
    shift: Mapped[str] = mapped_column(String(50), nullable=False)

    events: Mapped[list["Event"]] = relationship(back_populates="worker")

    def to_dict(self) -> dict:
        return {
            "worker_id": self.worker_id,
            "name": self.name,
            "role": self.role,
            "shift": self.shift,
        }


# ---------------------------------------------------------------------------
# Workstations
# ---------------------------------------------------------------------------

class Workstation(Base):
    __tablename__ = "workstations"

    station_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    station_type: Mapped[str] = mapped_column(String(100), nullable=False)
    line: Mapped[str] = mapped_column(String(50), nullable=False)

    events: Mapped[list["Event"]] = relationship(back_populates="workstation")

    def to_dict(self) -> dict:
        return {
            "station_id": self.station_id,
            "name": self.name,
            "station_type": self.station_type,
            "line": self.line,
        }


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------

class Event(Base):
    __tablename__ = "events"

    # BigInteger maps to BIGSERIAL in PostgreSQL — handles high event volumes
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Optional client-supplied UUID for idempotent ingestion
    event_id: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)

    # Use DateTime(timezone=True) → TIMESTAMPTZ in PostgreSQL
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),  # DB fills this if not supplied
    )

    worker_id: Mapped[str] = mapped_column(
        String(10), ForeignKey("workers.worker_id"), nullable=False
    )
    workstation_id: Mapped[str] = mapped_column(
        String(10), ForeignKey("workstations.station_id"), nullable=False
    )
    event_type: Mapped[str] = mapped_column(String(30), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    model_version: Mapped[str | None] = mapped_column(String(50), default="v1.0")

    worker: Mapped["Worker"] = relationship(back_populates="events")
    workstation: Mapped["Workstation"] = relationship(back_populates="events")

    # Explicit index names avoid Alembic autogenerate conflicts
    __table_args__ = (
        Index("ix_events_worker_id", "worker_id"),
        Index("ix_events_workstation_id", "workstation_id"),
        Index("ix_events_timestamp", "timestamp"),
        Index("ix_events_event_type", "event_type"),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "received_at": self.received_at.isoformat() if self.received_at else None,
            "worker_id": self.worker_id,
            "workstation_id": self.workstation_id,
            "event_type": self.event_type,
            "confidence": self.confidence,
            "count": self.count,
            "model_version": self.model_version,
        }