

async def test_login(client, register_user):
    login_data = {
        "email": "testuser@example.com",
        "password": "testpassword",
    }

    response = client.post("/auth/login", json=login_data)
    json_response = response.json()

    assert response.status_code == 200
    assert "access_token" in json_response
    assert "refresh_token" in json_response


