"""
Database setup using SQLAlchemy Core (2.x style).

Why SQLAlchemy Core instead of raw psycopg2?
  - One codebase works with both PostgreSQL (production/Render) and
    SQLite (optional local fallback) — just change DATABASE_URL.
  - Connection pooling handled automatically (critical for Render's
    free-tier PostgreSQL which has a 97-connection limit).
  - pool_pre_ping=True drops stale connections that Render recycles.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase

from app.config import settings

engine = create_engine(
    settings.database_url,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_pre_ping=settings.db_pool_pre_ping,
    # Needed when DATABASE_URL uses the older "postgres://" scheme (Render sometimes does)
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# FastAPI dependency — yields a session, always closes it
# ---------------------------------------------------------------------------

def get_session() -> Session:
    """
    Use as a FastAPI dependency:
        def my_route(db: Session = Depends(get_session)): ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Table creation (used at startup; for production prefer Alembic migrations)
# ---------------------------------------------------------------------------

def init_db() -> None:
    """Create all tables if they don't exist yet."""
    from app import models  # noqa: F401 — ensures models are registered on Base
    Base.metadata.create_all(bind=engine)