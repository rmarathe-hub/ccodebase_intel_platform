from fastapi.testclient import TestClient

from app.main import create_app


def test_health() -> None:
    client = TestClient(create_app())
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "index_pipeline_version" in body
    assert body["index_pipeline_version"]
    assert "build" in body


def test_ready_shape() -> None:
    client = TestClient(create_app())
    response = client.get("/ready")
    assert response.status_code == 200
    body = response.json()
    assert "status" in body
    assert "database" in body
    assert "index_pipeline_version" in body
    assert "build" in body
