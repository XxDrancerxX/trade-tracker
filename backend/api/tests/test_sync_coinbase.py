import pytest
from django.contrib.auth.models import User
from api.models import ExchangeCredential, SpotTrade
from api.services.ingestion.sync_coinbase import sync_coinbase_fills_once

@pytest.mark.django_db  # Use the Django test database for this test
def test_sync_happy_and_idempotent(monkeypatch): #monkeypatch is a pytest fixture for modifying/imported code during tests.
    # We use it to:
    # 1. Isolate external dependencies (network, time, filesystem).
    # 2. Inject fakes/stubs so tests are fast and deterministic.
    # 3. Avoid leaking changes between tests (auto-undo)
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
        def fills(self, *, limit=50, product_id=None, order_id=None):
            assert product_id == "BTC-USD"  # verify param passed through
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
    import api.services.ingestion.sync_coinbase as mod  # Import the module under test , mod is now a reference to that module.
    monkeypatch.setattr(mod, "build_exchange_adapter", lambda c: FakeAdapter())
    # sets/replaces an attribute on a module/object for the duration of the test, then automatically restores the original after the test.
    # Effect: inside sync_coinbase_fills_once, any call to build_exchange_adapter(...) uses our lambda, which returns FakeAdapter(), so .fills() returns our fake data (no real network).

    # Act + Assert
    inserted, seen = sync_coinbase_fills_once(cred, limit=50, product_id="BTC-USD") #call our sync function. Because we monkeypatched
    assert inserted == 2 # asserts that two new SpotTrade rows were inserted.
    assert seen == 2 # asserts that two fills were processed (normalized successfully).
    assert SpotTrade.objects.count() == 2 # asserts that there are exactly two SpotTrade rows in the database.

    # Run again → no new rows
    # We run it a second time to prove idempotency.
    # First call: inserts 2 new SpotTrade rows from the fake fills.
    # Second call (same input): should not create duplicates because:
    # the DB has a UniqueConstraint on (user, exchange, external_id),
    # the code pre-filters existing external_ids and uses ignore_conflicts on bulk_create.
    # The assertions verify:
    # inserted2 == 0 → nothing new was written,
    # seen2 == 2 → both payloads were still processed/normalized,
    # SpotTrade.objects.count() == 2 → DB row count didn’t change.
    inserted2, seen2 = sync_coinbase_fills_once(cred, limit=50)
    assert inserted2 == 0
    assert seen2 == 2
    assert SpotTrade.objects.count() == 2


@pytest.mark.django_db
def test_sync_skips_bad_payloads(monkeypatch, caplog):
    # checks error handling. The fake adapter returns one good fill (has product_id) and one bad fill (missing that field). 
    # Inside the sync code, the bad entry raises a ValueError; the ingest logic logs a warning and skips it. 
    # The test captures logs at WARNING level, runs the sync, and asserts that only the good trade inserted, seen equals 1 (only the normalized rows), and a warning mentioning “normalize failed” was written.
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
    # verifies deduplication by external_id. The fake adapter returns two fills with the same trade_id. With bulk_create(..., ignore_conflicts=True)
    # and the unique constraint on (user, exchange, external_id), only one row inserts. The test asserts (inserted, seen) == (1, 2)—both fills were processed (seen=2), but only one new row went into the database (inserted=1), and the SpotTrade table still holds a single row.
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

# Across all three, Pytest’s monkeypatch fixture swaps out network calls, the @pytest.mark.django_db marker enables database access,
# and the assertions focus on ingest counts and stored trades to prove the sync logic is correct, idempotent, tolerant of bad payloads, and respects uniqueness.


@pytest.mark.django_db
def test_sync_passes_filters(monkeypatch):
    seen_opts = {}
    class FakeAdapter:
        def fills(self, *, limit, product_id, order_id):
            seen_opts.update({"limit": limit, "product_id": product_id, "order_id": order_id})
            return []
    import api.services.ingestion.sync_coinbase as mod    
    monkeypatch.setattr(mod, "build_exchange_adapter", lambda c: FakeAdapter())
    sync_coinbase_fills_once(cred, limit=25, product_id="ETH-USD", order_id="abc")
    assert seen_opts == {"limit": 25, "product_id": "ETH-USD", "order_id": "abc"}