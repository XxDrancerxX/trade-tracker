# FE-001 — Frontend: Bootstrap (Vite + React)

Goal
- Create a minimal Vite + React frontend, wire dev env, and point it at the Django backend (VITE_API_URL).
- Keep local envs out of git and verify the app can contact the backend.

Commands run
```bash
# scaffold and install
npm create vite@latest frontend -- --template react
cd frontend
npm install
npm i react-router-dom

# create local env files
printf "VITE_API_URL=http://127.0.0.1:8000\n" > .env.local
printf "VITE_API_URL=\n" > .env.example

# ignore local env
echo "/frontend/.env.local" >> ../.gitignore

# run dev server (bind to all interfaces if needed)
npm run dev -- --host
```

Quick verification
- In `frontend/src/App.jsx` add and check:
```js
const API_URL = import.meta.env.VITE_API_URL;
console.log("API_URL from env:", API_URL);
```
- Forward ports in VS Code (5173 for Vite, 8000 for Django) and open the forwarded URLs in the host browser ($BROWSER <url>).

Git workflow (linked to issue branch)
```bash
# create/commit files on the issue branch (Codespaces "Work on Issue" or manual)
git add frontend .gitignore
git commit -m "FE-001: bootstrap Vite app, envs. Fixes #7"
git push --set-upstream origin XxDrancerxX/issue7
```

Acceptance checklist
- [ ] Vite app runs and is visible in browser (forwarded URL)
- [ ] `.env.local` created locally and `.env.example` committed
- [ ] `/frontend/.env.local` added to `.gitignore`
- [ ] `VITE_API_URL` is read by the app (console or on-screen)
- [ ] Initial commit pushed to the issue branch and linked to the GitHub issue

Notes
- Use the forwarded backend URL (codespace public URL) in `.env.local` when calling the running Django server from browser.
- This is a minimal setup. Move `VITE_API_URL` into a shared config file when adding real auth and API client.
//=============================================================================================================================//
Commands run
```bash
npm create vite@latest frontend -- --template react
```
-Downloads the Vite starter.
-Creates a folder: frontend/

Sets up:

-package.json → which dependencies & scripts exist.
-vite.config.js → how to build/serve the app.
-src/main.jsx → entry point that mounts React.
-src/App.jsx → sample React component (Vite + React page).

Mental model: this is our frontend app skeleton.

```bash
npm i react-router-dom
```
(we added for future routing)
-Adds routing library so later we can have /login, /dashboard, etc.
-Just installed now; we’ll use it in the next steps.

* .env.local and .env.example *
We  made two env files inside frontend/:

```bash
# .env.local (not committed)
VITE_API_URL=http://127.0.0.1:8000   # later replaced with Codespaces URL

# .env.example (committed)
VITE_API_URL=
```
- VITE_ prefix = Vite exposes it to the browser.
- .env.local = your actual local config.
- .env.example = documentation of what vars are needed.
- We then added /frontend/.env.local to root .gitignore to avoid committing local config.
Reason: same codebase, different URLs per environment, no secrets in git.

```bash
const API_URL = import.meta.env.VITE_API_URL;
```
-This is how your React app reads that env variable.
- import.meta.env is a special Vite object.
- At build time, Vite swaps import.meta.env.VITE_API_URL with the actual string from .env.*.

📦 trade-tracker/
│
├── backend/             → Django REST API (business logic, DB)
│   ├── manage.py
│   └── api/
│
├── frontend/            → Vite + React app (user interface)
│   ├── src/             → React components, pages, etc.
│   ├── public/          → static files (favicon, etc.)
│   ├── .env.local       → backend API URL for development
│   └── vite.config.js   → Vite’s config (ports, proxy, etc.)
│
├── .gitignore
└── README.md

# 🧠 Fe 002 — CORS + Backend Auth Endpoints Verified

## 🎯 Goal
Enable secure communication between the React (Vite) frontend and Django backend using JWT authentication and proper CORS configuration.

---

## ⚙️ Step-by-step summary

### 1) Configured JWT authentication
- Installed and enabled djangorestframework-simplejwt.
- Added auth endpoints:
  - `POST /api/auth/token/` → obtain `{ "access", "refresh" }`
  - `POST /api/auth/token/refresh/` → renew access token
  - `GET /api/me/` → return authenticated user data

