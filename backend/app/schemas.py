from datetime import datetime

from pydantic import BaseModel, ConfigDict

from .models import DeviceStatus, ReadingSource


class DeviceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    bench: str
    device_type: str
    firmware_version: str
    status: DeviceStatus


class ReadingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: int
    metric: str
    value: float
    unit: str
    source: ReadingSource
    recorded_at: datetime


class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: int | None
    metric: str
    severity: str
    message: str
    acknowledged: bool
    created_at: datetime


class AnomalyRequest(BaseModel):
    metric: str = "cpu_temp"
    ticks: int = 12


class DashboardSummary(BaseModel):
    devices_total: int
    devices_online: int
    alerts_open: int
    readings_last_hour: int
