def test_register_and_login_flow(client):
    # Register a new user
    resp = client.post(
        "/auth/register",
        json={"email": "john.doe@example.com", "password": "secret123", "name": "John Doe"},
    )
    assert resp.status_code in (201, 400)
    if resp.status_code == 201:
        data = resp.get_json()
        assert "access_token" in data and data["access_token"]

    # Duplicate register should fail with 400
    dup = client.post(
        "/auth/register",
        json={"email": "john.doe@example.com", "password": "secret123", "name": "John Doe"},
    )
    assert dup.status_code == 400

    # Login with correct credentials
    login_ok = client.post(
        "/auth/login",
        json={"email": "john.doe@example.com", "password": "secret123"},
    )
    assert login_ok.status_code == 200
    token = login_ok.get_json()["access_token"]
    assert isinstance(token, str) and len(token) > 20

    # Login with invalid credentials
    bad_login = client.post(
        "/auth/login",
        json={"email": "john.doe@example.com", "password": "wrong"},
    )
    assert bad_login.status_code == 401
