# Mini PNG 1x1 valide
_PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
    b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)


def test_media_upload_list_and_delete(client, auth_headers):
    res = client.post(
        "/api/admin/media",
        files={"file": ("avatar.png", _PNG_BYTES, "image/png")},
        headers=auth_headers,
    )
    assert res.status_code == 201
    media = res.json()
    assert media["originalName"] == "avatar.png"
    assert media["status"] == "ready"
    assert media["url"].endswith(f"/media/{media['filename']}")

    # Le fichier est servi sous /media
    served = client.get(f"/media/{media['filename']}")
    assert served.status_code == 200
    assert served.content == _PNG_BYTES

    # Liste et suppression
    assert len(client.get("/api/admin/media", headers=auth_headers).json()) == 1
    assert client.delete(f"/api/admin/media/{media['id']}", headers=auth_headers).status_code == 204
    assert client.get("/api/admin/media", headers=auth_headers).json() == []


def test_media_rejects_bad_signature_and_type(client, auth_headers):
    # Faux PNG (contenu texte déguisé en image/png)
    fake = client.post(
        "/api/admin/media",
        files={"file": ("fake.png", b"not-a-real-png-file", "image/png")},
        headers=auth_headers,
    )
    assert fake.status_code == 415

    # Type interdit
    bad_type = client.post(
        "/api/admin/media",
        files={"file": ("script.js", b"alert(1)", "application/javascript")},
        headers=auth_headers,
    )
    assert bad_type.status_code == 415
