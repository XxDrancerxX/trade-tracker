// filepath: /workspaces/trade-tracker/frontend/src/App.jsx
import React, { useState } from "react";
import { useAuth } from "./auth/AuthContext";

function AuthDebugPanel() {
  const { user, isLoading, login, logout } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [errorMsg, setErrorMsg] = useState("");

  async function handleLogin(e) {
    e.preventDefault();
    setErrorMsg("");
    const res = await login(username, password);
    if (!res.ok) {
      // keep message simple for now; you can inspect res.error later
      setErrorMsg("Login failed. Check credentials or network.");
    }
  }

  async function handleLogout() {
    setErrorMsg("");
    await logout();
  }

  return (
    <div style={{ maxWidth: 400, margin: "2rem auto", padding: "1rem", border: "1px solid #ddd", borderRadius: 8 }}>
      <h2>Auth Debug Panel</h2>
      <p>
        <strong>Status:</strong>{" "}
        {isLoading ? "Loading..." : user ? "Logged in" : "Logged out"}
      </p>
      {user && (
        <p>
          <strong>User:</strong> {user.username} ({user.email})
        </p>
      )}

      {!user && (
        <form onSubmit={handleLogin} style={{ marginTop: "1rem" }}>
          <div style={{ marginBottom: "0.5rem" }}>
            <label>
              Username:
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                autoComplete="username"
              />
            </label>
          </div>
          <div style={{ marginBottom: "0.5rem" }}>
            <label>
              Password:
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
              />
            </label>
          </div>
          <button type="submit" disabled={isLoading}>
            {isLoading ? "Logging in..." : "Login"}
          </button>
        </form>
      )}

      {user && (
        <button
          type="button"
          onClick={handleLogout}
          disabled={isLoading}
          style={{ marginTop: "1rem" }}
        >
          {isLoading ? "Working..." : "Logout"}
        </button>
      )}

      {errorMsg && (
        <p style={{ color: "red", marginTop: "0.5rem" }}>{errorMsg}</p>
      )}
    </div>
  );
}

export default function App() {
  return (
    <div>
      <h1 style={{ textAlign: "center" }}>Vite + React (Auth Test)</h1>
      <AuthDebugPanel />
    </div>
  );
}