- REST framework settings (in `settings.py`):
```py
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}
```

---

### 2) Set up CORS & CSRF for development
- Installed `django-cors-headers` and added to settings:
```py
INSTALLED_APPS = [
    "corsheaders",
    ...
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    ...
]
```

- .env configuration (example):
```env
FRONTEND_URLS=https://<vite-url>,http://localhost:5173
```

- Loaded dynamically in `settings.py`:
```py
CORS_ALLOWED_ORIGINS = FRONTEND_URLS
CSRF_TRUSTED_ORIGINS = FRONTEND_URLS + ["https://*.app.github.dev"]
CORS_ALLOW_CREDENTIALS = True
```

Note: origins must be scheme + host (no path or trailing slash). Example valid origin:
`https://supreme-space-orbit-...-5173.app.github.dev`

---

### 3) Verified endpoints with curl

- Token request:
```bash
curl -X POST "<backend-url>/api/auth/token/" \
  -H "Content-Type: application/json" \
  -d '{"username":"superuser","password":"123456"}'
# → returns {"access":"...","refresh":"..."}
```

- Protected route:
```bash
curl -H "Authorization: Bearer <ACCESS_TOKEN>" \
  "<backend-url>/api/me/"
# → returns authenticated user JSON
```

---

### 4) Frontend integration test
- Added `frontend/.env.local`:
```env
VITE_API_URL=https://<backend-url>
```

- Quick browser test from console:
```js
const API_URL = "https://<backend-url>";

fetch(`${API_URL}/api/auth/token/`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ username: "superuser", password: "123456" }),
})
  .then(r => r.json())
  .then(console.log);
```
Result: no CORS/preflight errors and valid token response.

---

## 🧩 What this enables
- Secure JWT-based login and session handling.
- Frontend can safely call protected Django APIs.
- Proper cross-origin setup for Codespaces and localhost development.
- Foundation for adding an AuthProvider and protected routes in React.

---

## ✅ Acceptance criteria
- [x] `/api/auth/token/` reachable  
- [x] `/api/auth/token/refresh/` reachable  
- [x] `/api/me/` returns user with valid token  
- [x] CORS & CSRF configured for Vite dev URL  
- [x] No CORS / preflight errors in browser  
- [x] Docs updated (`.env.example`, README)

---

## 💡 Key concept
JWT tokens are compact, signed JSON objects the backend issues and validates on each request. CORS is a browser-enforced policy that must be configured on the backend to allow your frontend origin(s) to call the API safely.

---




# FE-003 — AuthProvider (Cookie-based)

Goal
- Build a frontend AuthProvider that:
  - Logs in via /api/auth/token/
  - Knows current user via /api/me/
  - Restores session on page refresh
  - Logs out via /api/auth/logout/
  - Centralizes auth state & API calls
- Security variant: JWT access + refresh live in HttpOnly cookies (not localStorage). React only sees { user, isLoading }.

## Backend pieces

1) Cookie helpers (auth_cookies.py)
- set_access_cookie(resp, access) → sets tt_access
- set_refresh_cookie(resp, refresh) → sets tt_refresh
- Flags: HttpOnly, Secure, SameSite=None, Path=/
  - Not readable by JS
  - Sent on cross-origin with credentials: "include"

2) Cookie-based JWT auth (authentication.py)
- CookieJWTAuthentication(JWTAuthentication):
  - Reads tt_access from request.COOKIES
  - If valid → sets request.user
  - If missing/invalid → None or AuthenticationFailed
- Registered in REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"]

3) Auth views (core/urls.py)
- POST /api/auth/token/ (CookieTokenObtainPairView)
  - Validates credentials, issues tokens
  - set_access_cookie + set_refresh_cookie
  - Returns { ok: true }
- POST /api/auth/token/refresh/ (CookieTokenRefreshView)
  - Reads refresh from body or tt_refresh cookie
  - Issues new tt_access (and possibly tt_refresh)
- POST /api/auth/logout/ (logout_view)
  - Clears tt_access + tt_refresh
  - Returns { ok: true }
- GET /api/me/
  - @IsAuthenticated, returns { id, username, email }
  - Auth via CookieJWTAuthentication

## Frontend pieces

