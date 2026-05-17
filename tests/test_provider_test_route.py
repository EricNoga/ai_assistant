def test_provider_test_endpoint(client):
    response = client.get("/providers/test")

    assert response.status_code == 200

    data = response.json()

    assert "response" in data
    assert isinstance(data["response"], str)