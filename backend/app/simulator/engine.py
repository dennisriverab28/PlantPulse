"""Telemetry generation for simulated plant-floor machines.

Each metric follows a slow sinusoidal duty cycle plus gaussian noise, so charts
look like real industrial telemetry instead of random static. Anomalies can be
injected per-machine to drive a metric out of its normal band for N ticks.
"""

import math
import random
from datetime import datetime, timezone

METRIC_PROFILES: dict[str, dict] = {
    "temperature": {"base": 68.0, "amplitude": 6.0, "noise": 1.5, "unit": "°C", "period_s": 3600},
    "vibration": {"base": 2.4, "amplitude": 0.6, "noise": 0.25, "unit": "mm/s", "period_s": 900},
    "rpm": {"base": 1750.0, "amplitude": 40.0, "noise": 20.0, "unit": "rpm", "period_s": 1800},
    "throughput": {"base": 120.0, "amplitude": 15.0, "noise": 6.0, "unit": "units/hr", "period_s": 7200},
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


class MachineSimulator:
    def __init__(self, machine_id: int, seed: int | None = None):
        self.machine_id = machine_id
        self.rng = random.Random(seed)
        # A per-machine phase offset so machines don't move in lockstep.
        self.phase = self.rng.uniform(0, 2 * math.pi)
        self.anomaly_metric: str | None = None
        self.anomaly_ticks = 0

    def inject_anomaly(self, metric: str = "temperature", ticks: int = 12) -> None:
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
                    "machine_id": self.machine_id,
                    "metric": metric,
                    "value": round(value, 2),
                    "unit": p["unit"],
                    "recorded_at": at,
                }
            )
        if self.anomaly_ticks > 0:
            self.anomaly_ticks -= 1
            if self.anomaly_ticks == 0:
                self.anomaly_metric = None
        return readings
