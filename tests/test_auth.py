async def test_register_success(client):
    resp = await client.post("/auth/register", json={"email": "alice@example.com", "password": "password123"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "alice@example.com"
    assert body["is_active"] is True
    assert body["is_admin"] is False
    assert "password" not in body
    assert "hashed_password" not in body


async def test_register_duplicate_email(client):
    await client.post("/auth/register", json={"email": "alice@example.com", "password": "password123"})
    resp = await client.post("/auth/register", json={"email": "alice@example.com", "password": "otherpass123"})
    assert resp.status_code == 409


async def test_login_success(client):
    await client.post("/auth/register", json={"email": "alice@example.com", "password": "password123"})
    resp = await client.post("/auth/login", data={"username": "alice@example.com", "password": "password123"})
    assert resp.status_code == 200
    assert resp.json()["token_type"] == "bearer"
    assert len(resp.json()["access_token"]) > 20


async def test_login_wrong_password(client):
    await client.post("/auth/register", json={"email": "alice@example.com", "password": "password123"})
    resp = await client.post("/auth/login", data={"username": "alice@example.com", "password": "wrongpassword"})
    assert resp.status_code == 401


async def test_login_nonexistent_email_returns_401_not_500(client):
    resp = await client.post("/auth/login", data={"username": "nobody@example.com", "password": "whatever123"})
    assert resp.status_code == 401


async def test_protected_endpoint_without_token(client):
    resp = await client.get("/bookings/me")
    assert resp.status_code == 401


async def test_protected_endpoint_with_garbage_token(client):
    resp = await client.get("/bookings/me", headers={"Authorization": "Bearer garbage.token.here"})
    assert resp.status_code == 401


async def test_helper_register_and_login_returns_usable_token(client, register_and_login):
    token = await register_and_login("bob@example.com")
    resp = await client.get("/bookings/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
