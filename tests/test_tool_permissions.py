from fastapi.testclient import TestClient

from backend.api.app import create_app


client = TestClient(
    create_app()
)


def test_high_risk_tool_is_blocked_by_default():
    response = client.post(
        "/tools/run",
        json={
            "tool_name": "run_python_code",
            "args": {
                "code": "print('hello')"
            }
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "result" in data
    assert "Tool blocked" in data["result"]


def test_low_risk_tool_is_allowed():
    response = client.post(
        "/tools/run",
        json={
            "tool_name": "list_files",
            "args": {
                "path": "."
            }
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "result" in data
    assert isinstance(data["result"], list)