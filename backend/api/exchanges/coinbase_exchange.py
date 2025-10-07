import os, time, hmac, hashlib, base64, requests
from urllib.parse import urlencode
from api.services.crypto_vault import CryptoVault


class CoinbaseExchangeAdapter:
    def __init__(self, api_key=None, api_secret_b64=None, passphrase=None, base_url=None):
        self.base_url = (base_url or os.getenv("EX_BASE_URL", "https://api-public.sandbox.exchange.coinbase.com")).rstrip("/")
        self.api_key = api_key or os.getenv("EX_API_KEY_READ", "")
        self.api_secret_b64 = api_secret_b64 or os.getenv("EX_API_SECRET_READ", "")
        self.passphrase = passphrase or os.getenv("EX_API_PASSPHRASE_READ", "")

    # Single source of truth for signing
    def _sign_headers(self, method: str, path: str, query: str = "", body: str = "") -> dict:
        if not (self.api_key and self.api_secret_b64 and self.passphrase):
            raise RuntimeError("Auth required: api_key / api_secret / passphrase missing")
        ts = str(int(time.time()))
        prehash = f"{ts}{method.upper()}{path}{query}{body}"
        secret = base64.b64decode(self.api_secret_b64)
        sig = hmac.new(secret, prehash.encode(), hashlib.sha256).digest()
        return {
            "CB-ACCESS-KEY": self.api_key,
            "CB-ACCESS-SIGN": base64.b64encode(sig).decode(),
            "CB-ACCESS-TIMESTAMP": ts,
            "CB-ACCESS-PASSPHRASE": self.passphrase,
        }

    # Backwards-compat shim (you can delete this once you’ve updated call sites)
    def _headers(self, method: str, request_path: str, body: str = "") -> dict:
        path, _, q = request_path.partition("?")
        query = f"?{q}" if q else ""
        h = self._sign_headers(method, path, query, body)
        # Optional for GETs; harmless to include:
        h["Content-Type"] = "application/json"
        h["Accept"] = "application/json"
        return h

    def _get_public(self, path: str, params: dict | None = None):
        qs = urlencode(params or {})
        rp = f"{path}?{qs}" if qs else path
        r = requests.get(self.base_url + rp, timeout=15)
        r.raise_for_status()
        return r.json()

    def _get_private(self, path: str, params: dict | None = None):
        qs = urlencode(params or {})
        rp = f"{path}?{qs}" if qs else path
        # Uses the shim, which delegates to _sign_headers
        r = requests.get(self.base_url + rp, headers=self._headers("GET", rp), timeout=15)
        r.raise_for_status()
        return r.json()

    # Public
    def products(self):
        return self._get_public("/products")

    def product_ticker(self, product_id: str):
        return self._get_public(f"/products/{product_id}/ticker")

    # Private
    def accounts(self):
        return self._get_private("/accounts")

    def order_list(self, limit=50, status=None):
        params = {"limit": limit}
        if status:
            params["status"] = status
        return self._get_private("/orders", params)

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
