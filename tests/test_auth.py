from tests.conftest import ADMIN_CREDENTIALS


def test_login_and_me(client):
    res = client.post("/api/auth/login", data=ADMIN_CREDENTIALS)
    assert res.status_code == 200
    body = res.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {body['access_token']}"})
    assert me.status_code == 200
    assert me.json()["username"] == "admin"


def test_login_invalid_credentials(client):
    res = client.post("/api/auth/login", data={"username": "admin", "password": "wrong"})
    assert res.status_code == 401


def test_admin_route_requires_auth(client):
    assert client.get("/api/admin/sections").status_code == 401
    assert client.get("/api/admin/projects").status_code == 401
    assert client.get("/api/admin/messages").status_code == 401
    assert client.get("/api/admin/analytics/summary").status_code == 401


def test_change_password(client, auth_headers):
    res = client.put(
        "/api/auth/password",
        json={"currentPassword": "test-password", "newPassword": "new-secure-password"},
        headers=auth_headers,
    )
    assert res.status_code == 204

    assert client.post("/api/auth/login", data=ADMIN_CREDENTIALS).status_code == 401
    assert (
        client.post("/api/auth/login", data={"username": "admin", "password": "new-secure-password"}).status_code
        == 200
    )


def test_change_username_returns_new_token(client, auth_headers):
    res = client.put(
        "/api/auth/username",
        json={"currentPassword": "test-password", "newUsername": "barry_admin"},
        headers=auth_headers,
    )
    assert res.status_code == 200
    new_token = res.json()["access_token"]

    # L'ancien token ne fonctionne plus
    assert client.get("/api/auth/me", headers=auth_headers).status_code == 401
    # Le nouveau token fonctionne
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {new_token}"})
    assert me.status_code == 200
    assert me.json()["username"] == "barry_admin"
