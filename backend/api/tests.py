from django.test import TestCase

# Create your tests here.

# 🧪 Tests (what to test vs not)

# Do test your serializers/viewsets/repositories with offline data (deterministic).

# Don’t hit Coinbase in tests. If you want coverage of signing, unit-test the signing function with known inputs/outputs (no network).

# Example unit test (no network):

# def test_coinbase_signature_matches_known_vector():
#     ts = "1700000000"
#     method = "GET"
#     path = "/api/v3/brokerage/accounts"
#     body = ""
#     secret_b64 = "ZmFrZV9zZWNyZXRfNDJfYnl0ZXM="  # fake
#     msg = ts + method + path + body
#     import hmac, hashlib, base64
#     sig = hmac.new(base64.b64decode(secret_b64), msg.encode(), hashlib.sha256).digest()
#     got = base64.b64encode(sig).decode()

#===============================================================================================================================
#===============================================================================================================================

# //🔑 What is CI?

# CI = Continuous Integration.
# It’s the practice of automatically running your tests and checks every time you push code (on GitHub, GitLab, etc.).

# Why: catches bugs early, makes sure code always runs for everyone.

# How: GitHub Actions / GitLab CI run pytest, lint, type checks inside a clean environment.

# Rule: CI should only run deterministic tests (offline, reproducible). Not scripts that hit real APIs.