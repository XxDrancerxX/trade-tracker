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
//     - asks “who am I?” → GET /api/me/
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
  //Each is a named export from the react package; they are functions (hooks or API helpers) used inside function components.
  createContext, // Creates a Context object ({ Provider, Consumer }). Provider’s value prop supplies data to any descendant calling useContext.
  useContext, // Hook to read the current context value for a Context object created by createContext. It reads the current value from the nearest matching Provider.
  useEffect, // Hook to run side effects (data fetching, subscriptions) after render. Accepts a function and dependency array.
  useMemo, // Hook to memoize a value, recomputing it only when dependencies change.
  useState, // Hook to manage local component state.
} from "react";
import { apiFetch } from "../apiClient";  // import the apiFetch helper to make HTTP requests to the backend API.

const AuthContext = createContext(null); //this returns a Context object with 2 properties: Provider and Consumer. We only use Provider here.
//AuthContext.Provider: a component that supplies a value to descendants.
// The “current value” slot (managed by React) that consumers read via useContext(AuthContext).


//=====================================================================================================================================================================================//
export function AuthProvider({ children }) { // Children are the nested components inside <AuthProvider> in the component tree.It's a special React prop hat allows components to wrap other components.
  const [user, setUser] = useState(null); // tracks current user; null = not logged in
  const [isLoading, setLoading] = useState(true); // tracks bootstrap + login
  
  //--------------------------------------------------------------------------------------------------------------------------------------------//
  // Helper: fetch current user using cookie-based auth
  async function fetchMe() {
    // Cookies are sent automatically by apiFetch via credentials: "include"
    const res = await apiFetch("/api/me/");
    return res;
  }
  
  //--------------------------------------------------------------------------------------------------------------------------------------------//
  // Public: login with username/password.
  // Backend is responsible for setting HTTP-only cookies (access/refresh).
  async function login(username, password) {
    // 1. Hit login endpoint → backend sets cookies.
    // 2. Call fetchMe() → backend reads cookies, returns user.
    // 3. Save user in state so whole app sees “logged in”.
    // -Return shape: { ok: true } on success, { ok: false, error } on failure.
    // -Callers use this to show messages.

    setLoading(true); // start loading state, marks the UI as busy.
    try { // Try to log in
      // 1) Hit login endpoint. Body as plain object; apiFetch JSON-encodes.
      await apiFetch("/api/auth/token/", { //apiFetch auto-JSONs the body and sends credentials: "include" to get cookies set.
        method: "POST",
        body: { username, password },
      });

      // 2) After cookies set, load user.
      const me = await fetchMe(); // Fetch current user info using the cookie-based session.
      setUser(me); // Update user state with fetched user info.
      return { ok: true }; // Indicate successful login.
    } catch (err) { // Catch any errors
      // This covers wrong credentials, network errors, etc.
      setUser(null); // Clear user state on failure.
      return { ok: false, error: err }; // Return error details to caller.
    } finally { // Always executed after try/catch
      setLoading(false);
    }
  }
  //--------------------------------------------------------------------------------------------------------------------------------------------//
    // Public: register a new user.
    async function register(username, password) {
    // - Very similar to login, but hits /api/auth/register/.
    // - Backend both creates the user and sets cookies.
    // - We just store resp.user as the current user.
    setLoading(true);
    try {
      const resp = await apiFetch("/api/auth/register/", {
        method: "POST",
        body: { username, password },
      });

      // Backend returns: { ok: true, user: {...} }
      setUser(resp.user);
      return { ok: true };
    } catch (err) {
      return { ok: false, error: err };
    } finally {
      setLoading(false);
    }
  }


  //--------------------------------------------------------------------------------------------------------------------------------------------//
  // Public: logout.
  // Backend should clear cookies on this route (adjust path to your backend).
  async function logout() {
    // -Calls backend to clear cookies.
    // -Clears user on the frontend so app sees “logged out”.
    setLoading(true);
    try {
      await apiFetch("/api/auth/logout/", { method: "POST" });
      return { ok: true };
    } catch (err) {
      return { ok: false, error: err };
    } finally {
      setUser(null);
      setLoading(false);
    }
  }

  //--------------------------------------------------------------------------------------------------------------------------------------------//
  // Bootstrap: on first mount, try to restore session from cookies.
  useEffect(() => { // runs once on mount due to empty dependency array.because deps = [] at end, it runs once after first render.
    let cancelled = false; // flag to prevent state updates if unmounted

    async function bootstrap() { // async function to initialize auth state
      // - Calls GET /api/me/.
      // - apiFetch automatically sends cookies (credentials: "include").
      // - If cookies are valid, backend returns current user JSON.
      // - Used by login() and the bootstrap effect.

      setLoading(true); // start loading state before fetching user
      try {
        try {
          const me = await fetchMe(); // attempt to fetch current user
          if (!cancelled) setUser(me); // if still mounted, set user state
        } catch (err) {
          // 401/403 means "not logged in" or cookie invalid.
          if (!cancelled) setUser(null);
        }
      } finally {
        if (!cancelled) setLoading(false); // // ensure loading state is cleared if still mounted.
      }
    }

    bootstrap(); // call the async bootstrap function
    return () => { // Cleanup function runs on unmount.
      cancelled = true; // set flag to prevent state updates after unmount.// Marks effect as cancelled so pending awaits won’t update state.
        // - Runs once when <AuthProvider> mounts.
        // - Uses any existing cookies to check if the user is already logged in.
        // - Sets user + isLoading accordingly.
        // - This is why on a hard refresh, the app still knows who we are.
    };
  }, []);  // Dependency array empty → effect runs only once (mount), then cleanup on unmount.

  const value = useMemo( // Memoize context value to avoid unnecessary re-renders.
    () => ({
      user,
      isLoading,
      login,
      logout,
      fetchMe,
      register,
    }),
    [user, isLoading], // Recompute value only when user or isLoading changes.
       // - We construct a single object containing everything consumers need.
       // - useMemo ensures we only create a **new** object when `user` or
       // - `isLoading` actually change, avoiding extra re-renders.
  );

  return (
    <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
  );
    // <AuthContext.Provider …> is the React Context Provider created by createContext.
// value={value} supplies one object: { user, isLoading, login, logout }. Any child component calling useAuth() receives this exact object.
// {children} renders whatever was nested inside <AuthProvider> in the component tree.
// When user or isLoading change, value’s object reference changes (because of useMemo dependencies) and consumers re-render with updated auth state.

}

