// src/auth/ProtectedRoute.jsx
import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "./AuthContext";

/**
 * ProtectedRoute
 *
 * - While auth is bootstrapping (isLoading === true), show a loading UI.
 * - If user is not logged in, redirect to /login.
 * - If user is logged in, render the protected children.
 */
export function ProtectedRoute({ children }) { // children is the protected content to render if authenticated
  const { user, isLoading } = useAuth();
  const location = useLocation();

  // 1) Still checking if the user is logged in → avoid flicker
  if (isLoading) {
    return <div>Loading...</div>; 
  }

  // 2) Finished loading, but no user → send to /login
  if (!user) {
    return (
      <Navigate
        to="/login"
        replace
        state={{ from: location }} // useful later to redirect back after login
      />
    );
  }

  // 3) Authenticated → render the protected content
  return children;
}

// ProtectedRoute
// --------------
// Wrapper for routes that require authentication.
// - Reads { user, isLoading } from AuthContext via useAuth().
// - While auth state is loading (initial /api/me/ check), shows "Loading..."
//   so we don't redirect or show protected UI too early.
// - After loading:
//     - If there is NO user → <Navigate> to "/login", passing along the
//       current location in state ({ from: location }) so we can send the
//       user back here after a successful login.
//     - If there IS a user → render the protected children (the page wrapped
//       inside <ProtectedRoute>).