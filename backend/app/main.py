from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import SessionLocal
from app.config import settings
from app.database import init_db, get_session
from app.crud import get_all_workers, get_all_stations
from app.seed import seed_master_data, seed_events
from app.routes.events import router as events_router
from app.routes.metrics import router as metrics_router
from app.schemas import SeedResponse, HealthResponse, WorkerOut, StationOut
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="FactoryIQ API",
    version="1.0.0",
    description="AI-powered factory productivity dashboard — PostgreSQL backend",
)

origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://factoryiq-dashboard.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events_router, prefix="/api")
app.include_router(metrics_router, prefix="/api")


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------

@app.on_event("startup")
def on_startup():
    init_db()

    db = SessionLocal()

    try:
        # Seed workers + stations
        seed_master_data(db)

        # ✅ Auto seed events if database empty
        from app.models import Event
        from sqlalchemy import select, func

        existing_events = db.execute(
            select(func.count()).select_from(Event)
        ).scalar_one()

        if existing_events == 0:
            print("Seeding initial factory shift...")
            seed_events(db, clear_first=True)

    finally:
        db.close()


# ---------------------------------------------------------------------------
# System routes
# ---------------------------------------------------------------------------
@app.get("/")
def root():
    return {"message": "FactoryIQ API running"}

@app.get("/api/health", response_model=HealthResponse, tags=["System"])
def health(db: Session = Depends(get_session)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {e}"

    return HealthResponse(
        status="ok",
        version="1.0.0",
        db=db_status,
    )


@app.get("/api/workers", response_model=list[WorkerOut], tags=["Workers"])
def list_workers(db: Session = Depends(get_session)):
    return get_all_workers(db)


@app.get("/api/workstations", response_model=list[StationOut], tags=["Workstations"])
def list_workstations(db: Session = Depends(get_session)):
    return get_all_stations(db)


@app.post("/api/seed-dummy-data", response_model=SeedResponse, tags=["System"])
def seed_dummy_data(db: Session = Depends(get_session)):
    """Clear events and regenerate a full synthetic shift."""
    n = seed_events(db, clear_first=True)
    return SeedResponse(status="ok", events_seeded=n)