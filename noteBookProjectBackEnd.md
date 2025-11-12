////////////////////////////
To remark notes:
# H1 Title
## H2 Section
### H3 Subsection
#### H4 Minor section

## Emphasis:
**bold**  _italic_  ~~strikethrough~~  `inline code`
Use <mark>highlight</mark> with HTML.

## Code blocks:
```bash
pytest --lf
python manage.py check
```
(Add the language after ``` for syntax highlighting.)

### Quotes / callouts


```md
> **Note:** DEBUG is False in CI to catch config issues.
> **Tip:** Use `pytest --cache-clear` if test selection seems off.
//////////////////////////


# 🐍 Python Package Structure: `__init__.py` Files

## **📦 Purpose: Mark Directories as Python Packages**

The `__init__.py` file tells Python: **"This directory is a package, not just a regular folder"**

### **Without `__init__.py`:**
```python
from api.models import User  # ❌ ModuleNotFoundError
```

### **With `__init__.py`:**
```python
from api.models import User  # ✅ Success!
```

## **🏗️ In Your Project Structure:**
```
backend/
├── api/
│   ├── __init__.py          # Makes 'api' a package
│   ├── models.py
│   ├── views.py
│   └── migrations/
│       └── __init__.py      # Makes 'api.migrations' a package
└── core/
    ├── __init__.py          # Makes 'core' a package
    └── settings.py
```

**Enables clean imports:**
```python
from api.models import ExchangeCredential
from api.services.crypto_vault import CryptoVault
from core.settings import DEBUG
```

## **📝 Content (Usually Empty):**
Most `__init__.py` files are **empty** - they just need to **exist** to mark the directory as a package.

## **🎯 Django Importance:**
- **App Recognition**: Django needs them to recognize apps (`api`, `core`)
- **Migration System**: `migrations/__init__.py` required for database migrations
- **Import Structure**: Enables hierarchical imports across Django apps

**Think of them as "package permission slips"** 📋

---

# 🧠 Engineer Log — Trade Tracker
This section summarizes all the key steps and explanations we've covered while setting up the project structure, CI, testing, and documentation.

# 🏗 1. Project Structure & Environment 

The repository uses a clear root structure:

/trade-tracker
├─ .github/workflows/        → GitHub Actions CI configs
├─ .vscode/                  → Editor settings (Python interpreter, pytest enabled)
├─ backend/                  → Django backend
├─ .gitignore
├─ LICENSE
├─ README.md
└─ noteBookProject.md        → Engineering notes (this file)


The virtual environment lives inside backend/.venv and is activated with:

source backend/.venv/bin/activate


Dependencies are installed via:

pip install -r requirements.txt

# ⚡ 2. CI Workflow (GitHub Actions) 

The CI uses GitHub Actions to automatically run tests on every push and pull request.

File: .github/workflows/pytest.yml

Key points explained:

🧱 runs-on → spins up an ephemeral Ubuntu VM per run (clean environment each time).

🧪 Installs Python 3.12, dependencies, then runs Django checks + pytest.

🔐 Uses GitHub Secrets for CI-safe environment variables.

🧠 DEBUG is set to "False" in CI to catch misconfigurations early.


# 🧪 3. Pytest & Test Execution
Running tests locally
## Run all tests
pytest -q

## Run only previously failed tests (from cache)
pytest --lf

## Clear cache before running
pytest --cache-clear -q


--lf uses .pytest_cache/ to remember previously failed tests.

If no failures exist, it runs all tests.

If failures exist, it runs only the failed ones for faster feedback.

The .pytest_cache/ folder is:

Auto-created by pytest after the first run.

Used for caching failed test info, node IDs, and stepwise runs.

Should be ignored in .gitignore:

.pytest_cache/

Example successful run:
api/tests.py/test_exchange_fills.py .
api/tests.py/test_vault.py .
================ 3 passed in 0.76s ==================

# 🐛 4. Common Errors & Fixes
Error	Cause	Fix
settings not configured	DJANGO_SETTINGS_MODULE not set	Add to pytest.ini
ModuleNotFoundError: api	Python path not pointing to backend	Add pythonpath = backend in pytest.ini and __init__.py files
Test failures persist	Cached failures from previous runs	Run pytest --cache-clear

# 📝 5. Engineering Log (This File)

Purpose: keep step-by-step notes, decisions, CI explanations, and troubleshooting in one place.

Lives in the root of the repo next to README.md.

Keeps documentation versioned with the code, unlike external Notion/Google Docs.

# 🧠 Knowledge Nuggets

.pytest_cache/ is pytest’s memory between runs, not part of your codebase.

CI environments are ephemeral, so every run starts clean — no local state is preserved.

Markdown logs in the root are a lightweight but powerful way to document workflows.

Setting DEBUG=False in CI ensures your production settings won’t break silently.

# 🧠 VS Code Settings:

VS Code acts as the main IDE for editing, testing, and managing the project.
The .vscode/settings.json file defines per-project editor behavior. Current setup:

python.defaultInterpreterPath → Points VS Code to the virtual environment inside backend/.venv. Ensures all linting, testing, and commands use the same Python as the terminal.

python.terminal.activateEnvironment → Auto-activates the venv in new terminals, so no need to run source .venv/bin/activate manually.

python.testing.pytestEnabled → Enables pytest for test discovery and running directly from the Test Explorer.

python.testing.unittestEnabled → Disabled to avoid conflicts (we use only pytest).

This keeps local development aligned with CI, avoids “works in terminal but not in editor” issues, and lets you run/manage tests through VS Code’s UI or terminal.

# 🧠 Virtual Environment (.venv) — Quick Summary

A .venv is a project-local Python environment that keeps dependencies isolated from the system and other projects.
It works by temporarily switching your shell’s PATH so python and pip point to the .venv folder instead of the global interpreter.

✨ Why It Matters

🧍 Isolation: Each project has its own library versions — no conflicts between Django 5 and Django 4, for example.

🧱 Reproducibility: Everyone (and CI) installs the exact same dependencies listed in requirements.txt.

🧼 Clean Removal: Deleting the .venv wipes all project dependencies without touching your system.

🛑 Safety: .venv/ is added to .gitignore to keep repos light and avoid OS-specific junk.


# ⚙️ Activate & Deactivate
**activate (Linux/macOS):**
source .venv/bin/activate

**deactivate:**
deactivate


After deactivation, your shell returns to the global Python interpreter.

📦 Recreating a .venv

If .venv breaks or on a new machine:

'''
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
'''

This restores everything exactly as before.

✅ Key idea: .venv is ignored by Git and can always be rebuilt from requirements.txt, making it both disposable and essential for stable development.

## 🧠 `__pycache__` Folders

- These folders are **auto-generated by Python** when modules are first **imported or executed**, not when installing dependencies.  
- Inside, Python stores **compiled bytecode** (`.pyc` files) to speed up future imports.  
- Each package or app (e.g. `api/`, `core/`, `exchanges/`) gets its own `__pycache__/` when code from that folder is used.  
- Safe to **delete at any time** — Python will recreate them automatically.  
- They are usually added to `.gitignore` to avoid committing unnecessary generated files.

## 🧠 MCP Server – Coinbase Docs Integration (VS Code)

### ✅ What We Did
- Set up **Coinbase Docs MCP Server** inside VS Code so we can query official API documentation directly from the chat sidebar.
- This allows quick searches like “Search for `trade API` in Coinbase docs” without leaving the editor.

### ⚡ Quick Setup Summary
1. Open VS Code and install an MCP-compatible extension (e.g. GitHub Copilot Chat).
2. Create or edit the MCP config file at:

Each time codespaces is closed this goes down so you need to restart each time you open codespaces.

ctrl + p
and then insert:
~/.vscode-remote/data/User/mcp.json

restart

3. Add the Coinbase server:

```json
{
  "servers": {
    "coinbase-docs": {
      "type": "sse",
      "url": "https://docs.cdp.coinbase.com/mcp"
    }
  },
  "inputs": []
}
```
 
4. Save the file — the Output panel should show:

[info] Connection state: Running
[info] Discovered 1 tools


5. In the VS Code Chat panel, try:

Search for "trade API" in Coinbase docs.
✅ You should see relevant documentation links appear.

## 📝 Notes:

URL: Must use https://docs.cdp.coinbase.com/mcp (❌ not /server or /sse).

Server Type: sse is correct.

If stuck on initialize, use Restart Server from the inline controls in mcp.json.

You can add multiple MCP servers (e.g. internal docs, other APIs) to the same file.



## 🔌 CoinbaseExchangeAdapter — quick notes

- Purpose: One-stop adapter for Coinbase Exchange REST API (sandbox by default), handling auth, headers, and convenient endpoints.

- Source: `backend/api/exchanges/coinbase_exchange.py`

- Config and creds:
  - Base URL: `EX_BASE_URL` (default: https://api-public.sandbox.exchange.coinbase.com), trimmed to avoid trailing `/`.
  - Auth env vars: `EX_API_KEY_READ`, `EX_API_SECRET_READ` (base64), `EX_API_PASSPHRASE_READ`.
  - Note: `CryptoVault` is imported but not used here; creds come from env.

- Auth/signing (private endpoints):
  - `_sign_headers(method, path, query="", body="")` builds `prehash = timestamp + METHOD + path + query + body`.
  - HMAC-SHA256 with base64-decoded secret → base64 signature.
  - Sends headers: `CB-ACCESS-KEY`, `CB-ACCESS-SIGN`, `CB-ACCESS-TIMESTAMP`, `CB-ACCESS-PASSPHRASE`.
  - `_headers()` adds `Content-Type`/`Accept` and wraps `_sign_headers`.
  - Requests use 15s timeout and `raise_for_status()` on errors.

- HTTP helpers:
  - `_get_public(path, params=None)`: GET without auth.
  - `_get_private(path, params=None)`: GET with signed headers.

- Endpoints exposed:
  - Public
    - `products()` → GET `/products`
    - `product_ticker(product_id)` → GET `/products/{id}/ticker`
  - Private
    - `accounts()` → GET `/accounts`
    - `order_list(limit=50, status=None)` → GET `/orders` (supports `status`)
    - `fills(limit=None, product_id=None, order_id=None)` → GET `/fills`
      - Coinbase requires either `order_id` OR `product_id`.
      - Supports `limit` and product/order filtering.

- Implementation notes:
  - Uses `urllib.parse.urlencode` to build query strings.
  - For signing, path and query are kept separate; request path is split at `?`.
  - `fills()` signs using the same `_sign_headers` logic and passes query.

- Common pitfalls:
  - `400 Bad Request` on `/fills` if neither `product_id` nor `order_id` is provided.
  - Sandbox keys and base URL are separate from production.
  - If private calls look empty, confirm key permissions and portfolio match.

- CLI examples (Django `cb`):
  - Products: `python manage.py cb products`
  - Ticker: `python manage.py cb ticker --product BTC-USD`
  - Accounts: `python manage.py cb accounts`
  - Orders: `python manage.py cb orders`
  - Fills: `python manage.py cb fills --product_id BTC-USD` or `--order_id <uuid>`; `--limit 10` to cap results

  ---

## 🛠 Django Management Command `cb` — quick notes

- Source: `backend/api/management/commands/cb.py`
- Purpose: Developer/debug CLI to hit Coinbase adapter endpoints and pretty-print JSON (no view/URL layer needed).
- Subcommand architecture:
  - Uses `parser.add_subparsers(dest="action", required=True)` so exactly one action must be chosen.
  - Registered subcommands: `products`, `accounts`, `ticker`, `orders`, `fills`, `sync_fills`.
  - Each subcommand gets its own arguments (e.g. `ticker --product`, `fills --product_id/--order_id/--limit`).
- Flow on execution (`python manage.py cb <action> [flags]`):
  1. Django loads `Command` class (name of file = command name: `cb.py` → `cb`).
  2. `add_arguments` defines subparsers and options.
  3. `handle()` receives parsed options in `opts` (e.g. `{"action": "fills", "product_id": "BTC-USD"}`).
  4. Instantiates `CoinbaseExchangeAdapter` and dispatches based on `action`.
  5. Validates creds for private calls (`accounts`, `orders`, `fills`).
  6. Serializes result with `json.dumps(..., indent=2, sort_keys=True)` to stdout.
- Error handling:
  - Wraps execution in try/except; any exception raised → re-raised as `CommandError` (prints clean error message + non‑zero exit code).
  - Explicit credential checks before private endpoints give clear messages instead of opaque 401s.
- Private vs Public:
  - Public: `products`, `ticker` (no key requirement).
  - Private: `accounts`, `orders`, `fills`, `sync_fills` (HMAC headers required).
- Extending pattern:
  - Add new endpoint: define `p_new = sub.add_parser("something")` in `add_arguments`; add flags via `p_new.add_argument(...)`; implement `elif action == "something": data = c.some_method(...)` in `handle()`.
  - Keep output JSON-only for easy piping: `python manage.py cb orders | jq '. | length'`.

### ▶️ sync-fills (one-page import)
- How it works: loads the user’s ExchangeCredential → builds Coinbase adapter → calls /fills → normalizes → de-dupes (DB + in-page) → bulk-inserts SpotTrade.

- Typical usage snippets:
  - List products: `python manage.py cb products`
  - Ticker for ETH: `python manage.py cb ticker --product ETH-USD`
  - Accounts (needs env creds): `python manage.py cb accounts`
  - Open/filled orders: `python manage.py cb orders`
  - Recent fills for product: `python manage.py cb fills --product_id BTC-USD --limit 5`
  - Fills by order id: `python manage.py cb fills --order_id <uuid>`
  - One-page sync into SpotTrade (private):`python manage.py cb sync_fills --username <user> [--label default] [--limit 50]`
  -python manage.py cb sync-fills --username alice --limit 100
# Run twice to verify idempotency (second run should insert 0)  

  Tips: add --verbosity 2 for more logs; replace placeholders like <user> with real values.

  - /orders endpoint returns only open orders when you omit the status filter. Once an order finishes and settles, Coinbase stops including it in that default response. 
  
- Gotchas:
  - Running from wrong directory → `manage.py` not found (must be in `backend/`).
  - `/fills` 400 if neither `product_id` nor `order_id` passed.
  - Placeholder `<your_order_id>` must be replaced with a real UUID (shell interprets `< >`).
  - Missing creds triggers early `CommandError` instead of HTTP failure.
- Rationale:
  - Faster iteration loop than building API views.
  - Encourages separation of transport (CLI) from adapter logic.

---

# 🔐 Credentials Storage, Encryption & Testing — Flow Summary

## 1. Purpose of this part of the system

Before you can safely hit Coinbase (or any exchange) on behalf of users, you need a secure way to store and retrieve their API credentials.

**The goal is:**
- ✅ Accept plaintext keys/passphrases once at the API boundary
- 🔐 Encrypt immediately using Fernet (CryptoVault)
- 🗄️ Persist only encrypted bytes in the database (`*_enc` fields)
- 🧪 Test this behavior to prevent regressions
- 🧠 Later, securely decrypt in memory to hit Coinbase's authenticated endpoints

## 2. Core components

### 🧱 Model — ExchangeCredential
- Stores encrypted credentials per user per exchange
- `*_enc` fields = encrypted bytes, not plaintext
- Linked to User via FK, allowing multi-user support

### ✍️ Serializer — ExchangeCredentialCreateSerializer
- Validates input, encrypts plaintext, and saves to the model
- `context={"request": req}` is passed automatically by DRF views (or manually in tests)
- `self.context["request"].user` ensures the credentials belong to the logged-in user

### 🔐 CryptoVault
- Field-level encryption using Fernet

## 3. The Test

### ✅ What it verifies
- Serializer validates and accepts input
- Encrypted bytes are stored in DB
- Stored data ≠ plaintext
- Decryption works round-trip
- context properly attaches the user

### 🧠 Why it's important
- This is your security regression test
- If anyone breaks encryption or stores plaintext by mistake, this fails immediately

## 4. Why we still need .env

`.env` now holds app-level config, not user secrets:
- `FIELD_ENCRYPTION_KEY` for CryptoVault ✅
- `DJANGO_SECRET_KEY`, `DATABASE_URL`, etc.
- Optional `EX_BASE_URL` (sandbox vs prod)

Per-user credentials live encrypted in the DB, not `.env`.

## 📌 Key Takeaways

- **Serializer + Model + CryptoVault = secure perimeter**
- **Tests guarantee encryption behavior never breaks**
- **Adapter = fetches from Coinbase**
- **Use-case = decrypt → call adapter → normalize → persist**
- **`.env` = app config, not user secrets**

This foundation makes your backend multi-user, secure, and ready to sync trades from multiple exchanges.

---

# 🧪 Test Analysis: `test_exchange_fills.py`

## 📍 **Location:** `/workspaces/trade-tracker/backend/api/tests/test_exchange_fills.py`

## 🎯 **Purpose:**
Tests the **CoinbaseExchangeAdapter.fills()** method without hitting real Coinbase servers using HTTP mocking.

## 🔄 **Test Workflow:**

### **1. Setup HTTP Mocking:**
```python
@responses.activate  # Hijacks requests.get() for the entire test
def test_fills_mock():
    responses.add(
        responses.GET, 
        "https://api-public.sandbox.exchange.coinbase.com/fills",
        json=[{"trade_id": 1, "product_id": "BTC-USD"}],  # Fake response data
        status=200
    )
```

### **2. Create Adapter with Fake Credentials:**
```python
c = CoinbaseExchangeAdapter("k","c2VjcmV0LWJhc2U2NA==","p", base_url=base)
```
- **"k"** = dummy API key
- **"c2VjcmV0LWJhc2U2NA=="** = dummy secret (base64)
- **"p"** = dummy passphrase
- **These don't need to be real** - they're just for testing the adapter logic

### **3. Call the Method:**
```python
data = c.fills(limit=1)  # Only passes limit parameter (product_id and order_id are optional)
```

### **4. Verify Mock Response:**
```python
assert data[0]["trade_id"] == 1  # Checks we got back the fake data correctly
```

## 🪄 **How HTTP Interception Works:**

1. **`@responses.activate`** → Replaces real `requests.get()` with fake version
2. **`responses.add()`** → Registers fake response for specific URL pattern
3. **Adapter calls `requests.get()`** → Gets intercepted by responses library
4. **Fake response returned** → No real network calls happen
5. **Test verifies fake data** → Proves adapter logic works correctly

## ✅ **What This Test Verifies:**
- **URL Construction:** `/fills?limit=1` built correctly
- **HTTP Method:** GET request sent properly  
- **Parameter Handling:** Optional parameters work (limit passed, others skipped)
- **JSON Parsing:** Response data accessible via `data[0]["trade_id"]`
- **Adapter Logic:** No syntax errors, proper method execution

## ❌ **What This Test Does NOT Cover:**
- **Real Authentication:** Uses dummy credentials, no actual HMAC signing
- **Network Errors:** No timeout, connection, or HTTP error testing
- **Credential Security:** No encryption/decryption involved
- **User Context:** No database or user isolation testing

## 🎯 **Key Insight:**
This is a **unit test** focused on adapter logic. It ensures your code can:
- Build correct URLs
- Handle optional parameters  
- Parse JSON responses
- Execute without errors

**Separate tests needed for:**
- Real credential encryption/decryption flow
- Error handling (network failures, 401s, etc.)
- Integration with encrypted credentials from database

## 📝 **Test Category:** 
**HTTP Adapter Unit Test** - Fast, reliable, no external dependencies.

------------------

# 🔐 Test Analysis: `test_vault.py`

## 📍 **Location:** `/workspaces/trade-tracker/backend/api/tests/test_vault.py`

## 🎯 **Purpose:**
Tests the **CryptoVault encryption/decryption system** - the core security component that protects user credentials in the database.

## 🔄 **Test Workflow:**

### **Simple Round-Trip Test:**
```python
def test_vault_roundtrip():
    v = CryptoVault()           # Loads FIELD_ENCRYPTION_KEY from .env
    ct = v.enc("secret")        # Encrypts "secret" → encrypted bytes
    assert v.dec(ct) == "secret" # Decrypts back → should match original
```

## ✅ **What This Test Verifies:**
- **Encryption works:** Plaintext gets scrambled into unreadable bytes
- **Decryption works:** Encrypted bytes restore to original text  
- **Round-trip integrity:** No data loss during encrypt/decrypt cycle
- **Environment setup:** `FIELD_ENCRYPTION_KEY` loads correctly from `.env`

## 🚨 **Critical Security Check:**
This is our **"encryption safety test"** - if this fails:
- ❌ User credentials won't be safely stored
- ❌ our security foundation is broken
- ❌ Risk of storing plaintext API keys in database

## 🧠 **Why It's Essential:**
- **Regression protection:** Catches broken encryption code immediately
- **Environment validation:** Ensures `.env` configuration works
- **Security confidence:** Proves encryption works before storing real data
- **CI integration:** Runs automatically on every code push

## 📝 **Test Category:** 
**Security Unit Test** - Fast, deterministic, no external dependencies.

**Flow:** `"secret" → encrypt → [random bytes] → decrypt → "secret"` ✅

