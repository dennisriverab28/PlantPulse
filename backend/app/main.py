import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db import Base, engine
from .routers import dashboard, devices, health
from .simulator.runner import simulator_loop


@asynccontextmanager
async def lifespan(app: FastAPI):
    # create_all keeps the scaffold simple; swap for Alembic migrations in slice 1.
    Base.metadata.create_all(engine)
    task = asyncio.create_task(simulator_loop()) if settings.simulator_enabled else None
    yield
    if task:
        task.cancel()


app = FastAPI(
    title="PlantPulse API",
    description=(
        "Embedded fleet operations hub: live device telemetry from test benches, "
        "lab inventory, firmware-validation reports, AI copilot."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(devices.router)
app.include_router(dashboard.router)
