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

# 🧠 Issue 002 — CORS + Backend Auth Endpoints Verified

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