1) config.js
- export const API_URL = import.meta.env.VITE_API_URL
- .env.local example: VITE_API_URL="https://...-8000.app.github.dev"

2) apiClient.js
- apiFetch(path, options = {})
  - URL: ${API_URL}${path}
  - credentials: "include" (send/receive cookies)
  - Auto-JSON for plain objects (Content-Type set as needed)
  - Parses JSON responses
  - Throws structured Error on non-2xx: err.status, err.body
- No token args; auth via cookies only

3) AuthContext.jsx
- State:
  - user (object | null)
  - isLoading (boolean)
- Functions:
  - fetchMe() → GET /api/me/
  - login(username, password)
    - POST /api/auth/token/ with { username, password }
    - Backend sets tt_access + tt_refresh
    - Calls fetchMe(), sets user
    - Returns { ok: true } or { ok: false, error }
  - logout()
    - POST /api/auth/logout/
    - Clears user
- Bootstrap (useEffect)
  - On mount → fetchMe()
    - 200 → set user
    - 401/403 → user = null
  - isLoading toggled around calls
- useAuth()
  - Exposes { user, isLoading, login, logout }

4) main.jsx
- Wrap app:
  - <AuthProvider><App /></AuthProvider>

5) Dev Auth Debug UI (App.jsx)
- Shows status (Logged in / Logged out / Loading…)
- Displays user info
- Login form + Logout button
- Confirms cookies + /api/me/ work end-to-end

## End-to-end workflow

1) App load (refresh)
- <AuthProvider> mounts → apiFetch("/api/me/") with credentials
- Browser sends tt_access (if present)
- Backend authenticates via cookie → returns user
- Frontend sets user; else 401 → user = null

2) Login
- login → POST /api/auth/token/ with credentials
- Backend sets tt_access + tt_refresh cookies
- fetchMe → sets user

3) Authenticated API calls (later)
- Any apiFetch("/api/spot-trades/") includes cookies automatically

4) Logout
- POST /api/auth/logout/ → backend clears cookies
- Frontend sets user = null

5) (Later) Refresh
- /api/auth/token/refresh/ reads tt_refresh cookie
- Issues new tt_access (and possibly tt_refresh)
- Client can call on 401 then retry

## Why this design

- Security: No tokens in JS/localStorage; HttpOnly + Secure + SameSite=None cookies
- Simplicity: Frontend only cares about user + 3 endpoints
- Extensible: New routes use useAuth() + apiFetch() without token handling

## Quick verification checklist

- [ ] Login response includes Set-Cookie for tt_access/tt_refresh
- [ ] apiFetch sends credentials: "include"
- [ ] /api/me/ returns 200 with cookies (no Authorization header)
- [ ] Logout clears cookies and /api/me/ returns 401


1️⃣ CLEAN ASCII DIAGRAM (Workflow)

          ┌─────────────────────────────┐
          │         React App           │
          │     (AuthContext.jsx)      │
          └──────────────┬──────────────┘
                         │
                         │ 1) User clicks "Login"
                         ▼
              ┌──────────────────────────┐
              │  POST /api/auth/token/   │
              │  body:{username,password}│
              └──────────────┬───────────┘
                             │
                             │ Backend validates login
                             ▼
        ┌──────────────────────────────────────────────────┐
        │                   Django Backend                  │
        │      CookieTokenObtainPairView (SimpleJWT)       │
        ├──────────────────────────────────────────────────┤
        │ Generates:                                        │
        │   access_token  → short-lived                     │
        │   refresh_token → long-lived                      │
        └──────────────┬────────────────────────────────────┘
                       │
                       │ Sets cookies in response:
                       │   Set-Cookie: tt_access=...  (HttpOnly)
                       │   Set-Cookie: tt_refresh=... (HttpOnly)
                       ▼
        ┌──────────────────────────────────────────────────┐
        │ Browser stores cookies securely:                 │
        │   - cannot be read by JS                         │
        │   - automatically attached on every request      │
        └──────────────┬────────────────────────────────────┘
                       │
                       │ 2) React calls /api/me/ to load user
                       ▼
           ┌──────────────────────────────────────┐
           │ GET /api/me/                         │
           │ cookies: tt_access sent automatically │
           └──────────────┬───────────────────────┘
                          │
                          ▼
         ┌──────────────────────────────────────────────────┐
         │ Django authenticates via CookieJWTAuthentication │
         │  - reads tt_access                               │
         │  - validates JWT                                 │
         │  - attaches request.user                         │
         └──────────────┬────────────────────────────────────┘
                        │
                        ▼
         ┌──────────────────────────────────────────────┐
         │ React receives user JSON: {id, username, ...} │
         │ AuthProvider sets user in state               │
         └──────────────────────────────────────────────┘


