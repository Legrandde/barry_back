def test_projects_crud_slug_and_reorder(client, auth_headers):
    initial = client.get("/api/admin/projects", headers=auth_headers)
    assert initial.status_code == 200
    assert len(initial.json()) == 6

    # Création avec slug auto-généré
    created = client.post(
        "/api/admin/projects",
        json={
            "title": "EcoSystem IoT",
            "description": "Suivi intelligent de la consommation électrique.",
            "type": "mobile",
            "category": "Mobile Application",
            "technologies": ["React Native", "Django", "MQTT"],
        },
        headers=auth_headers,
    )
    assert created.status_code == 201
    project = created.json()
    assert project["slug"] == "ecosystem-iot"

    # Création d'un projet avec le même titre -> suffixe -2
    duplicate = client.post(
        "/api/admin/projects",
        json={"title": "EcoSystem IoT"},
        headers=auth_headers,
    )
    assert duplicate.status_code == 201
    assert duplicate.json()["slug"] == "ecosystem-iot-2"

    # Conflit si slug explicite déjà pris
    conflict = client.post(
        "/api/admin/projects",
        json={"title": "Autre", "slug": "ecosystem-iot"},
        headers=auth_headers,
    )
    assert conflict.status_code == 409

    # Réordonnancement
    all_ids = [item["id"] for item in client.get("/api/admin/projects", headers=auth_headers).json()]
    reversed_ids = list(reversed(all_ids))
    reordered = client.put(
        "/api/admin/projects/reorder",
        json={"ids": reversed_ids},
        headers=auth_headers,
    )
    assert reordered.status_code == 200
    assert [item["id"] for item in reordered.json()] == reversed_ids

    # Dépublication + vérification côté public
    patch = client.patch(
        f"/api/admin/projects/{project['id']}",
        json={"isPublished": False},
        headers=auth_headers,
    )
    assert patch.status_code == 200
    assert client.get("/api/public/projects/ecosystem-iot").status_code == 404

    # Suppression
    assert client.delete(f"/api/admin/projects/{project['id']}", headers=auth_headers).status_code == 204
    assert client.get(f"/api/admin/projects/{project['id']}", headers=auth_headers).status_code == 404


def test_other_collections_crud(client, auth_headers):
    # Services
    res = client.post(
        "/api/admin/services",
        json={"title": "Audit Sécurité", "description": "Audit complet d'API", "icon": "cloud"},
        headers=auth_headers,
    )
    assert res.status_code == 201

    # Skill categories
    res = client.post(
        "/api/admin/skill-categories",
        json={"name": "IA & Data", "icon": "code", "skills": [{"name": "Python", "level": 90}]},
        headers=auth_headers,
    )
    assert res.status_code == 201
    assert res.json()["skills"][0]["level"] == 90

    # Experiences
    res = client.post(
        "/api/admin/experiences",
        json={
            "title": "Développeur Freelance",
            "company": "Indépendant",
            "period": "2025 - Présent",
            "description": "Projets web et mobile sur mesure.",
            "technologies": ["FastAPI", "React"],
        },
        headers=auth_headers,
    )
    assert res.status_code == 201

    # Educations
    res = client.post(
        "/api/admin/educations",
        json={
            "degree": "Certification FastAPI",
            "institution": "En ligne",
            "period": "2026",
            "achievements": ["Major"],
        },
        headers=auth_headers,
    )
    assert res.status_code == 201

    # Testimonials
    res = client.post(
        "/api/admin/testimonials",
        json={"name": "Amadou Diallo", "role": "CTO", "company": "GuinéeTech", "rating": 5, "text": "Super !"},
        headers=auth_headers,
    )
    assert res.status_code == 201

    # Social links
    res = client.post(
        "/api/admin/social-links",
        json={"label": "Portfolio", "url": "https://barryalhassane.com", "icon": "website"},
        headers=auth_headers,
    )
    assert res.status_code == 201
