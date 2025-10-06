import os, time, hmac, hashlib, base64, requests
from urllib.parse import urlencode
from api.services.crypto_vault import CryptoVault

class CoinbaseExchangeAdapter:
    """
    Coinbase Exchange (Pro) sandbox adapter.
    Base URL: https://api-public.sandbox.exchange.coinbase.com
    """
    def __init__(self, api_key, api_secret_b64, passphrase, base_url=None):
        self.base_url = base_url or os.getenv("EX_BASE_URL", "https://api.exchange.coinbase.com")
        self.api_key = api_key
        self.api_secret_b64 = api_secret_b64
        self.passphrase = passphrase

    def _headers(self, method, request_path, body=""):
        ts = str(int(time.time()))
        msg = (ts + method + request_path + body).encode()
        sig = hmac.new(base64.b64decode(self.api_secret_b64), msg, hashlib.sha256).digest()
        return {
            "CB-ACCESS-KEY": self.api_key,
            "CB-ACCESS-SIGN": base64.b64encode(sig).decode(),
            "CB-ACCESS-TIMESTAMP": ts,
            "CB-ACCESS-PASSPHRASE": self.passphrase,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _get(self, path, params=None):
        qs = urlencode(params or {})
        rp = f"{path}?{qs}" if qs else path
        r = requests.get(self.base_url + rp, headers=self._headers("GET", rp), timeout=15)
        r.raise_for_status()
        return r.json()

    def accounts(self):
        return self._get("/accounts")

    def fills(self, product_id=None, limit=100):
        p = {"limit": limit}
        if product_id:
            p["product_id"] = product_id
        return self._get("/fills", p)

def build_exchange_adapter(cred):
    v = CryptoVault()
    return CoinbaseExchangeAdapter(
        api_key=v.dec(cred.api_key_enc),
        api_secret_b64=v.dec(cred.api_secret_enc),
        passphrase=v.dec(cred.passphrase_enc) if cred.passphrase_enc else "",
        base_url=os.getenv("EX_BASE_URL"),
    )

