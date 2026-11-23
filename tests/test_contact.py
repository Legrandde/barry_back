def test_contact_flow_and_honeypot(client, auth_headers):
    # Envoi normal
    res = client.post(
        "/api/public/contact",
        json={
            "name": "Mamadou Camara",
            "email": "mamadou@example.com",
            "phone": "+224 620 00 00 00",
            "subject": "Projet d'application mobile",
            "message": "Bonjour Alhassane, j'aimerais discuter d'un projet mobile.",
        },
    )
    assert res.status_code == 204

    # Envoi par un robot (champ honeypot rempli) -> 204 silencieux mais non enregistré
    bot = client.post(
        "/api/public/contact",
        json={
            "name": "Spam Bot",
            "email": "spam@bot.com",
            "subject": "Promo",
            "message": "Achetez maintenant !",
            "website": "https://spam.example.com",
        },
    )
    assert bot.status_code == 204

    # Vérification côté admin
    unread = client.get("/api/admin/messages/unread-count", headers=auth_headers)
    assert unread.status_code == 200
    assert unread.json() == {"unread": 1}

    messages = client.get("/api/admin/messages", headers=auth_headers).json()
    assert len(messages) == 1
    msg_id = messages[0]["id"]
    assert messages[0]["isRead"] is False

    # Marquer comme lu
    patched = client.patch(f"/api/admin/messages/{msg_id}", json={"isRead": True}, headers=auth_headers)
    assert patched.status_code == 200
    assert patched.json()["isRead"] is True
    assert client.get("/api/admin/messages/unread-count", headers=auth_headers).json() == {"unread": 0}

    # Suppression
    assert client.delete(f"/api/admin/messages/{msg_id}", headers=auth_headers).status_code == 204
    assert client.get("/api/admin/messages", headers=auth_headers).json() == []
