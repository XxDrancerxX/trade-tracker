# Ensures every test run has a valid field-encryption key.
import os
import pytest
from cryptography.fernet import Fernet

@pytest.fixture(autouse=True, scope="session") # Automatically run for the entire test session
def _field_encryption_key(): # Ensures FIELD_ENCRYPTION_KEY is set for tests
    os.environ.setdefault("FIELD_ENCRYPTION_KEY", Fernet.generate_key().decode()) # Generate a new key if not already set
