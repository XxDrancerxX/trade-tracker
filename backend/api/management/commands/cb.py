from django.core.management.base import BaseCommand, CommandError
import  json

#This command is intended for development and debugging purposes only.
#It allows you to call certain Coinbase Exchange API endpoints via your adapter
#and pretty-print the results to the console.


class Command(BaseCommand):
    #BaseCommand is what connects your code to Django’s command system, making your command discoverable and runnable via manage.py.
    """
    BaseCommand is a Django class (django.core.management.base.BaseCommand) that you subclass to create a custom management command
    (run via python manage.py <command>). It wires your code into Django’s CLI: argument parsing, settings setup, stdout/stderr, and error handling.
    """

    help = "Call Coinbase Exchange Sandbox via your adapter and pretty-print the result." #Sets a help message for your Django management command.When you run python manage.py help cb.

    def add_arguments(self, parser):
        """
        Parser   is an object provided by Django (based on Python ’s argparse library)
        that helps define and process command-line arguments for your management command.
        argparse is Python’s standard library for building command-line interfaces (CLIs). 
        It parses the arguments a user types after your script/command and gives you a clean Namespace (like a dict) with typed values. 
        """

        sub = parser.add_subparsers(dest="action", required=True) #Defines subcommands (like git commit, git push). Each subcommand can have its own arguments.
        #sub.add_parser("products"), sub.add_parser("accounts"), sub.add_parser("orders"), sub.add_parser("ticker") ==>> Creates subcommands for your management command.
        #dest="action" means: “store the chosen subcommand under the key 'action'.”
        sub.add_parser("products")
        sub.add_parser("accounts")
        p_fills = sub.add_parser("fills")
        p_fills.add_argument("--product_id", type=str, help="Product ID to filter fills (e.g. BTC-USD)")
        p_fills.add_argument("--order_id", type=str, help="Order ID to filter fills")
        p_fills.add_argument("--limit", type=int, help="Limit number of results", default=None)
        p = sub.add_parser("ticker")
        p.add_argument("--product", default="BTC-USD") #Adds an optional argument --product to the ticker subcommand, with a default value of BTC-USD.
        #So you can do:
        # python manage.py cb ticker --product ETH-USD
        #Result ends up as opts["product"] == "ETH-USD" (or "BTC-USD" if omitted).        
        p_orders = sub.add_parser("orders") #Adds an orders subcommand.
        p_orders.add_argument("--status", default=None, help='Coinbase order status: open, done, all, etc.') #Optional argument --status for filtering orders by status.
        # NEW: Sync Coinbase Fills:
        p_sync = sub.add_parser("sync_fills")
        p_sync.add_argument("--username", required=True, help="Owner of the ExchangeCredential")
        p_sync.add_argument("--label", default="default", help="Credential label (default: default)")
        p_sync.add_argument("--limit", type=int, default=50, help="Page size (default: 50)")
        p_sync.add_argument("--product_id", help="Coinbase product like BTC-USD")
        p_sync.add_argument("--order_id", help="Specific order UUID")



    def handle(self, *args, **opts):
        # *args: ordered positional args you defined with parser.add_argument("name"). If you didn’t define positional args, this is usually empty.
        # **opts: everything else from argparse—i.e., named options (like --product) and values produced by your subparsers (dest="action").
        # So for python manage.py cb ticker --product ETH-USD, Django passes:
        # args == ()  # no positionals
        # opts == {"action": "ticker", "product": "ETH-USD"}
        """
        This is where the main logic of our management command goes.
        It parses the CLI into:
            - positional arguments → go into *args (a tuple).
            - options/flags/subcommand values → go into **opts (a dict).
        """
        from api.exchanges.coinbase_exchange import CoinbaseExchangeAdapter
        c = CoinbaseExchangeAdapter()  #  Instantiate your CoinbaseExchangeAdapter (which handles API calls to Coinbase Exchange).

        action = opts["action"] # Get which subcommand the user chose (like "products", "accounts", etc.). 
        try: #Error handling: if anything goes wrong in the try block, it raises a CommandError with the error message.
            if action == "products": #If user called python manage.py cb products then it calls c.products() to fetch product data from Coinbase Exchange.
                data = c.products()
            elif action == "accounts":
                if not (c.api_key and c.api_secret_b64 and c.passphrase):
                    raise CommandError("Missing API creds for private call (accounts).") #Accounts is a private API call, so it checks if API credentials are set; if not, it raises an error.
                data = c.accounts()
            elif action == "ticker":
                data = c.product_ticker(opts["product"])
            elif action == "orders": #Orders is the endpoint for fetching user orders.
                if not (c.api_key and c.api_secret_b64 and c.passphrase):
                    raise CommandError("Missing API creds for private call (orders).")
                status = opts.get("status") #Gets the --status option value if provided; otherwise, None.
                data = c.order_list(status=status) if hasattr(c, "order_list") else []#Calls c.order_list(...) to fetch orders from Coinbase Exchange, filtering by status if given.
            elif action == "fills": #Fills is the endpoint for trade fills (completed trades).
                product_id = opts.get("product_id")
                order_id = opts.get("order_id")
                limit = opts.get("limit")
                data = c.fills(limit=limit, product_id=product_id, order_id=order_id) if hasattr(c, "fills") else []
                # sync_fills:  action to sync fills into our database.

            elif action == "sync_fills":
                from django.contrib.auth.models import User
                from api.models import ExchangeCredential
                from api.services.ingestion.sync_coinbase import sync_coinbase_fills_once

                username = opts["username"]
                label = opts["label"]
                limit = opts["limit"]

                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    raise CommandError(f"User '{username}' not found")

                try:
                    cred = ExchangeCredential.objects.get(
                        user=user, exchange="coinbase", label=label
                    )
                except ExchangeCredential.DoesNotExist:
                    raise CommandError(
                        f"ExchangeCredential not found for user='{username}', exchange='coinbase', label='{label}'"
                    )

                inserted, seen = sync_coinbase_fills_once(
                        cred,
                        limit=limit,
                        product_id=opts.get("product_id"),
                        order_id=opts.get("order_id"),
                    )
                self.stdout.write(self.style.SUCCESS(f"sync done: inserted={inserted} seen={seen}"))
                return    
                          
            else:
                raise CommandError(f"Unknown action: {action}") #If the user provides an invalid subcommand, raises a CommandError with a message like "Unknown action: ...".

            self.stdout.write(json.dumps(data, indent=2, sort_keys=True))
            """self.stdout.write(...) is a Django method for printing output to the terminal when running a management command.
                json.dumps(data, indent=2, sort_keys=True):
                Converts the data object (usually a Python dictionary or list returned from the Coinbase API) into a formatted JSON string.
                indent=2 makes the output pretty and readable, with each level indented by 2 spaces.
                sort_keys=True sorts the keys in dictionaries alphabetically for easier reading.
            """
            #After your command fetches data from Coinbase (products, accounts, ticker, or orders), it stores the result in data.

        except Exception as e:#Catches any exception(Error) that occurs in the try block and stores it in variable e.
            raise CommandError(str(e))#Converts the error to a string and raises a Django CommandError.