from django.core.management.base import BaseCommand, CommandError
import  json


class Command(BaseCommand):
    help = "Call Coinbase Exchange Sandbox via your adapter and pretty-print the result."

    def add_arguments(self, parser):
        sub = parser.add_subparsers(dest="action", required=True)
        sub.add_parser("products")
        sub.add_parser("accounts")
        p = sub.add_parser("ticker")
        p.add_argument("--product", default="BTC-USD")
        sub.add_parser("orders")

    def handle(self, *args, **opts):
        from api.exchanges.coinbase_exchange import CoinbaseExchangeAdapter
        c = CoinbaseExchangeAdapter()  # relies on env loaded by settings.py

        action = opts["action"]
        try:
            if action == "products":
                data = c.products()
            elif action == "accounts":
                if not (c.api_key and c.api_secret_b64 and c.passphrase):
                    raise CommandError("Missing API creds for private call (accounts).")
                data = c.accounts()
            elif action == "ticker":
                data = c.product_ticker(opts["product"])
            elif action == "orders":
                if not (c.api_key and c.api_secret_b64 and c.passphrase):
                    raise CommandError("Missing API creds for private call (orders).")
                data = c.order_list() if hasattr(c, "order_list") else []
            else:
                raise CommandError(f"Unknown action: {action}")

            self.stdout.write(json.dumps(data, indent=2, sort_keys=True))
        except Exception as e:
            raise CommandError(str(e))