─────────────────────────────────────────────────────────────
                   SESSION RESTORE (page refresh)
─────────────────────────────────────────────────────────────

`AuthProvider` mounts → calls `/api/me/` again  
Cookies auto-sent → backend validates → React gets user again  


─────────────────────────────────────────────────────────────
                           LOGOUT
─────────────────────────────────────────────────────────────
React → POST /api/auth/logout/  
Backend → clears tt_access + tt_refresh cookies  
React → sets user = null  

─────────────────────────────────────────────────────────────
# FE-004 — Login Page Workflow (Notes)

## 🧩 Summary
This feature adds a dedicated `/login` page that includes:
- Form inputs for username and password
- Frontend validation with inline error messages
- Redirect on success and guard against logged-in users visiting `/login`
- Loading states tied to `AuthProvider.isLoading`
- Integration with the existing cookie-backed `AuthProvider`
- Cookie-based authentication, so no tokens are exposed to JavaScript

## 🏗 Frontend Pieces

### `AuthProvider.jsx`
- Holds `user`, `isLoading`, `login()`, `logout()`, `fetchMe()`
- **On login**
  - Calls `POST /api/auth/token/`
  - Backend sets `tt_access`, `tt_refresh` cookies
  - Calls `fetchMe()` → updates `user`
- **On logout**
  - Calls `POST /api/auth/logout/`
  - Backend clears cookies
  - Sets `user = null`

### `apiClient.js`
- Wrapper for `fetch`
- Prefixes `API_URL`
- Sends `credentials: "include"` so HttpOnly cookies flow automatically
- Auto-JSON encodes bodies, parses JSON responses
- Throws structured `{ status, body }` errors

### `LoginPage.jsx`
- Renders username/password inputs
- Displays validation and backend errors
- On submit:
  - Calls `login(username, password)`
  - Redirects on success
  - Shows error message below the form on failure

## 🔄 End-to-End Workflow
1. **App load / page refresh**
   - `<AuthProvider>` mounts → `apiFetch("/api/me/")` with credentials
   - Browser automatically sends cookies (if present)
   - Backend validates `tt_access` → returns user
   - Frontend sets `user`; on 401 → `user = null`

2. **Login**
   - `LoginPage` calls `login(username, password)`
   - `login()` steps:
     - `POST /api/auth/token/` → backend sets `tt_access` + `tt_refresh`
     - `fetchMe()` → `GET /api/me/`
     - Backend authenticates via `CookieJWTAuthentication`
     - Returns `{ id, username, ... }`
     - `setUser(me)`; `navigate("/")`

3. **Authenticated API calls (future)**
   - Any `apiFetch("/api/spot-trades/")` includes cookies automatically
   - Backend authenticates without an `Authorization` header

4. **Logout**
   - `POST /api/auth/logout/`
   - Backend clears cookies (empty `Set-Cookie`)
   - `AuthProvider.setUser(null)`; `navigate("/login")`

5. **Later (refresh token flow)**
   - Not implemented yet — planned for FE-010

## 🧠 Under-the-Hood (Cookies Edition)
- Cookies are HttpOnly: JavaScript cannot read them
- Cookies ride on every request because of `credentials: "include"`
- Django reads them via `CookieJWTAuthentication`
- No token ever touches React code → strong security posture

