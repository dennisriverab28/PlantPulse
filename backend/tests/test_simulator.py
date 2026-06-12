from datetime import datetime, timezone

from app.simulator.engine import METRIC_PROFILES, DeviceSimulator, is_anomalous


def test_tick_produces_all_metrics():
    sim = DeviceSimulator(device_id=1, seed=42)
    readings = sim.tick()
    assert {r["metric"] for r in readings} == set(METRIC_PROFILES)
    assert all(r["device_id"] == 1 for r in readings)


def test_normal_readings_are_not_anomalous():
    sim = DeviceSimulator(device_id=1, seed=42)
    at = datetime.now(timezone.utc)
    for r in sim.tick(at):
        assert not is_anomalous(r["metric"], r["value"], at, sim.phase)


def test_injected_anomaly_trips_detector_then_clears():
    sim = DeviceSimulator(device_id=1, seed=42)
    sim.inject_anomaly("cpu_temp", ticks=2)
    at = datetime.now(timezone.utc)

    for _ in range(2):
        readings = {r["metric"]: r for r in sim.tick(at)}
        assert is_anomalous("cpu_temp", readings["cpu_temp"]["value"], at, sim.phase)

    readings = {r["metric"]: r for r in sim.tick(at)}
    assert not is_anomalous("cpu_temp", readings["cpu_temp"]["value"], at, sim.phase)
