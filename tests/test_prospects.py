from datetime import date, timedelta


def test_prospects_full_crud_interactions_documents_and_stats(client, auth_headers):
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    today = date.today().isoformat()

    # 1. Création d'un dossier prospect
    created = client.post(
        "/api/admin/prospects",
        json={
            "name": "Wave Sénégal",
            "sector": "Fintech",
            "location": "Dakar, Sénégal",
            "website": "https://www.wave.com",
            "socialLinks": [{"label": "LinkedIn", "url": "https://linkedin.com/company/wave"}],
            "contactName": "Aminata Diallo",
            "contactRole": "Head of Product",
            "contactEmail": "aminata@wave.com",
            "contactPhone": "+221 77 000 00 00",
            "identifiedNeed": "Refonte du portail partenaires",
            "proposedService": "Application web React + API FastAPI",
            "estimatedBudget": "4 500 000 FCFA",
            "priority": "haute",
            "status": "a_contacter",
            "nextFollowUpDate": yesterday,
            "nextAction": "Envoyer la proposition initiale",
        },
        headers=auth_headers,
    )
    assert created.status_code == 201
    prospect = created.json()
    pid = prospect["id"]
    assert prospect["name"] == "Wave Sénégal"
    assert prospect["status"] == "a_contacter"
    # Une interaction initiale "Dossier créé" est enregistrée automatiquement
    assert len(prospect["interactions"]) == 1
    assert prospect["interactions"][0]["type"] == "statut"

    # 2. Statistiques & rappel en retard
    stats = client.get("/api/admin/prospects/stats", headers=auth_headers).json()
    assert stats["total"] == 1
    assert stats["aContacter"] == 1
    assert stats["overdueFollowUps"] == 1

    # 3. Mise à jour du statut -> génère automatiquement une entrée dans l'historique
    patched = client.patch(
        f"/api/admin/prospects/{pid}",
        json={"status": "en_discussion", "nextFollowUpDate": today},
        headers=auth_headers,
    )
    assert patched.status_code == 200
    assert patched.json()["status"] == "en_discussion"
    assert len(patched.json()["interactions"]) == 2

    # 4. Ajout d'une interaction réelle (email) -> met à jour lastContactDate
    inter = client.post(
        f"/api/admin/prospects/{pid}/interactions",
        json={
            "type": "email",
            "title": "Envoi du dossier de présentation",
            "content": "Présentation de notre approche et devis préliminaire.",
        },
        headers=auth_headers,
    )
    assert inter.status_code == 201
    detail = client.get(f"/api/admin/prospects/{pid}", headers=auth_headers).json()
    assert detail["lastContactDate"] == today
    assert len(detail["interactions"]) == 3

    # 5. Upload d'un document PDF valide + rejet d'un faux PDF
    bad_doc = client.post(
        f"/api/admin/prospects/{pid}/documents",
        files={"file": ("fake.pdf", b"not-a-pdf", "application/pdf")},
        headers=auth_headers,
    )
    assert bad_doc.status_code == 415

    good_doc = client.post(
        f"/api/admin/prospects/{pid}/documents",
        files={"file": ("proposition.pdf", b"%PDF-1.4\n%test content", "application/pdf")},
        headers=auth_headers,
    )
    assert good_doc.status_code == 201
    doc_id = good_doc.json()["id"]
    assert good_doc.json()["url"].endswith(".pdf")

    # 6. Filtrage, recherche et archivage
    found = client.get("/api/admin/prospects?search=Wave&priority=haute", headers=auth_headers).json()
    assert len(found) == 1

    archived = client.patch(f"/api/admin/prospects/{pid}", json={"isArchived": True}, headers=auth_headers)
    assert archived.status_code == 200
    assert client.get("/api/admin/prospects?archived=false", headers=auth_headers).json() == []
    assert len(client.get("/api/admin/prospects?archived=true", headers=auth_headers).json()) == 1

    # 7. Suppression du document puis du dossier
    assert client.delete(f"/api/admin/prospects/{pid}/documents/{doc_id}", headers=auth_headers).status_code == 204
    assert client.delete(f"/api/admin/prospects/{pid}", headers=auth_headers).status_code == 204
    assert client.get(f"/api/admin/prospects/{pid}", headers=auth_headers).status_code == 404
