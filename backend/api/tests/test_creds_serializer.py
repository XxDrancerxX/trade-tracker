import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory
from api.serializers import ExchangeCredentialCreateSerializer
from api.services.crypto_vault import CryptoVault

#===============================================================================================================================

# What actually happens under the hood
# Test DB setup (once per run):
# pytest-django creates a temporary test database, applies your migrations, and points Django to it.
# Per-test isolation with a transaction:
# When a test marked django_db starts, pytest-django opens a database transaction.
# Your test does its work (e.g., User.objects.create_user(...), serializer .save(), etc.).
# When the test ends (pass or fail), pytest-django rolls back that transaction.
# Result: every row you created disappears—the DB is clean for the next test.
# Speed + cleanliness:
# Rolling back a transaction is much faster than rebuilding the DB each time, and it guarantees tests don’t leak data into each other.


@pytest.mark.django_db # Tells pytest this test will touch the database (create rows, query, save, create user, save model, etc.).
# Without it, any DB access raises: RuntimeError: Database access not allowed, use the "django_db" mark...
def test_cred_serializer_encrypts():
    """
    Proves the contract: valid input → bytes at rest, not plaintext → decrypts back. 
    This guards security forever (future refactors can’t silently remove encryption).
    """
    
    user = User.objects.create_user("u", "u@x.com", "p")  # Create a test user in the DB. ==>> (username, email, password) <<==
    factory = APIRequestFactory()  # DRF helper to create a mock HTTP request without running a server.
    req = factory.post("/", {}) # Create a mock POST request to "/" with an empty body ({}). Path doesn't matter here since we are not sending it to a view. we are just testing the serializer.
    req.user = user # Attach the test user to the request, simulating an authenticated request.

    ser = ExchangeCredentialCreateSerializer( # Instantiate our serializer with test input data.
        data={
            "exchange": "coinbase-exchange",
            "label": "default",
            "api_key": "K",
            "api_secret": "S",
            "passphrase": "P",
        },
        context={"request": req} # Serializers can access the request via self.context["request"] if needed (e.g., to get the current user).
    )
    

    # In tests, assert stops the test and shows the errors if validation fails
    assert ser.is_valid(), ser.errors # Validate the input data. If invalid, print errors.DRF decides between create() or update().
    # For creates, it calls our serializer’s create(self, validated_data).
    # This validated_data is where our "ser" variable goes and it goeas as parameter(validated) in our create method in serializer.
    obj = ser.save() # Calls the serializer's create() method, which encrypts the secrets and saves the ExchangeCredential instance to the DB.

    # encrypted fields are bytes and not equal to plaintext
    # round-trip decryption matches original
    # obj.api_key_enc / obj.api_secret_enc are the stored fields (from the model).
    # b"K" / b"S" are the plaintext bytes we originally sent ("K"/"S" converted to bytes).
    # If encryption worked, the stored values must differ from the plaintext bytes.
    
    assert isinstance(obj.api_key_enc, (bytes, bytearray)) #Ensure the DB stores ciphertext bytes, not plaintext strings. Guards type mistakes (e.g., accidentally storing str).
    assert isinstance(obj.api_secret_enc, (bytes, bytearray))
    #b just means a bytes literal in Python. 
    #b"K" → a bytes object containing the ASCII byte for K (0x4B)
    # Our model fields api_key_enc and api_secret_enc are BinaryField, which store bytes.
    #To check “not equal to plaintext,” we compare against plaintext as bytes, i.e., b"K" and b"S".
    assert obj.api_key_enc != b"K"
    assert obj.api_secret_enc != b"S"


    v = CryptoVault() # Instantiate our CryptoVault (which reads FIELD_ENCRYPTION_KEY from env).
    # Decrypt the stored ciphertext and verify it matches the original plaintext.
    # v.dec() returns a str, so we compare against "K" and "S" as strings.
    # If decryption works, we should get back the original plaintext values.
    assert v.dec(obj.api_key_enc) == "K"
    assert v.dec(obj.api_secret_enc) == "S"
    assert v.dec(obj.passphrase_enc) == "P"