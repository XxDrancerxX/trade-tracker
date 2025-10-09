import os, time, hmac, hashlib, base64, requests    
from urllib.parse import urlencode 
from api.services.crypto_vault import CryptoVault


# - API requests require a dynamic signature for security.
# - The signature (CB-ACCESS-SIGN) is generated using HMAC-SHA256 with our base64-decoded API secret.
# - Each signature is unique per request, based on timestamp, method, path, and body.
# - The signature is encoded in base64 and sent in the request header.
# - API key, secret, and passphrase are all required for authenticated requests(given toether when creating the API key).
# - See: https://docs.cdp.coinbase.com/exchange/rest-api/authentication

class CoinbaseExchangeAdapter:  # handle authentication for Coinbase API requests
    def __init__(self, api_key=None, api_secret_b64=None, passphrase=None, base_url=None):
        self.base_url = (base_url or os.getenv("EX_BASE_URL", "https://api-public.sandbox.exchange.coinbase.com")).rstrip("/")
        self.api_key = api_key or os.getenv("EX_API_KEY_READ", "")
        self.api_secret_b64 = api_secret_b64 or os.getenv("EX_API_SECRET_READ", "")
        self.passphrase = passphrase or os.getenv("EX_API_PASSPHRASE_READ", "")



    # ||| Single source of truth for signing||| #
    # It generates the required headers (including the signature) that you must include when sending a private/authenticated request to the Coinbase API.
    # method: HTTP method for the request (e.g., "GET", "POST")
    # path: API endpoint path (e.g., "/accounts")
    # query: URL query string for parameters (e.g., "?limit=50"), optional
    # body: Request body for POST/PUT requests, optional
    def _sign_headers(self, method: str, path: str, query: str = "", body: str = "") -> dict:
        if not (self.api_key and self.api_secret_b64 and self.passphrase):  # If any are missing immediately stops the program (or function) and throws a RuntimeError exception.
            raise RuntimeError("Auth required: api_key / api_secret / passphrase missing")  # It will print an error message in the terminal or console where your Python program is running.
        ts = str(int(time.time())) # Current timestamp in seconds since epoch, Coinbase expects the timestamp as a string.
        prehash = f"{ts}{method.upper()}{path}{query}{body}" # The string that will be signed, constructed by concatenating the timestamp, HTTP method, request path, query string, and body.
        secret = base64.b64decode(self.api_secret_b64) # Decodes the API secret base64-encoded string back into its original binary form (raw bytes).HMAC expects a binary key, not a string of Base64 characters.
        # hmac.new() prepares the HMAC calculation.
        #.hexdigest() to get the signature as a hexadecimal string.
        #.digest() on that object produces the actual 256-bit binary signature.
        sig = hmac.new(secret, prehash.encode(), hashlib.sha256).digest()#Takes the secret key (in bytes), the prehash string (also in bytes with .encode()), and the hashing algorithm (SHA256) as inputs, and produces a binary signature.
        
        #HTTP headers must be text, not raw binary data.
        #base64.b64encode(sig) converts the binary signature into a base64-encoded string (using only safe, printable characters).
        #.decode() turns that base64 bytes object into a regular string.
        return {
            "CB-ACCESS-KEY": self.api_key,
            "CB-ACCESS-SIGN": base64.b64encode(sig).decode(),
            "CB-ACCESS-TIMESTAMP": ts,
            "CB-ACCESS-PASSPHRASE": self.passphrase,
        }
    
        #Summary:
        # You decode your secret from base64.
        # Build a prehash string from request details.
        # Convert prehash to bytes.
        # Use HMAC-SHA256 to create a 256-bit (32-byte) signature.
        # Encode the signature in base64 for safe transmission.
        # Send all as headers in your API request.



    
    # It takes:
    # method: HTTP method for the request (e.g., "GET", "POST")
    # request_path: Full API endpoint path including query string (e.g., "/accounts?limit=50")
    # body: the exact JSON string you’ll send in the request body (empty for GET).

    # It returns a dictionary of headers including the signature.
    # It extracts the path and query from request_path, then calls _sign_headers to get the signed headers.
    # It adds Content-Type and Accept headers, which are optional for GET requests but harmless to include.

    def _headers(self, method: str, request_path: str, body: str = "") -> dict: # This is a helper method to build the HTTP headers for your API request.
        # path = everything before ? (the clean path, e.g. "/api/v3/brokerage/orders").
        # _ = the actual ? character (we don’t need it, so underscore).
        # q = everything after ? (the raw query string, e.g. "limit=100&cursor=abc").
        # For HMAC signing, you must be precise about what you sign. Keeping path and query separate helps build the prehash exactly.
        path, _, q = request_path.partition("?") # .partition("?") splits the string once, at the first ?.It always returns 3 parts: (before, separator, after)
        query = f"?{q}" if q else ""
        h = self._sign_headers(method, path, query, body) # It calls our _sign_headers function and it pass the parameters + the query if there is a query to build Coinbase auth headers by signing (timestamp+method+path+query+body) with HMAC-SHA256.
        # Optional for GETs; harmless to include:
        h["Content-Type"] = "application/json"
        h["Accept"] = "application/json"
        return h



    # Low-level request methods (wrap these in higher-level methods as needed)
    def _get_public(self, path: str, params: dict | None = None):
        qs = urlencode(params or {})
        rp = f"{path}?{qs}" if qs else path
        r = requests.get(self.base_url + rp, timeout=15)
        r.raise_for_status()
        return r.json()
    
    # Private requests use the same signing logic 
    def _get_private(self, path: str, params: dict | None = None):
        qs = urlencode(params or {})
        rp = f"{path}?{qs}" if qs else path
        # Uses the shim, which delegates to _sign_headers
        r = requests.get(self.base_url + rp, headers=self._headers("GET", rp), timeout=15)
        r.raise_for_status()
        return r.json()

    # High-level API methods (wrap these as needed)
    # Public
    def products(self):
        return self._get_public("/products")

    # Get ticker for a specific product
    # e.g. BTC-USD, ETH-USD, LTC-USD     
    def product_ticker(self, product_id: str):
        return self._get_public(f"/products/{product_id}/ticker")

    #   Private
    # Get all accounts (wallets)
    # Requires authentication 
    def accounts(self):
        return self._get_private("/accounts")

    # List orders (open and completed)
    # status can be "open", "pending", "active", "done", or "all"
    # Default limit is 50, max is 100
    # Requires authentication 
    def order_list(self, limit=50, status=None):
        params = {"limit": limit}
        if status:
            params["status"] = status
        return self._get_private("/orders", params)
    
    # List fills (trade executions)
    # limit: Default 100, max 100
    # product_id: Optional filter by product (e.g. BTC-USD)
    # Requires authentication
    def fills(self, limit: int | None = None, product_id: str | None = None):
        path = "/fills"
        params = {}
        if limit is not None:
            params["limit"] = int(limit)
        if product_id:
            params["product_id"] = product_id
        query = f"?{urlencode(params)}" if params else ""
        url = f"{self.base_url}{path}{query}"
        # Reuse the same signing logic as everything else
        headers = self._sign_headers("GET", path, query)
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        return r.json()
