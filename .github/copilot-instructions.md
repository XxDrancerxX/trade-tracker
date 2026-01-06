# Trade Tracker - AI Copilot Instructions

## Project Overview
Trade Tracker is a full-stack crypto trading application with a Django REST API backend and React frontend. It allows users to connect exchange credentials, track trades (spot and futures), and analyze trading activity.

**Key Stack:**
- **Backend:** Django 5.2, Django REST Framework, SimpleJWT, SQLite
- **Frontend:** React 19, Vite, React Router
- **External API:** Coinbase Exchange (REST API with HMAC-SHA256 signing)

## Architecture & Data Flow

### Backend Structure
```
backend/
├── core/              # Django project config (settings, URLs, auth)
├── api/               # Main app
│   ├── models.py      # User, ExchangeCredential, SpotTrade, FuturesTrade
│   ├── views.py       # REST endpoints (register, login, trade CRUD)
│   ├── serializers.py # Validation & JSON serialization
│   ├── exchanges/     # Exchange adapters (Coinbase, etc.)
│   └── services/      # Business logic (CryptoVault, ingestion)
└── manage.py          # Django CLI
```

### Key Models
- **ExchangeCredential**: Stores encrypted API key/secret/passphrase (one per user per exchange)
  - Uses `CryptoVault` for encryption
  - `can_trade` and `can_transfer` boolean flags control permissions
- **SpotTrade / FuturesTrade**: User trades linked via ForeignKey to User
  - `external_id`: Exchange trade ID (unique per user+exchange, allows NULL duplicates)
  - `user`: Enforces data isolation - users only see their own trades

### Authentication Flow
1. User registers via `POST /api/auth/register/` → creates User + JWT tokens
2. Tokens stored as **HttpOnly cookies** (`tt_access`, `tt_refresh`)
3. All protected endpoints use `CookieJWTAuthentication` (reads `tt_access` from cookie)
4. Token refresh: `POST /api/auth/token/refresh/` updates cookies on 401
5. Cookie-based design ensures frontend never touches raw tokens

### API Endpoints
- `POST /api/auth/register/` - Create account
- `POST /api/auth/token/` - Login (set cookies)
- `POST /api/auth/token/refresh/` - Refresh tokens
- `GET /api/me/` - Current user info
- `GET/POST /api/spot-trades/` - Spot trade CRUD (filtered to user)
- `GET/POST /api/futures-trades/` - Futures trade CRUD (filtered to user)

## Critical Developer Workflows

### Backend Setup & Running
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver  # Runs on http://localhost:8000
```

### Testing Backend
```bash
# All tests must be run from backend/ with venv activated
pytest                    # Run all tests
pytest -v api/tests/      # Run specific test module
pytest --cov=api          # Coverage report
```
**Important:** `conftest.py` auto-generates `FIELD_ENCRYPTION_KEY` for test isolation; encryption must work during testing.

### Database Migrations
```bash
python manage.py makemigrations  # Create migration files
python manage.py migrate         # Apply to db.sqlite3
```

### Frontend Setup & Running
```bash
cd frontend
npm install
npm run dev    # Dev server on http://localhost:5173
npm run build  # Production build
npm run lint   # ESLint strict (max-warnings=0)
npm run e2e    # Playwright tests
```

## Project-Specific Conventions

### Backend Patterns
1. **ViewSets + Serializers**: Use DRF `ModelViewSet` for CRUD; serializers handle validation
   - Example: `SpotTradeViewSet` auto-generates list/create/retrieve/update/delete via `DefaultRouter`
   - Override `get_queryset()` to filter by authenticated user (critical for data isolation)
2. **Encrypted Fields**: Do not store raw secrets; use `CryptoVault` for encryption
   - Fields: `api_key_enc`, `api_secret_enc`, `passphrase_enc` (BinaryField)
   - Decrypt in service layer before passing to exchange adapters
3. **Environment Variables**: All secrets/config from `.env` (loaded by `python-dotenv`)
   - Examples: `SECRET_KEY`, `DEBUG`, `COINBASE_API_KEY`, `FIELD_ENCRYPTION_KEY`
   - Production: `DEBUG=False`, `SECURE_SSL_REDIRECT=True`, explicit `ALLOWED_HOSTS`

### Frontend Patterns
1. **API Client**: `apiFetch()` is the single gateway for all API calls
   - Auto-handles: credentials (cookies), JSON stringification, error parsing, token refresh on 401
   - Usage: `apiFetch("/api/spot-trades/", { method: "POST", body: { ... } })`
2. **Auth Context**: `useAuth()` hook manages user state, login, logout, token refresh
   - Provides: `user`, `logout`, `isLoading`
   - Auto-refreshes tokens on 401 (transparent to components)
3. **Protected Routes**: `<ProtectedRoute>` redirects unauthenticated users to `/login`
   - Usage: `<ProtectedRoute><Dashboard /></ProtectedRoute>`

### Code Comments
- Backend code is heavily commented (docstrings, inline explanations)
  - Follow this pattern for clarity: explain "what" and "why", not just "how"
  - Example: `# ForeignKey ensures user sees only their trades via get_queryset() filter`
