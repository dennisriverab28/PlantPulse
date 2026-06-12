"""Background loop that streams simulated device telemetry into the database."""

import asyncio
import logging

from sqlalchemy import select

from ..config import settings
from ..db import SessionLocal
from ..models import Alert, Device, SensorReading
from .engine import DeviceSimulator, is_anomalous

logger = logging.getLogger(__name__)

# Live registry so API endpoints (e.g. anomaly injection) can reach simulators.
simulators: dict[int, DeviceSimulator] = {}

SEED_DEVICES = [
    ("EDGE-01", "Bench A", "ESP32 edge gateway", "v2.4.1"),
    ("HIL-02", "Bench A", "STM32 HIL test rig", "v1.9.0"),
    ("SENSE-03", "Bench B", "nRF52 sensor node", "v3.1.2"),
    ("VISION-04", "Bench B", "i.MX8 vision module", "v0.8.7"),
]


def seed_devices() -> list[Device]:
    with SessionLocal() as db:
        devices = db.scalars(select(Device)).all()
        if not devices:
            db.add_all(
                Device(name=name, bench=bench, device_type=dtype, firmware_version=fw)
                for name, bench, dtype, fw in SEED_DEVICES
            )
            db.commit()
            devices = db.scalars(select(Device)).all()
        return list(devices)


def record_tick() -> None:
    with SessionLocal() as db:
        for sim in simulators.values():
            for r in sim.tick():
                db.add(SensorReading(**r))
                if is_anomalous(r["metric"], r["value"], r["recorded_at"], sim.phase):
                    open_alert = db.scalar(
                        select(Alert).where(
                            Alert.device_id == r["device_id"],
                            Alert.metric == r["metric"],
                            Alert.acknowledged.is_(False),
                        )
                    )
                    if open_alert is None:
                        db.add(
                            Alert(
                                device_id=r["device_id"],
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
    devices = await asyncio.to_thread(seed_devices)
    for d in devices:
        simulators[d.id] = DeviceSimulator(d.id, seed=d.id)
    logger.info("simulator started for %d devices", len(simulators))
    try:
        while True:
            await asyncio.to_thread(record_tick)
            await asyncio.sleep(settings.simulator_interval_seconds)
    except asyncio.CancelledError:
        logger.info("simulator stopped")
        raise
