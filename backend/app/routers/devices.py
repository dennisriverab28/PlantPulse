from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Device, SensorReading
from ..schemas import AnomalyRequest, DeviceOut, ReadingOut
from ..simulator.runner import simulators

router = APIRouter(prefix="/api/devices", tags=["devices"])


@router.get("", response_model=list[DeviceOut])
def list_devices(db: Session = Depends(get_db)):
    return db.scalars(select(Device).order_by(Device.name)).all()


@router.get("/{device_id}/readings", response_model=list[ReadingOut])
def device_readings(
    device_id: int,
    metric: str = "cpu_temp",
    limit: int = 50,
    db: Session = Depends(get_db),
):
    if db.get(Device, device_id) is None:
        raise HTTPException(404, "device not found")
    rows = db.scalars(
        select(SensorReading)
        .where(SensorReading.device_id == device_id, SensorReading.metric == metric)
        .order_by(SensorReading.recorded_at.desc())
        .limit(min(limit, 500))
    ).all()
    return list(reversed(rows))


@router.post("/{device_id}/anomaly", status_code=202)
def inject_anomaly(device_id: int, body: AnomalyRequest):
    sim = simulators.get(device_id)
    if sim is None:
        raise HTTPException(409, "simulator is not running for this device")
    try:
        sim.inject_anomaly(body.metric, body.ticks)
    except ValueError as e:
        raise HTTPException(422, str(e))
    return {"injected": body.metric, "ticks": body.ticks}
