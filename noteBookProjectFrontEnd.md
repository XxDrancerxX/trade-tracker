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
