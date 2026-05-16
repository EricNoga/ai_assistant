from fastapi.testclient import TestClient

from backend.api.app import create_app

client = TestClient(
    create_app()
)

def test_provider_test_endpoint():
    response = client.get("/providers/test")

    assert response.status_code == 200

    data = response.json()

    assert "response" in data
    assert isinstance(data["response"], str)