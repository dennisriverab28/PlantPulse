import os

os.environ["SIMULATOR_ENABLED"] = "false"
os.environ["DATABASE_URL"] = "sqlite://"

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


def test_health():
    with TestClient(app) as client:
        r = client.get("/api/health")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}


def test_devices_empty():
    with TestClient(app) as client:
        r = client.get("/api/devices")
        assert r.status_code == 200
        assert r.json() == []
