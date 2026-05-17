def test_providers_endpoint(client):
    response = client.get("/providers")

    assert response.status_code == 200

    data = response.json()

    assert "active_provider" in data
    assert "valid_providers" in data
    assert "default_model" in data

    assert data["active_provider"] == "mock"
    assert "mock" in data["valid_providers"]
    assert "openai" in data["valid_providers"]