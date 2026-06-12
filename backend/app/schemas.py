from datetime import datetime

from pydantic import BaseModel, ConfigDict

from .models import MachineStatus, ReadingSource


class MachineOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    line: str
    machine_type: str
    status: MachineStatus


class ReadingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    machine_id: int
    metric: str
    value: float
    unit: str
    source: ReadingSource
    recorded_at: datetime


class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    machine_id: int | None
    metric: str
    severity: str
    message: str
    acknowledged: bool
    created_at: datetime


class AnomalyRequest(BaseModel):
    metric: str = "temperature"
    ticks: int = 12


class DashboardSummary(BaseModel):
    machines_total: int
    machines_running: int
    alerts_open: int
    readings_last_hour: int
