def test_history_endpoint(client):
    response = client.get("/history")

    assert response.status_code == 200

    data = response.json()

    assert "history" in data
    assert isinstance(data["history"], list)


def test_tasks_endpoint(client):
    response = client.get("/tasks")

    assert response.status_code == 200

    data = response.json()

    assert "tasks" in data
    assert isinstance(data["tasks"], list)


def test_runs_endpoint(client):
    response = client.get("/runs")

    assert response.status_code == 200

    data = response.json()

    assert "runs" in data
    assert isinstance(data["runs"], list)