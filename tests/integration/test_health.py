from app.core.config import Settings


def test_default_app_name(monkeypatch) -> None:
    monkeypatch.delenv("APP_NAME", raising=False)

    assert Settings(_env_file=None).app_name == "Workspace API"


def test_health_check_returns_ok(client) -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
