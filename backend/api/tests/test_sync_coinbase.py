import pytest
from django.contrib.auth.models import User
from api.models import ExchangeCredential, SpotTrade
from api.services.ingestion.sync_coinbase import sync_coinbase_fills_once

@pytest.mark.django_db
def test_sync_happy_and_idempotent(monkeypatch):
    """
    First run inserts 2 trades. Second run inserts 0 (idempotent).
    """
    # Arrange: user + dummy cred row (bytes for *_enc fields)
    user = User.objects.create_user("u", "u@x.com", "p")
    cred = ExchangeCredential.objects.create(
        user=user,
        exchange="coinbase",
        label="default",
        api_key_enc=b"x",
        api_secret_enc=b"y",
        passphrase_enc=b"z",
    )

    # Fake adapter
    class FakeAdapter:
        def fills(self, limit=50):
            return [
                {
                    "trade_id": 1,
                    "product_id": "BTC-USD",
                    "side": "buy",
                    "price": "65000.00",
                    "size": "0.001",
                    "created_at": "2025-10-29T12:00:00Z",
                },
                {
                    "trade_id": 2,
                    "product_id": "ETH-USD",
                    "side": "sell",
                    "price": "3500.50",
                    "size": "0.010",
                    "created_at": "2025-10-29T12:01:00Z",
                },
            ]

    # Monkeypatch the factory to return our fake adapter
    import api.services.ingestion.sync_coinbase as mod
    monkeypatch.setattr(mod, "build_exchange_adapter", lambda c: FakeAdapter())

    # Act + Assert
    inserted, seen = sync_coinbase_fills_once(cred, limit=50)
    assert inserted == 2
    assert seen == 2
    assert SpotTrade.objects.count() == 2

    # Run again → no new rows
    inserted2, seen2 = sync_coinbase_fills_once(cred, limit=50)
    assert inserted2 == 0
    assert seen2 == 2
    assert SpotTrade.objects.count() == 2


@pytest.mark.django_db
def test_sync_skips_bad_payloads(monkeypatch, caplog):
    """
    One good, one bad (missing product_id). Good inserts; bad is logged and skipped.
    seen = number of normalized rows (bad excluded).
    """
    user = User.objects.create_user("u2", "u2@x.com", "p")
    cred = ExchangeCredential.objects.create(
        user=user,
        exchange="coinbase",
        label="default",
        api_key_enc=b"x",
        api_secret_enc=b"y",
        passphrase_enc=b"z",
    )

    class FakeAdapter:
        def fills(self, limit=50):
            return [
                {  # good
                    "trade_id": 10,
                    "product_id": "BTC-USD",
                    "side": "buy",
                    "price": "65000",
                    "size": "0.002",
                    "created_at": "2025-10-29T12:02:00Z",
                },
                {  # bad: no product_id
                    "trade_id": 11,
                    "side": "buy",
                    "price": "1",
                    "size": "1",
                    "created_at": "2025-10-29T12:03:00Z",
                },
            ]

    import api.services.ingestion.sync_coinbase as mod
    monkeypatch.setattr(mod, "build_exchange_adapter", lambda c: FakeAdapter())

    with caplog.at_level("WARNING"):
        inserted, seen = sync_coinbase_fills_once(cred, limit=50)

    assert inserted == 1
    assert seen == 1                # bad was excluded from "seen"
    assert SpotTrade.objects.count() == 1
    # one warning about normalization failure
    assert any("normalize failed" in rec.message for rec in caplog.records)


@pytest.mark.django_db
def test_sync_duplicate_in_same_page(monkeypatch):
    """
    Two fills with the same trade_id in a single page.
    With the corrected counting (len(created_objs)), inserted == 1, seen == 2.
    """
    user = User.objects.create_user("u3", "u3@x.com", "p")
    cred = ExchangeCredential.objects.create(
        user=user,
        exchange="coinbase",
        label="default",
        api_key_enc=b"x",
        api_secret_enc=b"y",
        passphrase_enc=b"z",
    )

    class FakeAdapter:
        def fills(self, limit=50):
            base = {
                "product_id": "BTC-USD",
                "side": "buy",
                "price": "65000",
                "size": "0.001",
                "created_at": "2025-10-29T12:04:00Z",
            }
            a = {"trade_id": 99, **base}
            b = {"trade_id": 99, **base}  # duplicate external_id
            return [a, b]

    import api.services.ingestion.sync_coinbase as mod
    monkeypatch.setattr(mod, "build_exchange_adapter", lambda c: FakeAdapter())

    inserted, seen = sync_coinbase_fills_once(cred, limit=50)
    assert inserted == 1   # only one actually inserted
    assert seen == 2       # both normalized
    assert SpotTrade.objects.count() == 1
