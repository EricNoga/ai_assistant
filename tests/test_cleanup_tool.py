def test_cleanup_tool_blocks_unsafe_path(client):
    response = client.post(
        "/tools/run",
        json={
            "tool_name": "cleanup_test_file",
            "args": {
                "path": "../../dangerous_file.txt"
            }
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "result" in data
    assert "Cleanup blocked" in data["result"]


def test_cleanup_tool_handles_missing_file(client):
    response = client.post(
        "/tools/run",
        json={
            "tool_name": "cleanup_test_file",
            "args": {
                "path": "data/state/does_not_exist.txt"
            }
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "result" in data
    assert "File does not exist" in data["result"]