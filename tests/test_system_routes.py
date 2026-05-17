def test_root_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "AI Assistant Backend Running"


def test_status_endpoint(client):
    response = client.get("/status")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "running"
    assert "model" in data
    assert "max_agent_steps" in data
    assert "available_tools" in data


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert "ok" in data
    assert "checks" in data