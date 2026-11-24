def test_list_and_patch_section(client, auth_headers):
    res = client.get("/api/admin/sections", headers=auth_headers)
    assert res.status_code == 200
    keys = {item["key"] for item in res.json()}
    assert {"site", "theme", "hero", "about", "services", "skills", "stats", "parcours", "formation", "process", "projects", "testimonials", "contact", "cta"} == keys

    patched = client.patch(
        "/api/admin/sections/hero",
        json={"role": "Architecte Full-stack & Mobile"},
        headers=auth_headers,
    )
    assert patched.status_code == 200
    assert patched.json()["role"] == "Architecte Full-stack & Mobile"
    assert patched.json()["firstName"] == "Alhassane"


def test_patch_section_rejects_unknown_field(client, auth_headers):
    res = client.patch(
        "/api/admin/sections/hero",
        json={"champInconnu": "valeur"},
        headers=auth_headers,
    )
    assert res.status_code == 422


def test_visibility_toggle_and_non_hideable(client, auth_headers):
    # Masquer testimonials
    res = client.put(
        "/api/admin/sections/testimonials/visibility",
        json={"isVisible": False},
        headers=auth_headers,
    )
    assert res.status_code == 200
    assert res.json() == {"key": "testimonials", "isVisible": False, "hideable": True}

    # La route publique renvoie 404 pour une section masquée
    assert client.get("/api/public/sections/testimonials").status_code == 404

    # Et le contenu global reflète visibility.testimonials == False
    content = client.get("/api/public/content").json()
    assert content["visibility"]["testimonials"] is False

    # Impossible de masquer site ou theme
    for key in ("site", "theme"):
        blocked = client.put(
            f"/api/admin/sections/{key}/visibility",
            json={"isVisible": False},
            headers=auth_headers,
        )
        assert blocked.status_code == 422


def test_hero_layout_and_theme_customization(client, auth_headers):
    for layout in ("classic", "centered", "editorial", "poster", "minimal"):
        res = client.patch(
            "/api/admin/sections/hero",
            json={"layout": layout, "availabilityBadge": "Ouvert aux missions"},
            headers=auth_headers,
        )
        assert res.status_code == 200
        assert res.json()["layout"] == layout
        assert res.json()["availabilityBadge"] == "Ouvert aux missions"

    bad_layout = client.patch(
        "/api/admin/sections/hero",
        json={"layout": "inconnu"},
        headers=auth_headers,
    )
    assert bad_layout.status_code == 422

    theme_res = client.patch(
        "/api/admin/sections/theme",
        json={
            "accentColor": "#2563eb",
            "headingFont": "Plus Jakarta Sans",
            "bodyFont": "Inter",
            "defaultMode": "dark",
        },
        headers=auth_headers,
    )
    assert theme_res.status_code == 200
    body = theme_res.json()
    assert body["accentColor"] == "#2563eb"
    assert body["headingFont"] == "Plus Jakarta Sans"
    assert body["bodyFont"] == "Inter"
    assert body["defaultMode"] == "dark"
