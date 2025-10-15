# api/tests.py/test_exchange_fills.py
import responses #It's an HTTP mocking library for requests. It intercepts HTTP calls and returns fake responses we define.
from api.exchanges.coinbase_exchange import CoinbaseExchangeAdapter #Import the CoinbaseExchangeAdapter class from our codebase.
#This test It checks that CoinbaseExchangeAdapter.fills() builds the correct URL and makes a GET request.

@responses.activate #Decorator to activate the responses library for the duration of the test function.
def test_fills_mock():
    #
    base = "https://api-public.sandbox.exchange.coinbase.com" #Base URL for Coinbase's sandbox API.  
    responses.add( #Mock the GET request to the /fills endpoint ,tells the responses library to intercept GET requests to this URL and return the specified JSON data with a 200 status code.
        responses.GET, f"{base}/fills", #Only intercept GET requests to this URL
        json=[{"trade_id": 1, "product_id": "BTC-USD"}], #The body of the mocked response to return.
        # responses will serialize this list to JSON for us.
        status=200,
    )
    # "If anyone calls GET to this exact URL, return this fake JSON"
    """
    When this test runs, all HTTP requests get intercepted
    No real network calls happen
    """
    c = CoinbaseExchangeAdapter("k","c2VjcmV0LWJhc2U2NA==","p", base_url=base) #Instantiate the adapter with fake credentials and the sandbox base URL.
    data = c.fills(limit=1)
    assert data[0]["trade_id"] == 1  #Check that the returned data from the coinbaseadapter matches the mocked response we did before wich is one.

