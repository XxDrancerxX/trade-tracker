def test_health_ok(client): # Test the /api/health endpoint
    r = client.get("/api/health")
    assert r.status_code == 200 # Check for HTTP 200 OK
    body = r.json()
    assert body["status"] == "ok"
# A lightweight smoke test to verify the app is up and the health endpoint is wired correctly (routing + view + middleware).