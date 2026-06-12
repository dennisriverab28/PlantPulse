from datetime import timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Alert, Device, DeviceStatus, SensorReading, utcnow
from ..schemas import AlertOut, DashboardSummary

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def summary(db: Session = Depends(get_db)):
    hour_ago = utcnow() - timedelta(hours=1)
    return DashboardSummary(
        devices_total=db.scalar(select(func.count(Device.id))) or 0,
        devices_online=db.scalar(
            select(func.count(Device.id)).where(Device.status == DeviceStatus.online)
        )
        or 0,
        alerts_open=db.scalar(
            select(func.count(Alert.id)).where(Alert.acknowledged.is_(False))
        )
        or 0,
        readings_last_hour=db.scalar(
            select(func.count(SensorReading.id)).where(SensorReading.recorded_at >= hour_ago)
        )
        or 0,
    )


@router.get("/alerts", response_model=list[AlertOut])
def open_alerts(db: Session = Depends(get_db)):
    return db.scalars(
        select(Alert)
        .where(Alert.acknowledged.is_(False))
        .order_by(Alert.created_at.desc())
        .limit(20)
    ).all()