## 🖼 ASCII Diagram — Cookie Login Flow
                        ┌────────────────────┐
                        │     Login Page      │
                        └─────────┬───────────┘
                                  │
                                  │ 1. User enters username/password
                                  ▼
                       ┌──────────────────────────┐
                       │ AuthContext.login()      │
                       └─────────┬────────────────┘
                                  │
                                  │ 2. POST /api/auth/token/
                                  ▼
                 ┌──────────────────────────────────────┐
                 │ Django SimpleJWT Token View           │
                 │ - Validates credentials               │
                 │ - Sets cookies: tt_access, tt_refresh │
                 └───────────┬───────────────────────────┘
                             │  (cookies stored in browser)
                             ▼
             ┌─────────────────────────────────────┐
             │ AuthContext.fetchMe()               │
             └───────────┬─────────────────────────┘
                         │
                         │ 3. GET /api/me/ (with cookies)
                         ▼
       ┌───────────────────────────────────────────────────┐
       │ Django CookieJWTAuthentication                    │
       │ - Reads tt_access                                 │
       │ - Validates JWT                                   │
       │ - Sets request.user                               │
       │ - Returns { id, username, email }                 │
       └───────────┬───────────────────────────────────────┘
                   │
                   ▼
      ┌─────────────────────────────────────────────┐
      │ React AuthContext.setUser(me)               │
      │ - user state now contains logged-in user    │
      └────────┬────────────────────────────────────┘
               │
               │ 4. LoginPage detects `user` ≠ null
               ▼
    ┌───────────────────────────────────────────────┐
    │ navigate("/")                                  │
    │ User is redirected to HomePage                 │
    └────────────────────────────────────────────────┘

───────────────────────────────────────────────────────────────────
                    SESSION RESTORE ON REFRESH
───────────────────────────────────────────────────────────────────

Browser refreshes →
AuthProvider.mount →

fetchMe() runs again →
cookies auto-sent →
/api/me/ returns user → setUser(me) →
User stays logged in

───────────────────────────────────────────────────────────────────
                    LOGOUT
───────────────────────────────────────────────────────────────────

Logout button → AuthContext.logout() →

POST /api/auth/logout/ →
Django clears cookies →
AuthProvider.setUser(null) →
User state resets →
Redirect to /login


# FE-005 / BE-005 — Signup System (Registration Flow)

## 🧩 Summary
Full-stack feature enabling secure user registration with cookie-based JWT authentication.

**Tech stack:**
- Backend: Django + DRF + SimpleJWT
- Frontend: React (Vite) + AuthContext
- Auth: JWT in HttpOnly cookies (`tt_access` + `tt_refresh`)

**User flow:**
1. Submit username + password
2. Backend creates user
3. Backend sets secure cookies
4. Frontend becomes "logged in"
5. Redirect to `/`

Signup behaves like login but includes account creation.

---

## 🏗 Backend Implementation

### 1. `RegisterSerializer`
**File:** `backend/api/serializers.py`

**Purpose:**
- Validate username/password
- Block duplicates
- Create Django `User` with hashed password

```python
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password")

    def validate_email(self, value):
        if value and User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already in use")
        return value

    def create(self, validated):
        return User.objects.create_user(
            username=validated["username"],
            email=validated.get("email", ""),
            password=validated["password"],
        )
  ``` 
✔ Password is hashed
✔ Creates new user
✔ Email optional for MVP       

---

### 2. `register_view`
**File:** `backend/core/urls.py` (imported from auth views module)

**Responsibilities:**
- Accept POST requests
- Validate + create user
- Generate `access` + `refresh` JWT
- Set HttpOnly cookies
- Return new user JSON

```python
@api_view(["POST"])
@permission_classes([AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()

    refresh = RefreshToken.for_user(user)

    out = Response(
        {"ok": True, "user": serializer.data},
        status=status.HTTP_201_CREATED
    )
    set_access_cookie(out, str(refresh.access_token))
    set_refresh_cookie(out, str(refresh))
    return out
  ```  

✔ Security Notes:
-Cookies are HttpOnly, Secure, SameSite=None, Path=/
-Token is never exposed to React
-Browser stores cookies automatically
-Any request to /api/... automatically includes credentials  

## 3. URL Registration
```python
path("api/auth/register/", register_view, name="register")
```
## 4. Backend Tests (pytest)
**Tests verify:**

-201 Created
-User is created
-Cookies are set
-Duplicate usernames return 400
-Backend is fully validated.

## 🏗 Frontend Implementation
**Located in:**
-frontend/src/auth/AuthContext.jsx
-frontend/src/pages/SignupPage.jsx
- Uses react-router-dom for navigation

## 1. AuthContext: new register() method

