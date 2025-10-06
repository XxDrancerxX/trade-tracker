import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory
from api.serializers import ExchangeCredentialCreateSerializer
from api.services.crypto_vault import CryptoVault

@pytest.mark.django_db
def test_cred_serializer_encrypts():
    user = User.objects.create_user("u", "u@x.com", "p")
    factory = APIRequestFactory()
    req = factory.post("/", {})
    req.user = user

    ser = ExchangeCredentialCreateSerializer(
        data={
            "exchange": "coinbase-exchange",
            "label": "default",
            "api_key": "K",
            "api_secret": "S",
            "passphrase": "P",
        },
        context={"request": req},
    )
    assert ser.is_valid(), ser.errors
    obj = ser.save()

    # encrypted fields are bytes and not equal to plaintext
    assert isinstance(obj.api_key_enc, (bytes, bytearray))
    assert isinstance(obj.api_secret_enc, (bytes, bytearray))
    assert obj.api_key_enc != b"K"
    assert obj.api_secret_enc != b"S"

    # round-trip decryption matches original
    v = CryptoVault()
    assert v.dec(obj.api_key_enc) == "K"
    assert v.dec(obj.api_secret_enc) == "S"
    assert v.dec(obj.passphrase_enc) == "P"