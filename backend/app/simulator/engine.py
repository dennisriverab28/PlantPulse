"""Telemetry generation for simulated embedded devices on test benches.

Each metric follows a slow sinusoidal duty cycle plus gaussian noise, so charts
look like real device telemetry instead of random static. Anomalies can be
injected per-device to drive a metric out of its normal band for N ticks —
e.g. a thermal runaway, a sagging supply rail, or a heap leak.
"""

import math
import random
from datetime import datetime, timezone

METRIC_PROFILES: dict[str, dict] = {
    "cpu_temp": {"base": 52.0, "amplitude": 6.0, "noise": 1.2, "unit": "°C", "period_s": 3600},
    "supply_voltage": {"base": 3.30, "amplitude": 0.04, "noise": 0.015, "unit": "V", "period_s": 1800},
    "current_draw": {"base": 180.0, "amplitude": 45.0, "noise": 10.0, "unit": "mA", "period_s": 900},
    "free_heap": {"base": 148.0, "amplitude": 16.0, "noise": 5.0, "unit": "KB", "period_s": 7200},
}

# Beyond this many noise-deviations from the expected curve, a reading is anomalous.
ALERT_SIGMA = 4.0


def expected_value(metric: str, at: datetime, phase: float = 0.0) -> float:
    p = METRIC_PROFILES[metric]
    t = at.timestamp()
    return p["base"] + p["amplitude"] * math.sin(2 * math.pi * t / p["period_s"] + phase)


def is_anomalous(metric: str, value: float, at: datetime, phase: float = 0.0) -> bool:
    p = METRIC_PROFILES[metric]
    return abs(value - expected_value(metric, at, phase)) > ALERT_SIGMA * p["noise"]


class DeviceSimulator:
    def __init__(self, device_id: int, seed: int | None = None):
        self.device_id = device_id
        self.rng = random.Random(seed)
        # A per-device phase offset so devices don't move in lockstep.
        self.phase = self.rng.uniform(0, 2 * math.pi)
        self.anomaly_metric: str | None = None
        self.anomaly_ticks = 0

    def inject_anomaly(self, metric: str = "cpu_temp", ticks: int = 12) -> None:
        if metric not in METRIC_PROFILES:
            raise ValueError(f"unknown metric: {metric}")
        self.anomaly_metric = metric
        self.anomaly_ticks = ticks

    def tick(self, at: datetime | None = None) -> list[dict]:
        at = at or datetime.now(timezone.utc)
        readings = []
        for metric, p in METRIC_PROFILES.items():
            value = expected_value(metric, at, self.phase) + self.rng.gauss(0, p["noise"])
            if metric == self.anomaly_metric and self.anomaly_ticks > 0:
                # Push the value well past the alert threshold.
                value += (ALERT_SIGMA + 2) * p["noise"] + 0.5 * p["amplitude"]
            readings.append(
                {
                    "device_id": self.device_id,
                    "metric": metric,
                    "value": round(value, 3),
                    "unit": p["unit"],
                    "recorded_at": at,
                }
            )
        if self.anomaly_ticks > 0:
            self.anomaly_ticks -= 1
            if self.anomaly_ticks == 0:
                self.anomaly_metric = None
        return readings