```javascript
async function register(username, password) {
  setLoading(true);
  try {
    const resp = await apiFetch("/api/auth/register/", {
      method: "POST",
      body: { username, password },
    });
    setUser(resp.user);
    return { ok: true };
  } catch (err) {
    return { ok: false, error: err };
  } finally {
    setLoading(false);
  }
}
```
**🔑 Key ideas**
- `apiFetch` sends `credentials: "include"` → cookies saved by browser
- On success → call `setUser(resp.user)`
- React instantly becomes "logged in"
- No tokens stored in `localStorage`
- No tokens exposed to JS → secure by design

---

## 2. `SignupPage.jsx`

**Core responsibilities:**
- Render form
- Validate fields
- Call `register()`
- Show backend validation errors
- Redirect on success

**Error normalization function**  
We map DRF error formats into a single human‑readable string:

```javascript
function normalizeError(err) {
  const body = err?.body || {};
  if (body.username) return `Username: ${body.username[0]}`;
  if (body.password) return `Password: ${body.password[0]}`;
  if (body.non_field_errors) return body.non_field_errors[0];
  return "Signup failed.";
}
```


**Submission flow:**  
```javascript
const { ok, error: err } = await register(username.trim(), password);

if (!ok) {
  setError(normalizeError(err));
  return;
}

navigate("/", { replace: true });
```
✔ Creates account
✔ AuthContext loads user
✔ Redirects to /

## End-to-End Workflow Diagram:
┌────────────────────────────┐
│       React SignupPage      │
└──────────────┬─────────────┘
               │
     1. User submits form
               │
               ▼
┌───────────────────────────────────────┐
│ AuthContext.register(username, pass)  │
└──────────────┬────────────────────────┘
               │
     2. apiFetch("/api/auth/register/")
               │
               ▼
      Browser sends POST request
      (credentials: "include")
               │
               ▼
┌─────────────────────────────────────────┐
│        Django register_view             │
├─────────────────────────────────────────┤
│ Validate → Create User → Issue Tokens   │
│ Set-Cookie: tt_access                   │
│ Set-Cookie: tt_refresh                  │
└──────────────┬──────────────────────────┘
               │
       3. Response JSON:
       { ok: true, user: {...} }
               │
               ▼
┌───────────────────────────────────────┐
│ AuthContext receives resp.user        │
│ setUser(resp.user)                    │
└──────────────┬────────────────────────┘
               │
        4. App is now authenticated
               │
               ▼
     React redirects → Home (/)


## 🔗 How Both Ends Integrate

**🔄 Backend responsibilities**
- Validate user data  
- Hash password  
- Create user  
- Issue JWT tokens  
- Store tokens in HttpOnly cookies  
- Return new user data

**🔄 Frontend responsibilities**
- Provide signup UI (username, password)  
- Validate fields early  
- Send signup request to backend  
- Store user object in context  
- Redirect on success  
- Display backend validation errors  

**🔐 Security benefits**
- No token ever touches React  
- Cookies are HttpOnly → immune to XSS  
- Cookies use `Secure` + `SameSite=None` → safe for cross‑origin dev  
- `AuthContext` remains the single source of truth  

---

## ✅ Final Result

The signup system is now:
- Secure (token‑less frontend, HttpOnly cookies)  
- Fully integrated (backend + frontend)  
- Production‑ready  
- Tested (backend pytest)  
- Extensible (easy to add email, password reset, etc.)

Signup is the foundation for:
- Protected routes  
- User onboarding  
- Dashboard personalization  
- Exchange connection UI  

**✔ Feature FE‑005 / BE‑005: DONE**


# FE-006 — ProtectedRoute (Auth-only pages)

## Purpose

Some routes (like `/`) should only be visible to authenticated users.  
`ProtectedRoute` is a small wrapper that:

- Waits for auth bootstrap (`isLoading`)
- Redirects unauthenticated users to `/login`
- Renders the protected content only when `user` is present

## Component

```jsx
// src/auth/ProtectedRoute.jsx
import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "./AuthContext.jsx";

export function ProtectedRoute({ children }) {
  const { user, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!user) {
    return (
      <Navigate
        to="/login"
        replace
        state={{ from: location }}
      />
    );
  }

  return children;
}
```

## Behavior checklist:

-Logged-out user visiting / → redirected to /login
-Logged-in user visiting / → sees HomePage
-Refresh on / → stays on / (session restored via cookies + AuthProvider)
-Logout + Back button → cannot see protected content again