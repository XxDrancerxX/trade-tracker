// src/pages/LoginPage.jsx
import React, { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../auth/useAuth"; // ✅ Fixed import path

function LoginPage() {
  const { user, isLoading, login } = useAuth();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const navigate = useNavigate();
  const location = useLocation();

  // If already logged in, redirect away from /login
  useEffect(() => {
    if (!isLoading && user) {
      const from = location.state?.from?.pathname || "/";
      navigate(from, { replace: true });
    }
  }, [user, isLoading, navigate, location]);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    // 🔎 basic validation
    if (!username.trim() || !password.trim()) {
      setError("Please fill in both fields.");
      return;
    }

    setIsSubmitting(true);

    // login returns { ok, error } - it doesn't throw
    const result = await login(username, password);

    if (!result.ok) {
      // Login failed - show error
      console.error("Login failed:", result.error);
      setError(result.error?.message || "Invalid username or password.");
    }
    // On success, redirect happens in useEffect when `user` becomes non-null

    setIsSubmitting(false);
  }

  return (
    <div style={{ maxWidth: 400, margin: "2rem auto" }}>
      <h1>Login</h1>

      {error && (
        <>
          <p style={{ color: "red", marginBottom: "0.5rem" }}>
            {error}
          </p>
          <p style={{ color: "red", marginBottom: "0.5rem" }}>
            Username and Password incorrect. Please try again.
          </p>
        </>
      )}

      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: "0.5rem" }}>
          <label>
            Username
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              style={{ width: "100%", padding: "0.25rem" }}
            />
          </label>
        </div>

        <div style={{ marginBottom: "0.5rem" }}>
          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              style={{ width: "100%", padding: "0.25rem" }}
            />
          </label>
        </div>

        <button
          type="submit"
          disabled={isSubmitting || isLoading}
          style={{ marginTop: "0.5rem", width: "100%" }}
        >
          {isSubmitting || isLoading ? "Logging in..." : "Login"}
        </button>
      </form>
    </div>
  );
}

export default LoginPage;
