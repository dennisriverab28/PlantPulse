"""Background loop that streams simulated telemetry into the database."""

import asyncio
import logging

from sqlalchemy import select

from ..config import settings
from ..db import SessionLocal
from ..models import Alert, Machine, SensorReading
from .engine import MachineSimulator, is_anomalous

logger = logging.getLogger(__name__)

# Live registry so API endpoints (e.g. anomaly injection) can reach simulators.
simulators: dict[int, MachineSimulator] = {}

SEED_MACHINES = [
    ("CNC-01", "Line A", "CNC mill"),
    ("PRESS-02", "Line A", "Hydraulic press"),
    ("WELD-03", "Line B", "Welding robot"),
    ("CONV-04", "Line B", "Conveyor"),
]


def seed_machines() -> list[Machine]:
    with SessionLocal() as db:
        machines = db.scalars(select(Machine)).all()
        if not machines:
            db.add_all(
                Machine(name=name, line=line, machine_type=mtype)
                for name, line, mtype in SEED_MACHINES
            )
            db.commit()
            machines = db.scalars(select(Machine)).all()
        return list(machines)


def record_tick() -> None:
    with SessionLocal() as db:
        for sim in simulators.values():
            for r in sim.tick():
                db.add(SensorReading(**r))
                if is_anomalous(r["metric"], r["value"], r["recorded_at"], sim.phase):
                    open_alert = db.scalar(
                        select(Alert).where(
                            Alert.machine_id == r["machine_id"],
                            Alert.metric == r["metric"],
                            Alert.acknowledged.is_(False),
                        )
                    )
                    if open_alert is None:
                        db.add(
                            Alert(
                                machine_id=r["machine_id"],
                                metric=r["metric"],
                                severity="critical",
                                message=(
                                    f"{r['metric']} out of band: "
                                    f"{r['value']} {r['unit']}"
                                ),
                            )
                        )
        db.commit()


async def simulator_loop() -> None:
    machines = await asyncio.to_thread(seed_machines)
    for m in machines:
        simulators[m.id] = MachineSimulator(m.id, seed=m.id)
    logger.info("simulator started for %d machines", len(simulators))
    try:
        while True:
            await asyncio.to_thread(record_tick)
            await asyncio.sleep(settings.simulator_interval_seconds)
    except asyncio.CancelledError:
        logger.info("simulator stopped")
        raise
