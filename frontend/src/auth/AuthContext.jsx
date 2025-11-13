// filepath: /workspaces/trade-tracker/frontend/src/auth/AuthContext.jsx
// Auth context using secure HTTP-only cookies set by the backend.
// Frontend no longer reads/writes tokens; it just triggers login/logout
// and asks `/api/me/` who the current user is.

import React, {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { apiFetch } from "../apiClient";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isLoading, setLoading] = useState(true); // tracks bootstrap + login

  // Helper: fetch current user using cookie-based auth
  async function fetchMe() {
    // Cookies are sent automatically by apiFetch via credentials: "include"
    const res = await apiFetch("/api/me/");
    return res;
  }

  // Public: login with username/password.
  // Backend is responsible for setting HTTP-only cookies (access/refresh).
  async function login(username, password) {
    setLoading(true);
    try {
      // 1) Hit login endpoint. Body as plain object; apiFetch JSON-encodes.
      await apiFetch("/api/auth/token/", {
        method: "POST",
        body: { username, password },
      });

      // 2) After cookies set, load user.
      const me = await fetchMe();
      setUser(me);
      return { ok: true };
    } catch (err) {
      // This covers wrong credentials, network errors, etc.
      setUser(null);
      return { ok: false, error: err };
    } finally {
      setLoading(false);
    }
  }

  // Public: logout.
  // Backend should clear cookies on this route (adjust path to your backend).
  async function logout() {
    try {
      await apiFetch("/api/auth/logout/", {
        method: "POST",
      });
    } catch (err) {
      // We still clear local state even if backend fails, to avoid a stuck UI.
    }
    setUser(null);
  }

  // Bootstrap: on first mount, try to restore session from cookies.
  useEffect(() => {
    let cancelled = false;

    async function bootstrap() {
      setLoading(true);
      try {
        try {
          const me = await fetchMe();
          if (!cancelled) setUser(me);
        } catch (err) {
          // 401/403 means "not logged in" or cookie invalid.
          if (!cancelled) setUser(null);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    bootstrap();
    return () => {
      cancelled = true;
    };
  }, []);

  const value = useMemo(
    () => ({
      user,
      isLoading,
      login,
      logout,
    }),
    [user, isLoading],
  );

  return (
    <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within <AuthProvider>");
  return ctx;
}
