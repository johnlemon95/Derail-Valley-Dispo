from contextlib import asynccontextmanager
import json
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database.db_session import create_tables, SessionLocal
from backend.database import repository as repo
from backend.services.auth_service import hash_password
from backend.api import job_routes, fleet_routes, admin_routes
from backend.websockets.event_handlers import router as ws_router
from config.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    _seed_initial_data()
    yield


def _seed_initial_data() -> None:
    """Create admin user and load station master data on first run."""
    db = SessionLocal()
    try:
        if not repo.get_user_by_username(db, "admin"):
            repo.create_user(db, "admin", "Host / Admin", "Admin", hash_password("admin"))

        stations_file = Path("config/stations_db.json")
        if stations_file.exists():
            data = json.loads(stations_file.read_text(encoding="utf-8"))
            from backend.database.models import StationORM
            if db.query(StationORM).count() == 0:
                for s in data.get("stations", []):
                    db.add(StationORM(code=s["code"], name=s["name"], description=s["description"]))
                db.commit()
    finally:
        db.close()


app = FastAPI(
    title="Derail Valley Dispatcher",
    version="0.1.0",
    description="Multi-User Logistik & Dispo für Derail Valley",
    lifespan=lifespan,
)

# LAN-only server – wide CORS is acceptable for local game sessions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_routes.router, prefix="/api/admin", tags=["Admin"])
app.include_router(job_routes.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(fleet_routes.router, prefix="/api/fleet", tags=["Fleet"])
app.include_router(ws_router)


@app.get("/", tags=["Health"])
def health():
    return {"status": "online", "service": "Derail Valley Dispatcher", "version": "0.1.0"}
