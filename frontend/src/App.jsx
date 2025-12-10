// filepath: /workspaces/trade-tracker/frontend/src/App.jsx
// "react" from node_modules/react. It exports a default object plus named exports (hooks, utilities).
// "React" is the default export, containing the core React API. It contains element such as createElement, Fragment, useEffect, useMemo, etc.
// src/App.jsx

import React from "react"; 3
import { ProtectedRoute } from "./auth/ProtectedRoute.jsx"; // Component to protect routes that require authentication.
import { Routes, Route, Navigate } from "react-router-dom"; // React Router components for routing.
// Routes: container for Route elements, matches the current URL to a Route.
// Route: defines a mapping from a path to a component.
// Navigate: component to programmatically redirect to another route.
import { useAuth } from "./auth/useAuth";  // Custom hook to access auth context. 
import LoginPage from "./pages/LoginPage.jsx"; //  Login page component.
import SignupPage from "./pages/SignUpPage.jsx"; // Signup page component.
import { apiFetch } from "./apiClient.js"; // Custom API fetch function with auth handling.





function Header() {
  //This is object destructuring, extracting user, logout, and isLoading from the object returned by useAuth().
  const { user, logout, isLoading } = useAuth(); // Custom hook to access auth context.

  async function handleLogout() {
    try {
      await logout(); // Call logout function from auth context
    } catch (err) {
      console.error("Logout error:", err);
    }
  }

  return (
    <header style={{ padding: "1rem 2rem", borderBottom: "1px solid #ddd" }}>
      <span style={{ fontWeight: "bold", marginRight: "1rem" }}>
        Trade Tracker
      </span>

      {isLoading && <span>Loading session…</span>} {/*If isLoading is true, show loading message */}

      {!isLoading && !user && (
        <a href="/login">Login</a>  // If not loading and no user(both conditions have to be true),show login link
      )}

      {!isLoading && !user && (
        <a href="/signup">Signup</a>  // If not loading and no user(both conditions have to be true),show login link
      )}

      {!isLoading && user && ( // If not loading and user is logged in, show username and logout button
        <> {/* This is a React Fragment - a wrapper that doesn't create an actual HTML element.  */}
          <span style={{ marginRight: "1rem" }}>
            Logged in as <strong>{user.username}</strong>
          </span>
          <button onClick={handleLogout}>Logout</button> {/* Logout button triggers handleLogout */}
        </>
      )}
    </header>
  );
}

function HomePage() {
  const { user, isLoading } = useAuth();

  async function handleTestApi() {
    try {
      const data = await apiFetch("/api/me/");
      console.log("API OK:", data);
    } catch (err) {
      console.error("RAW ERROR:", err);              // 👈 add this
      console.error("API ERROR:", {
        status: err.status,
        code: err.code,
        body: err.body,
      });
    }
  }


  return (
    <div style={{ padding: "2rem" }}>
      <h1>Home</h1>

      {isLoading && <p>Checking session…</p>}
      {!isLoading && user && (
        <>
          <p>
            Welcome back, <strong>{user.username}</strong>!
          </p>
        </>
      )}
      <button onClick={handleTestApi}>
        Test /api/me (refresh flow)
      </button>
    </div>
  );
}

function App() {
  return (
    <>
      <Header />
      <Routes>
        {/* 🔒 PROTECTED HOME */}
        <Route
          path="/"
          element={
            // <ProtectedRoute>
            <HomePage />
            // {/* </ProtectedRoute> */}
          }
        />

        {/* 🔓 PUBLIC ROUTES */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />

        {/* Catch-all redirects to "/" (which is protected) */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>

    </>
  );
}

export default App;
