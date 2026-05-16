from fastapi.testclient import TestClient

from backend.api.app import create_app

client = TestClient(
    create_app()
)

def test_tools_endpoint():
    response = client.get("/tools")

    assert response.status_code == 200

    data = response.json()

    assert "tools" in data
    assert isinstance(data["tools"], dict)

def test_tool_names_endpoint():
    response = client.get("/tools/names")

    assert response.status_code == 200

    data = response.json()

    assert "tools" in data
    assert isinstance(data["tools"], list)