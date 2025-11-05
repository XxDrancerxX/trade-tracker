from api.services.ingestion.coinbase_normalizer import normalize_fill_to_spot
# Basic test for normalize_fill_to_spot function
# Run this test with pytest or similar testing framework.
# This test take the simplest possible valid fill dict and checks that the normalized output has the expected fields and values.

def test_normalize_fill_to_spot_basic():
    fill = {
        "trade_id": 42,
        "product_id": "BTC-USD",
        "side": "buy",
        "price": "65000.12",
        "size": "0.0015",
        "created_at": "2025-10-29T12:34:56Z",
    }
    got = normalize_fill_to_spot(fill)
    assert got["external_id"] == "42"
    assert got["symbol"] == "BTC-USD"
    assert got["side"] == "BUY"
    assert str(got["price"]) == "65000.12"
    assert str(got["amount"]) == "0.0015"
    assert got["exchange"] == "coinbase"
    assert got["currency"] == "USD"
    # timestamp is UTC-aware
    assert got["trade_time"].tzinfo is not None
    assert got["trade_time"].utcoffset().total_seconds() == 0

