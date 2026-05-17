def test_chat_endpoint(client):
    response = client.post(
        "/chat",
        json={
            "message": "Hello"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "response" in data