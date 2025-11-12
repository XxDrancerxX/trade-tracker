import React, { createContext, useContext, useEffect, useMemo, useState } from "react"; 
import { apiFetch } from "/apiClient";

// Storage keys (single source of truth)
// the tt. prefix helps avoid collisions with other apps that might use localStorage
const LS_ACCESS = "tt.accessToken"; // the key under which the access token is stored in localStorage
const LS_REFRESH = "tt.refreshToken"; // the key under which the refresh token is stored in localStorage

const AuthContext = createContext(null); // creates a React Context object with a default value of null.

export function AuthProvider({ children }) {
  const [accessToken, setAccessToken] = useState(() => localStorage.getItem(LS_ACCESS) || null);
  const [refreshToken, setRefreshToken] = useState(() => localStorage.getItem(LS_REFRESH) || null);
  const [user, setUser] = useState(null);
  const [isLoading, setLoading] = useState(true); // loading bootstrap/session-restore

  // -- Helpers to persist/clear tokens -----------------------------
  const persistTokens = (access, refresh) => {
    setAccessToken(access);
    setRefreshToken(refresh ?? null);
    if (access) localStorage.setItem(LS_ACCESS, access); else localStorage.removeItem(LS_ACCESS);
    if (refresh) localStorage.setItem(LS_REFRESH, refresh); else localStorage.removeItem(LS_REFRESH);
  };

  const clearSession = () => {
    persistTokens(null, null);
    setUser(null);
  };

  // -- Core API calls ----------------------------------------------
  async function fetchMe(withAccess) {
    const res = await apiFetch("/api/me/", {}, withAccess);
    return res; // apiClient already parsed JSON
  }

  async function refreshAccess(withRefresh) {
    const res = await apiFetch("/api/auth/token/refresh/", {
      method: "POST",
      body: JSON.stringify({ refresh: withRefresh }),
    });
    // res is already JSON { access: "..." }
    return res?.access;
  }

  // -- Public actions ----------------------------------------------
  async function login(username, password) {
    setLoading(true);
    try {
      // 1) get tokens
      const tokens = await apiFetch("/api/auth/token/", {
        method: "POST",
        body: JSON.stringify({ username, password }),
      });
      // tokens: { access, refresh }
      persistTokens(tokens.access, tokens.refresh);

      // 2) fetch user
      const me = await fetchMe(tokens.access);
      setUser(me);
      return { ok: true };
    } catch (err) {
      // wrong credentials, network error, etc.
      clearSession();
      return { ok: false, error: err };
    } finally {
      setLoading(false);
    }
  }

  function logout() {
    clearSession();
  }

  // -- Bootstrap on first mount: restore session if possible -------
  useEffect(() => {
    let cancelled = false;
    async function bootstrap() {
      setLoading(true);
      try {
        if (!accessToken) {
          // no session saved
          return;
        }
        // Try /api/me with current access token
        try {
          const me = await fetchMe(accessToken);
          if (!cancelled) setUser(me);
        } catch (err) {
          // If unauthorized and we have refresh, try to refresh once
          if ((err.status === 401 || err.status === 403) && refreshToken) {
            try {
              const newAccess = await refreshAccess(refreshToken);
              if (newAccess) {
                persistTokens(newAccess, refreshToken);
                const me = await fetchMe(newAccess);
                if (!cancelled) setUser(me);
              } else {
                // refresh failed
                clearSession();
              }
            } catch {
              clearSession();
            }
          } else {
            clearSession();
          }
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    bootstrap();
    return () => { cancelled = true; };
    // Only run on mount; tokens are already in state from localStorage
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const value = useMemo(
    () => ({
      user,
      isLoading,
      login,
      logout,
      // (optional) you can expose tokens if you need to call apiClient elsewhere
      accessToken,
    }),
    [user, isLoading, accessToken]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within <AuthProvider>");
  return ctx;
}
