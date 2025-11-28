import re
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model() # Get the User model from Django's auth system.

@pytest.mark.django_db # Use the Django test database for this test.
def test_register_success(): # Test successful user registration.
    client = APIClient() # Create an API client to simulate requests.

    resp = client.post("/api/auth/register/", {
        "username": "newuser",
        "password": "newpass123",
    }, format="json",
    secure = True,
    ) # Send POST request to the register endpoint with JSON body.

    assert resp.status_code == 201 # Expect HTTP 201 Created response.
    data = resp.json() # Parse JSON response body.
    assert data["ok"] is True 
    assert data["user"]["username"] == "newuser" # Check returned username.

    # User exists in DB
    assert User.objects.filter(username="newuser").exists() # Verify user was created in the database.

    # Cookies are included
    cookies = resp.cookies # Get cookies from the response.
    assert "tt_access" in cookies
    assert "tt_refresh" in cookies


@pytest.mark.django_db
def test_register_duplicate_username(): # Test registration with an existing username.
    # Pre-create a user with the username "existing"
    User.objects.create_user(username="existing", password="abc12345")

    client = APIClient()
    resp = client.post("/api/auth/register/", {
        "username": "existing",
        "password": "newpass123",
    }, format="json",
    secure = True,
    )

    assert resp.status_code == 400
    # DRF sends {"username": ["A user with that username already exists."]}
    data = resp.json()
    assert "username" in data


@pytest.mark.django_db
def test_register_password_too_short(): # Test registration with a too-short password.
    client = APIClient()

    resp = client.post("/api/auth/register/", {
        "username": "shortpw",
        "password": "abc",   # too short
    }, format="json",
    secure = True,
    )

    assert resp.status_code == 400
    data = resp.json()
    assert "password" in data
