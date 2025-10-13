# api/tests.py/test_exchange_fills.py
import responses
from api.exchanges.coinbase_exchange import CoinbaseExchangeAdapter

@responses.activate
def test_fills_mock():
    base = "https://api-public.sandbox.exchange.coinbase.com"
    responses.add(
        responses.GET, f"{base}/fills",
        json=[{"trade_id": 1, "product_id": "BTC-USD"}],
        status=200,
    )
    c = CoinbaseExchangeAdapter("k","c2VjcmV0LWJhc2U2NA==","p", base_url=base)
    data = c.fills(limit=1)
    assert data[0]["trade_id"] == 1
