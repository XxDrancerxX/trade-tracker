import logging
import json
from typing import Tuple, List
from django.db import transaction
from api.exchanges.coinbase_exchange import build_exchange_adapter
from api.services.ingestion.coinbase_normalizer import normalize_fill_to_spot
from api.models import SpotTrade, ExchangeCredential

logger = logging.getLogger(__name__) # module-level logger 
# logging is configured in the Django settings module for consistency across the project.
# Used here to log warnings and info about the sync process.

def sync_coinbase_fills_once(cred: ExchangeCredential, limit: int = 50) -> Tuple[int, int]:
    """
    Fetch one page of fills and insert as SpotTrade (idempotent).
    Returns (inserted_count, seen_count).
    """
    adapter = build_exchange_adapter(cred) # Instantiate the CoinbaseExchangeAdapter using the provided ExchangeCredential.
    fills = adapter.fills(limit=limit) # Fetch fills from Coinbase using the adapter's fills method, limited to the specified number.

    rows: List[SpotTrade] = []
    bad_count = 0

    for idx, f in enumerate(fills):# Iterate over each fill fetched from Coinbase.
        try:
            data = normalize_fill_to_spot(f) # Normalize the fill data into the internal SpotTrade format using the normalize_fill_to_spot function.
        except Exception as e: #Catches any exception that occurs during normalization.
            logger.warning("normalize failed idx=%s error=%s payload=%r", idx, e, f) #Logs a warning message with the index of the fill, the error message, and the original payload that caused the error.
            bad_count += 1
            continue

        notes_val = data.get("notes") # Extracts the "notes" field from the normalized data.
        if isinstance(notes_val, (dict, list)):
            data["notes"] = json.dumps(notes_val, separators=(",", ":"))  # TextField-safe

        rows.append(SpotTrade(user=cred.user, **data)) #Creates a new SpotTrade instance with the normalized data and appends it to the rows list.

    # seen = normalized rows we attempted to insert (bad payloads excluded)
    seen = len(rows)
    if not rows:
        if bad_count:
            logger.info("no rows to insert; bad=%d", bad_count)
        return 0, seen

    # Pre-check duplicates so inserted is accurate (only for non-null external_id)
    ext_ids = [r.external_id for r in rows if r.external_id] # Collects all non-null external IDs from the rows to check for duplicates in the database.
    existing: set[str] = set() # Initializes an empty set to hold existing external IDs found in the database.
    if ext_ids:
        existing = set(
            SpotTrade.objects.filter(
                user=cred.user, exchange="coinbase", external_id__in=ext_ids
            ).values_list("external_id", flat=True)
        )

    new_rows = [r for r in rows if not r.external_id or r.external_id not in existing]
    dupes = len(rows) - len(new_rows)
    if dupes:
        logger.info("skipping %d duplicates already in DB", dupes)

    inserted = 0
    if new_rows:
        with transaction.atomic():
            created_objs = SpotTrade.objects.bulk_create(
                new_rows, ignore_conflicts=True, batch_size=500
            )
            inserted = len(created_objs)   # ← count what the DB really inserted
    if bad_count:
        logger.info("skipped %d bad payloads", bad_count)

    return inserted, seen