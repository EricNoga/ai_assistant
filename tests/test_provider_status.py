from fastapi.testclient import TestClient

from backend.api.app import create_app

client = TestClient(
    create_app()
)

def test_status_has_provider():
    response = client.get("/status")

    assert response.status_code == 200

    data = response.json()

    assert "provider" in data
    assert data["provider"] == "mock"

def test_status_has_valid_providers():
    response = client.get("/status")

    assert response.status_code == 200

    data = response.json()

    assert "valid_providers" in data
    assert "mock" in data["valid_providers"]
    assert "openai" in data["valid_providers"]