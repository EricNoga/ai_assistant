from fastapi.testclient import TestClient

from backend.api.app import create_app

client = TestClient(
    create_app()
)

def test_status_include_high_risk_tool_settings():
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert "allow_high_risk_tools" in data
    assert data["allow_high_risk_tools"] is False

def test_health_includes_high_risk_tool_setting():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "checks" in data
    assert "allow_high_risk_tools" in data["checks"]
    assert data["checks"]["allow_high_risk_tools"] is False