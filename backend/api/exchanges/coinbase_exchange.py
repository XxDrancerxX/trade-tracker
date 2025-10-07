import os, time, hmac, hashlib, base64, requests
from urllib.parse import urlencode
from api.services.crypto_vault import CryptoVault


class CoinbaseExchangeAdapter:
    """
    Coinbase Exchange (Sandbox) adapter
    REST base: https://api-public.sandbox.exchange.coinbase.com
    """

    def __init__(self, api_key=None, api_secret_b64=None, passphrase=None, base_url=None):
        self.base_url = base_url or os.getenv("EX_BASE_URL", "https://api-public.sandbox.exchange.coinbase.com")
        self.api_key = api_key or os.getenv("EX_API_KEY_READ", "")
        self.api_secret_b64 = api_secret_b64 or os.getenv("EX_API_SECRET_READ", "")
        self.passphrase = passphrase or os.getenv("EX_API_PASSPHRASE_READ", "")

    # ---------- signing (for private endpoints) ----------
    def _headers(self, method: str, request_path: str, body: str = "") -> dict:
        ts = str(int(time.time()))
        msg = (ts + method.upper() + request_path + (body or "")).encode()
        sig = hmac.new(base64.b64decode(self.api_secret_b64), msg, hashlib.sha256).digest()
        return {
            "CB-ACCESS-KEY": self.api_key,
            "CB-ACCESS-SIGN": base64.b64encode(sig).decode(),
            "CB-ACCESS-TIMESTAMP": ts,
            "CB-ACCESS-PASSPHRASE": self.passphrase,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _get_public(self, path: str, params: dict | None = None):
        qs = urlencode(params or {})
        rp = f"{path}?{qs}" if qs else path
        r = requests.get(self.base_url + rp, timeout=15)
        r.raise_for_status()
        return r.json()

    def _get_private(self, path: str, params: dict | None = None):
        qs = urlencode(params or {})
        rp = f"{path}?{qs}" if qs else path
        r = requests.get(self.base_url + rp, headers=self._headers("GET", rp), timeout=15)
        r.raise_for_status()
        return r.json()

    # ---------- endpoints your cb.py calls ----------
    # Public
    def products(self):
        return self._get_public("/products")

    def product_ticker(self, product_id: str):
        return self._get_public(f"/products/{product_id}/ticker")

    # Private (need View perms + correct sandbox key/secret/passphrase)
    def accounts(self):
        return self._get_private("/accounts")

    def order_list(self, limit=50, status=None):
        params = {"limit": limit}
        if status:
            params["status"] = status
        return self._get_private("/orders", params)
