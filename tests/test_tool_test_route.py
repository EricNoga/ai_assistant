def test_tool_run_endpoint_with_valid_tool(client):
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

    assert data["tool_name"] == "list_files"
    assert "result" in data


def test_tool_run_endpoint_with_invalid_tool(client):
    response = client.post(
        "/tools/run",
        json={
            "tool_name": "fake_tool",
            "args": {}
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "error" in data
    assert "available_tools" in data