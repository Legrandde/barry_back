def test_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_public_content_returns_all_seeded_sections_and_collections(client):
    res = client.get("/api/public/content")
    assert res.status_code == 200
    data = res.json()

    assert data["site"]["firstName"] == "Alhassane"
    assert data["site"]["lastName"] == "Barry"
    assert data["theme"]["accentColor"] == "#f59e0b"
    assert data["hero"]["image"] == "barry.png"
    assert len(data["services"]["items"]) == 4
    assert len(data["skills"]["categories"]) == 5
    assert len(data["stats"]["items"]) == 3
    assert len(data["parcours"]["items"]) == 3
    assert len(data["formation"]["items"]) == 2
    assert len(data["process"]["steps"]) == 5
    assert len(data["projects"]["items"]) == 6
    assert len(data["testimonials"]["items"]) == 4
    assert len(data["contact"]["socials"]) == 3
    assert data["cta"]["highlightWord"] == "projet"


def test_public_content_localizes_contact_for_senegal_vs_guinea(client):
    # Visiteur au Sénégal (IP Dakar) -> numéro sénégalais + Dakar, Guédiawaye
    sn = client.get("/api/public/content", headers={"X-Forwarded-For": "41.82.12.1"})
    assert sn.status_code == 200
    sn_data = sn.json()
    assert sn_data["site"]["phone"] == "+221 77 487 40 73"
    assert sn_data["site"]["location"] == "Dakar, Guédiawaye"
    assert sn_data["site"]["whatsappNumber"] == "221774874073"
    assert sn_data["contact"]["phone"] == "+221 77 487 40 73"
    assert sn_data["contact"]["location"] == "Dakar, Guédiawaye"
    assert sn_data["cta"]["secondaryCtaHref"] == "tel:+221774874073"

    # Visiteur en Guinée (IP Conakry) -> numéro et localisation guinéens conservés
    gn = client.get("/api/public/content", headers={"X-Forwarded-For": "197.149.240.1"})
    assert gn.status_code == 200
    gn_data = gn.json()
    assert gn_data["site"]["phone"] == "+224 626 01 45 52"
    assert gn_data["site"]["location"] == "Timbi Madina"
    assert gn_data["site"]["whatsappNumber"] == "224626014552"
    assert gn_data["contact"]["phone"] == "+224 626 01 45 52"
    assert gn_data["contact"]["location"] == "Timbi Madina"
    assert gn_data["cta"]["secondaryCtaHref"] == "tel:+224626014552"

    # Secours par en-tête proxy Cloudflare (CF-IPCountry: SN)
    cf = client.get("/api/public/content", headers={"CF-IPCountry": "SN"})
    assert cf.status_code == 200
    assert cf.json()["site"]["phone"] == "+221 77 487 40 73"
    assert cf.json()["site"]["location"] == "Dakar, Guédiawaye"


def test_public_project_by_slug(client):
    res = client.get("/api/public/projects/teranga-palace")
    assert res.status_code == 200
    assert res.json()["title"] == "Teranga Palace"
    assert res.json()["liveUrl"] == "https://dakar-dreams.vercel.app/"

    assert client.get("/api/public/projects/inexistant").status_code == 404
