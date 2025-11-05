from decimal import Decimal, InvalidOperation
from datetime import datetime, timezone
#This normalizer is not an HTTP endpoint, this is just a utility to convert Coinbase fill/order data into our internal SpotTrade format.
#feed  it per-fill dicts from /fills or completed order dicts from /orders so the downstream SpotTrade creation logic can treat them uniformly. Keeping the raw payload in notes helps diagnose mismatches between Coinbase endpoints.

def normalize_fill_to_spot(fill: dict) -> dict: ## The colon after fill is a type hint: fill is expected to be a dict (this is for readability/static type checkers only — not enforced at runtime).
    # > dict : Return type hint: the function is expected to return a dict. Again, informative for readers and tools (mypy), not enforced at runtime.
    """
    Convert a Coinbase fill/order JSON into our SpotTrade shape.
    Tolerates variations between /fills and /orders payloads.
    Raises ValueError on missing/invalid fields.
    """
    try:#Handle possible variations in field names and missing data.
        # accept multiple possible id keys (trade-level id, order id, fill id)
        raw_id = fill.get("trade_id") or fill.get("id") or fill.get("fill_id") or fill.get("order_id")
        if raw_id is None:
            raise KeyError("trade_id/id/fill_id/order_id") #Raises a KeyError if none of the expected ID keys are found in the fill dictionary.

        # product / symbol
        product_id = str(fill.get("product_id") or fill.get("instrument") or "") #We put an empty string as a last resort to avoid NoneType issues. so str("") is safe since it results in an empty string.
        if not product_id:
            # The subsequent if not product_id: raise KeyError("product_id") uses the empty string (which is falsy) to detect “missing” and raise a clear error. So the "" is just a sentinel that fails the check.
            # Avoids converting None → "None" (which would be wrong).
            raise KeyError("product_id") # Raises a KeyError if product_id is missing.

        side = str(fill.get("side") or "").upper() # convert side to uppercase string

        # amount: fills use "size", orders use "filled_size"
        # different Coinbase endpoints use different field names — /fills returns "size" while /orders returns "filled_size".
        size_raw = fill.get("size") or fill.get("filled_size") or fill.get("quantity") #this is the raw numeric value (string or number) for the trade amount.
        if size_raw is None:
            raise KeyError("size/filled_size/quantity")
        amount = Decimal(str(size_raw)) # convert to Decimal for precision

        # price: prefer explicit "price"; if missing compute from executed_value / filled_size
        price_raw = fill.get("price")
        if price_raw is not None:
            price = Decimal(str(price_raw))
        else:
            executed_value = fill.get("executed_value") or fill.get("usd_volume") or fill.get("funds")
            if executed_value is None:
                # price can be missing for some order payloads; compute requires executed_value
                raise KeyError("price or executed_value")
            try:#Guards against division errors and invalid numeric values such as non-numeric strings.
                price = Decimal(str(executed_value)) / (amount if amount != 0 else Decimal("1"))
            except (InvalidOperation, ZeroDivisionError) as e:
                raise ValueError(f"Invalid numeric values for price computation: {e}") from e

        # fee if available
        fee = Decimal(str(fill.get("fee") or fill.get("fill_fees") or "0"))

        # created / executed timestamp
        created_at = str(fill.get("created_at") or fill.get("done_at") or fill.get("time") or "")
        if not created_at:
            raise KeyError("created_at/done_at/time")
    except KeyError as e:
        raise ValueError(f"Missing required key: {e}") from e
    except InvalidOperation as e:
        raise ValueError(f"Invalid numeric value: {e}") from e

    try:  # parse ISO 8601 timestamp, ensure UTC
        trade_time = datetime.fromisoformat(created_at.replace("Z", "+00:00")).astimezone(timezone.utc)
    except Exception:
        raise ValueError(f"Invalid timestamp: {created_at}")

    # currency extraction
    currency = None
    if "-" in product_id:
        parts = product_id.split("-")
        if len(parts) >= 2:
            currency = parts[-1]

    notes = {  # include relevant raw fields for auditing/debugging
        "order_id": fill.get("order_id"),
        "fee": str(fee),
        "executed_value": str(fill.get("executed_value")) if fill.get("executed_value") is not None else None,
        "filled_size": str(fill.get("filled_size")) if fill.get("filled_size") is not None else None,
        "settled": fill.get("settled"),
        "market_type": fill.get("market_type"),
        "raw": fill,  # keep full payload for auditing/debug
    }

    return {
        "external_id": str(raw_id),
        "symbol": product_id,
        "side": side,
        "price": price,
        "amount": amount,
        "trade_time": trade_time,
        "exchange": "coinbase",
        "currency": currency,
        "notes": notes,
    }
# ...existing code...