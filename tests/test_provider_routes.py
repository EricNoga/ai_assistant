from fastapi.testclient import TestClient

from backend.api.app import create_app


client = TestClient(
    create_app()
)


def test_providers_endpoint():
    response = client.get("/providers")

    assert response.status_code == 200

    data = response.json()

    assert "active_provider" in data
    assert "valid_providers" in data
    assert "default_model" in data

    assert data["active_provider"] == "mock"
    assert "mock" in data["valid_providers"]
    assert "openai" in data["valid_providers"]