- Frontend code is also annotated; maintain this documentation

## Integration Points & External Dependencies

### Coinbase Exchange Adapter
- **Location**: `api/exchanges/coinbase_exchange.py`
- **Authentication**: HMAC-SHA256 signing required
  - Method: Private method `_sign_headers(method, path, query, body)` generates `CB-ACCESS-SIGN` header
  - Signature includes timestamp + method + path + body; different per request
- **Configuration**: Uses env vars `EX_BASE_URL`, `EX_API_KEY_READ`, `EX_API_SECRET_READ`, `EX_API_PASSPHRASE_READ`
  - Sandbox default: `https://api-public.sandbox.exchange.coinbase.com`
  - Production: Set env var to live endpoint
- **Integration**: Fetch trades via Coinbase API, decrypt user credentials, pass to adapter, store in SpotTrade/FuturesTrade

### External Dependencies (Backend)
- **Django REST Framework**: ModelViewSet, Serializers, permissions
- **SimpleJWT**: JWT token generation/validation, refresh logic
- **python-dotenv**: Load `.env` file at startup
- **cryptography.fernet**: Symmetric encryption for secrets
- **requests**: HTTP client for Coinbase API calls

## Common Pitfalls & Solutions

1. **User Data Isolation**: Always filter queryset by `user=request.user` in `get_queryset()`
   - Without it: users can see/modify others' trades
   - Example: `return SpotTrade.objects.filter(user=self.request.user)`

2. **Token Refresh**: Frontend's `apiFetch()` auto-retries 401 with refresh token
   - Backend's `CookieTokenRefreshView` updates cookies; no JSON body needed
   - If refresh fails: cookies cleared, user redirected to login

3. **Encryption Key Missing**: Backend fails to start without `FIELD_ENCRYPTION_KEY`
   - Development: Auto-generated (or set in `.env`)
   - Testing: `conftest.py` auto-generates per test session
   - Production: Must be set in environment, never hardcoded

4. **CORS & Cookies**: Frontend must use `credentials: "include"` (handled by `apiFetch()`)
   - Without it: cookies not sent, authentication fails
   - Backend CORS config in `settings.py` (if using django-cors-headers)

## Testing Strategy
- **Backend**: pytest with pytest-django; fixtures in `conftest.py`
- **Frontend**: Vitest (unit), Playwright (E2E)
- **Coverage**: Aim for high coverage on models, serializers, views
- **Mocking**: Use `responses` library to mock Coinbase API calls

## Debugging Tips
- **Backend logs**: Check console output for full tracebacks
- **Database**: Use `python manage.py dbshell` to inspect sqlite3
- **Frontend network tab**: Check API request/response in browser DevTools
- **Token issues**: Inspect `tt_access` cookie in Application tab (browser DevTools)
