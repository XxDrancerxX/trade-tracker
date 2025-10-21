def test_health_ok(client):
    r = client.get("/api/health", secure=True)  # pretend request is over HTTPS
    assert r.status_code == 200
