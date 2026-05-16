from fastapi.testclient import TestClient

from backend.api.app import create_app


client = TestClient(
    create_app()
)


def test_medium_risk_tool_is_allowed():
    response = client.post(
        "/tools/run",
        json={
            "tool_name": "write_file",
            "args": {
                "path": "data/state/test_medium_risk_tool.txt",
                "content": "medium risk tool test"
            }
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "result" in data
    assert "File written" in data["result"]


def test_high_risk_tool_still_blocked():
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