export function useAuth() {
  const ctx = useContext(AuthContext); // Read the current AuthContext value using useContext hook.
  if (!ctx) throw new Error("useAuth must be used within <AuthProvider>"); // Ensure hook is used within AuthProvider; otherwise, throw an error.
  return ctx;
}


// AuthContext centralizes everything about the signed-in user so the rest of the app doesn’t juggle tokens or duplicate state. It uses an underlying React context:

// AuthProvider keeps two pieces of state—user (current account) and isLoading (bootstrap/login/logout in progress). It exposes them along with login and logout functions.
// login talks to /api/auth/token/; the backend sets HttpOnly cookies, and then fetchMe() loads the user and stores it.
// logout hits /api/auth/logout/, clears cookies server-side, then resets frontend state.
// On mount, a bootstrap effect calls /api/me/ to restore a session if cookies already exist.
// useMemo ensures consumers only re-render when user or isLoading actually change.
// useAuth() is the safe helper so components can grab { user, isLoading, login, logout } without re-implementing context logic.
// The design keeps auth logic in one place, reuses secure HttpOnly cookies instead of exposing tokens to React, and gives every component a single, consistent source of truth for the authentication state.

//=====================================================================================================================//
// Summary / mental model
// ----------------------
// - AuthProvider = the “auth brain” of the app.
//   - Knows how to log in, register, log out, and restore sessions.
//   - Owns `user` + `isLoading` state.
// - useAuth() = the “auth API” for the rest of the app.
//   - Components call useAuth() to *read* auth state and trigger actions.
// - Backend handles all JWT + cookie details; frontend only:
//
//     - POST /api/auth/token/       (login)
//     - POST /api/auth/register/    (signup)
//     - POST /api/auth/logout/      (logout)
//     - GET  /api/me/               (who am I?)
//
// - Because cookies are HttpOnly and handled by the browser, the React side
//   never stores or reads raw tokens → safer and simpler.
//
// - This design gives:
//     - single source of truth for auth
//     - shared state across the whole app (navbar, protected routes, pages)
//     - clean separation between “auth logic” (here) and UI (pages/components).