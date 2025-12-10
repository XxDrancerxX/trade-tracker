// Auth context using secure HTTP-only cookies set by the backend.
// Frontend no longer reads/writes tokens; it just triggers login/logout
// and asks `/api/me/` who the current user is.

// AuthContext.jsx — central place for auth state & actions
//=====================================================================================================//

// High-level idea
// ---------------
// - We keep *one* global source of truth for authentication: AuthContext.
// - The backend uses HttpOnly cookies for JWTs; frontend never touches tokens.
// - Frontend only:
//     - asks "who am I?" → GET /api/me/
//     - triggers login/logout/register endpoints.
// - Any component can call useAuth() to read:
//     - user       → current logged-in user object (or null)
//     - isLoading  → whether auth is bootstrapping / logging in / logging out
//     - login()    → perform login and load user
//     - logout()   → log out and clear user
//     - register() → sign up and load user
//=====================================================================================================//

// Pieces
// ------
// 1) Context object
//    const AuthContext = createContext(null);
//
//    - React Context is a way to pass data down the tree without prop-drilling.
//    - AuthContext will hold { user, isLoading, login, logout, fetchMe, register }.
//    - We provide that value at the top of the app with <AuthProvider>.
//
// 2) <AuthProvider> component
//    export function AuthProvider({ children }) { … }
//
//    - Wraps the whole app in <AuthContext.Provider>.
//    - Owns the *real* auth state and logic.
//    - children = whatever React elements are inside <AuthProvider> in App.jsx.
//
//    State inside AuthProvider:
//    --------------------------
//    const [user, setUser] = useState(null);
//      - null  → not logged in / unknown
//      - {...} → user object from /api/me/
//
//    const [isLoading, setLoading] = useState(true);
//      - true  → auth is doing something (bootstrap, login, logout, register)
//      - false → idle
//=====================================================================================================//

import React, {
  useEffect,      // Hook to run side effects after render
  useMemo,        // Hook to memoize values, recomputing only when deps change
  useState,       // Hook to manage local component state
  useCallback,    // Hook to memoize functions, preventing recreation unless deps change
} from "react";
import { apiFetch } from "../apiClient";
import { AuthContext } from "./AuthContext";



//=====================================================================================================================================================================================//
export function AuthProvider({ children }) {
  // Children: nested components inside <AuthProvider> in the component tree
  const [user, setUser] = useState(null);        // Current user object or null
  const [isLoading, setLoading] = useState(true); // True during auth operations
  
  //--------------------------------------------------------------------------------------------------------------------------------------------//
  // Helper: fetch current user from /api/me/
  // Cookies are sent automatically by apiFetch via credentials: "include"
  const fetchMe = useCallback(async () => {
    const res = await apiFetch("/api/me/");
    return res;
  }, []); // No dependencies → stable reference
  
  //--------------------------------------------------------------------------------------------------------------------------------------------//
  // Public: login with username/password
  // Backend sets HTTP-only cookies (access/refresh)
  const login = useCallback(async (username, password) => {
    // Flow:
    // 1. Hit login endpoint → backend sets cookies
    // 2. Call fetchMe() → backend reads cookies, returns user
    // 3. Save user in state so whole app sees "logged in"
    // Returns: { ok: true } on success, { ok: false, error } on failure

    setLoading(true);
    try {
      // Step 1: Authenticate and get cookies set
      await apiFetch("/api/auth/token/", {
        method: "POST",
        body: { username, password },
      });

      // Step 2: Fetch user info using the newly-set cookies
      const me = await fetchMe();
      setUser(me);
      return { ok: true };
    } catch (err) {
      // Wrong credentials, network errors, etc.
      setUser(null);
      return { ok: false, error: err };
    } finally {
      setLoading(false);
    }
  }, [fetchMe]); // Depends on fetchMe (stable due to useCallback)
  
  //--------------------------------------------------------------------------------------------------------------------------------------------//
  // Public: register a new user
  const register = useCallback(async (username, password) => {
    // Similar to login, but hits /api/auth/register/
    // Backend creates the user AND sets cookies
    // Returns user directly in response
    
    setLoading(true);
    try {
      const resp = await apiFetch("/api/auth/register/", {
        method: "POST",
        body: { username, password },
      });

      // Backend returns: { user: {...} }
      setUser(resp.user);
      return { ok: true };
    } catch (err) {
      return { ok: false, error: err };
    } finally {
      setLoading(false);
    }
  }, []); // No dependencies → stable reference

  //--------------------------------------------------------------------------------------------------------------------------------------------//
  // Public: logout
  const logout = useCallback(async () => {
    // Calls backend to clear cookies
    // Clears user on frontend so app sees "logged out"
    
    setLoading(true);
    try {
      await apiFetch("/api/auth/logout/", { method: "POST" });
      return { ok: true };
    } catch (err) {
      return { ok: false, error: err };
    } finally {
      setUser(null);  // Always clear user, even if backend call fails
      setLoading(false);
    }
  }, []); // No dependencies → stable reference

  //--------------------------------------------------------------------------------------------------------------------------------------------//
  // Bootstrap: on first mount, try to restore session from cookies
  // - Runs once when <AuthProvider> mounts
  // - Uses any existing cookies to check if the user is already logged in
  // - Sets user + isLoading accordingly
  // - This is why on a hard refresh, the app still knows who we are
  useEffect(() => {
    let cancelled = false; // Flag to prevent state updates if unmounted

    async function bootstrap() {
      // Calls GET /api/me/
      // apiFetch automatically sends cookies (credentials: "include")
      // If cookies are valid, backend returns current user JSON
      
      setLoading(true);
      try {
        const me = await fetchMe();
        if (!cancelled) setUser(me);
      } catch {
        // 401/403 means not logged in or invalid session
        if (!cancelled) setUser(null);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    bootstrap();
    
    return () => {
      // Cleanup: prevent state updates if component unmounts during bootstrap
      cancelled = true;
    };
  }, [fetchMe]); // Runs when fetchMe changes (never, due to useCallback with [])

  // Memoize context value to prevent unnecessary re-renders
  const value = useMemo(
    () => ({
      user,
      isLoading,
      login,
      logout,
      fetchMe,
      register,
    }),
    [user, isLoading, login, logout, fetchMe, register], // Recompute when any of these change
  );

  return (
    <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
  );
  // <AuthContext.Provider> supplies the value to all descendants
  // value={value} contains: { user, isLoading, login, logout, fetchMe, register }
  // {children} renders whatever was nested inside <AuthProvider>
  // When any dependency changes, value's object reference changes and consumers re-render
}


//=====================================================================================================================//
// Summary / mental model
// ----------------------
// AuthProvider = the "auth brain" of the app
//   - Knows how to log in, register, log out, and restore sessions
//   - Owns `user` + `isLoading` state
//
// useAuth() = the "auth API" for the rest of the app
//   - Components call useAuth() to read auth state and trigger actions
//
// Backend handles all JWT + cookie details; frontend only:
//   - POST /api/auth/token/       (login)
//   - POST /api/auth/register/    (signup)
//   - POST /api/auth/logout/      (logout)
//   - GET  /api/me/               (who am I?)
//
// Because cookies are HttpOnly and handled by the browser, the React side
// never stores or reads raw tokens → safer and simpler
//
// This design gives:
//   - Single source of truth for auth
//   - Shared state across the whole app (navbar, protected routes, pages)
//   - Clean separation between "auth logic" (here) and UI (pages/components)