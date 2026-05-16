from fastapi.testclient import TestClient

from backend.api.app import create_app


client = TestClient(
    create_app()
)


def test_chat_endpoint():
    response = client.post(
        "/chat",
        json={
            "message": "Hello"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "response" in data