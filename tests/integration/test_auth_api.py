def test_auth_register_login_and_me_flow(client):
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "integration@example.com",
            "password": "strongpass123",
            "full_name": "Integration User",
        },
    )
    assert register_response.status_code == 201
    assert register_response.json()["email"] == "integration@example.com"

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "integration@example.com",
            "password": "strongpass123",
        },
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    me_response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "integration@example.com"
    assert me_response.json()["wallet_balance"] == 100
