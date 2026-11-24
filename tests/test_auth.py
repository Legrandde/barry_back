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


def test_two_factor_auth_full_lifecycle(client, auth_headers):
    from core.totp import totp_at

    # Initialement désactivée
    assert client.get("/api/auth/me", headers=auth_headers).json()["totpEnabled"] is False

    # Setup 2FA
    setup = client.post("/api/auth/2fa/setup", headers=auth_headers)
    assert setup.status_code == 200
    secret = setup.json()["secret"]
    assert setup.json()["otpauthUri"].startswith("otpauth://totp/")

    # Mauvais code refusé à l'activation
    assert client.post("/api/auth/2fa/enable", json={"code": "000000"}, headers=auth_headers).status_code == 422

    # Bon code active la 2FA
    assert client.post("/api/auth/2fa/enable", json={"code": totp_at(secret)}, headers=auth_headers).status_code == 204
    assert client.get("/api/auth/me", headers=auth_headers).json()["totpEnabled"] is True

    # Connexion demande désormais la 2FA et ne donne pas d'access_token
    step1 = client.post("/api/auth/login", data=ADMIN_CREDENTIALS)
    assert step1.status_code == 200
    body = step1.json()
    assert body["requires_2fa"] is True
    assert body["challenge_token"]
    assert body["access_token"] == ""

    # Le challenge_token ne peut PAS accéder aux routes admin
    assert client.get("/api/auth/me", headers={"Authorization": f"Bearer {body['challenge_token']}"}).status_code == 401

    # Validation étape 2 avec le code TOTP -> vrai access_token
    step2 = client.post(
        "/api/auth/verify-2fa",
        json={"challengeToken": body["challenge_token"], "code": totp_at(secret)},
    )
    assert step2.status_code == 200
    final_token = step2.json()["access_token"]
    assert final_token
    assert client.get("/api/auth/me", headers={"Authorization": f"Bearer {final_token}"}).status_code == 200

    # Désactivation de la 2FA
    dis = client.post(
        "/api/auth/2fa/disable",
        json={"currentPassword": "test-password", "code": totp_at(secret)},
        headers={"Authorization": f"Bearer {final_token}"},
    )
    assert dis.status_code == 204
    assert client.get("/api/auth/me", headers={"Authorization": f"Bearer {final_token}"}).json()["totpEnabled"] is False


def test_security_hardening_jwt_revocation_headers_and_rate_limit(client, auth_headers):
    # En-têtes de sécurité HTTP présents
    health = client.get("/api/health")
    assert health.status_code == 200
    assert health.headers["X-Content-Type-Options"] == "nosniff"
    assert health.headers["X-Frame-Options"] == "DENY"
    assert health.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"

    # Rejet des URLs javascript:
    bad_url = client.patch("/api/admin/sections/hero", json={"image": "javascript:alert(1)"}, headers=auth_headers)
    assert bad_url.status_code == 422

    # Le changement de mot de passe révoque immédiatement l'ancien JWT
    res = client.put(
        "/api/auth/password",
        json={"currentPassword": "test-password", "newPassword": "new-secure-password-2026"},
        headers=auth_headers,
    )
    assert res.status_code == 204
    assert client.get("/api/auth/me", headers=auth_headers).status_code == 401

    # Rate-limit sur /api/auth/login (auth_headers a déjà consommé 1 tentative, 9 autres passent, la 11e renvoie 429)
    for _ in range(9):
        attempt = client.post("/api/auth/login", data={"username": "admin", "password": "wrong"})
        assert attempt.status_code == 401
    blocked = client.post("/api/auth/login", data={"username": "admin", "password": "wrong"})
    assert blocked.status_code == 429
