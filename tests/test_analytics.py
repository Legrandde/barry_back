_BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
)


def test_analytics_track_and_summary(client, auth_headers):
    # Visite humaine (avec IP publique transmise par un reverse proxy)
    res = client.post(
        "/api/public/track",
        json={"name": "pageview", "path": "/", "referrer": "https://www.linkedin.com/feed", "utmSource": "linkedin"},
        headers={
            "User-Agent": _BROWSER_UA,
            "Accept-Language": "fr-FR,fr;q=0.9",
            "X-Forwarded-For": "197.149.240.1",
        },
    )
    assert res.status_code == 204

    # Action (ouverture d'un projet) par le même visiteur
    res2 = client.post(
        "/api/public/track",
        json={"name": "project_open", "label": "teranga-palace", "path": "/"},
        headers={"User-Agent": _BROWSER_UA, "X-Forwarded-For": "197.149.240.1"},
    )
    assert res2.status_code == 204

    # Second visiteur depuis le Sénégal (via X-Forwarded-For)
    res3 = client.post(
        "/api/public/track",
        json={"name": "pageview", "path": "/"},
        headers={"User-Agent": _BROWSER_UA, "X-Forwarded-For": "41.82.12.1"},
    )
    assert res3.status_code == 204

    # Robot ignoré silencieusement
    bot = client.post(
        "/api/public/track",
        json={"name": "pageview", "path": "/"},
        headers={"User-Agent": "Googlebot/2.1"},
    )
    assert bot.status_code == 204

    summary = client.get("/api/admin/analytics/summary?days=7", headers=auth_headers)
    assert summary.status_code == 200
    data = summary.json()
    assert data["totals"] == {"pageviews": 2, "uniqueVisitors": 2, "events": 1}
    assert data["today"]["pageviews"] == 2
    assert data["activeVisitors"] == 2
    assert data["referrers"] == [{"name": "linkedin.com", "count": 1}, {"name": "Accès direct", "count": 1}]
    assert data["devices"] == [{"name": "Ordinateur", "count": 2}]
    assert data["browsers"] == [{"name": "Chrome", "count": 2}]
    assert data["operatingSystems"] == [{"name": "Windows", "count": 2}]
    assert data["events"] == [{"name": "project_open", "label": "teranga-palace", "count": 1}]
    assert data["geoAvailable"] is True
    assert {c["code"] for c in data["countries"]} == {"GN", "SN"}
    assert {(r["country"], r["region"]) for r in data["regions"]} == {("GN", "Conakry"), ("SN", "Dakar")}


def test_analytics_localhost_v4_v6_and_proxy_headers_fallback(client, auth_headers):
    # ::1 et 127.0.0.1 doivent produire le même visiteur unique
    for ip in ("127.0.0.1", "::1"):
        res = client.post(
            "/api/public/track",
            json={"name": "pageview", "path": "/"},
            headers={
                "User-Agent": _BROWSER_UA,
                "X-Forwarded-For": ip,
                "CF-IPCountry": "FR",
                "X-Vercel-IP-Country-Region": "Ile-de-France",
            },
        )
        assert res.status_code == 204

    data = client.get("/api/admin/analytics/summary?days=7", headers=auth_headers).json()
    assert data["totals"]["pageviews"] == 2
    assert data["totals"]["uniqueVisitors"] == 1
    assert data["countries"] == [{"code": "FR", "visitors": 1, "pageviews": 2}]
    assert data["regions"] == [{"country": "FR", "region": "Ile-de-France", "visitors": 1, "pageviews": 2}]
