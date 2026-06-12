from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Machine, SensorReading
from ..schemas import AnomalyRequest, MachineOut, ReadingOut
from ..simulator.runner import simulators

router = APIRouter(prefix="/api/machines", tags=["machines"])


@router.get("", response_model=list[MachineOut])
def list_machines(db: Session = Depends(get_db)):
    return db.scalars(select(Machine).order_by(Machine.name)).all()


@router.get("/{machine_id}/readings", response_model=list[ReadingOut])
def machine_readings(
    machine_id: int,
    metric: str = "temperature",
    limit: int = 50,
    db: Session = Depends(get_db),
):
    if db.get(Machine, machine_id) is None:
        raise HTTPException(404, "machine not found")
    rows = db.scalars(
        select(SensorReading)
        .where(SensorReading.machine_id == machine_id, SensorReading.metric == metric)
        .order_by(SensorReading.recorded_at.desc())
        .limit(min(limit, 500))
    ).all()
    return list(reversed(rows))


@router.post("/{machine_id}/anomaly", status_code=202)
def inject_anomaly(machine_id: int, body: AnomalyRequest):
    sim = simulators.get(machine_id)
    if sim is None:
        raise HTTPException(409, "simulator is not running for this machine")
    try:
        sim.inject_anomaly(body.metric, body.ticks)
    except ValueError as e:
        raise HTTPException(422, str(e))
    return {"injected": body.metric, "ticks": body.ticks}
