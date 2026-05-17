TEST_FILE_PATH = "data/state/test_medium_risk_tool.txt"


def test_medium_risk_tool_is_allowed(client):
    response = client.post(
        "/tools/run",
        json={
            "tool_name": "write_file",
            "args": {
                "path": TEST_FILE_PATH,
                "content": "medium risk tool test"
            }
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "result" in data
    assert "File written" in data["result"]

    cleanup_response = client.post(
        "/tools/run",
        json={
            "tool_name": "cleanup_test_file",
            "args": {
                "path": TEST_FILE_PATH
            }
        }
    )

    assert cleanup_response.status_code == 200

    cleanup_data = cleanup_response.json()

    assert "result" in cleanup_data
    assert "Deleted file" in cleanup_data["result"]


def test_high_risk_tool_still_blocked(client):
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
    assert data["result"]["blocked"] is True
    assert data["result"]["permission_level"] == "high"
    assert "approval_id" in data["result"]