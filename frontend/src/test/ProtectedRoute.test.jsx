// filepath: frontend/src/test/ProtectedRoute.test.jsx
import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { ProtectedRoute } from "../auth/ProtectedRoute.jsx";

// 🧪 Mock useAuth hook
// Replaces the useAuth module with a mock function
// This lets us control what useAuth returns in each test
vi.mock("../auth/useAuth", () => ({
  useAuth: vi.fn(),
}));

// Mock react-router-dom components
vi.mock("react-router-dom", () => ({
  Navigate: ({ to }) => <div>Redirect to {to}</div>,
  useLocation: () => ({ pathname: "/some-path" }),
}));

// Import AFTER mocks
import { useAuth } from "../auth/useAuth";



describe("ProtectedRoute", () => {
    // Reset mocks before each test to avoid state leakage
  beforeEach(() => {
    vi.resetAllMocks();
  });
//------------------------------------------------------------------------------------------------------------------------------
// 1st test: loading state
//This test verifies that while authentication is being checked, the component shows a loading indicator.

  it("shows loading while auth is bootstrapping", () => {
    useAuth.mockReturnValue({ // Simulate loading state
      //mockReturnValue sets what useAuth returns when called
      user: null,
      isLoading: true,
    });

    render(
      <ProtectedRoute>
        <div>Secret content</div> {/* Child content to render if authenticated */}
      </ProtectedRoute>
    );
    
    //screen.getByText(/loading/i) - Finds text matching "loading" (case-insensitive regex
    ///loading/i = regex that matches "Loading", "loading", "LOADING", etc.
    // toBeInTheDocument() - Asserts the element exists in the DOM
    expect(screen.getByText(/loading/i)).toBeInTheDocument(); 
    expect(screen.queryByText("Secret content")).toBeNull(); // Secret content should not be rendered yet
    //queryByText("Secret content") searches the rendered DOM for any element containing the text "Secret content".
    //We want to verify that "Secret content" is NOT rendered during loading.
});
//------------------------------------------------------------------------------------------------------------------------------
// 2nd test: not authenticated
//This test checks that if the user is not authenticated, they are redirected to the login page.

  it("redirects to /login when not authenticated", () => {
    useAuth.mockReturnValue({
      user: null,
      isLoading: false,
    });

    render(
      <ProtectedRoute>
        <div>Secret content</div>
      </ProtectedRoute>
    );

    // Our mocked Navigate renders this text
    expect(screen.getByText("Redirect to /login")).toBeInTheDocument();
    expect(screen.queryByText("Secret content")).toBeNull();
  });

//------------------------------------------------------------------------------------------------------------------------------
// 3rd test: authenticated
//This test ensures that when the user is authenticated, the protected content is displayed.

it("renders children when authenticated", () => {
    // Simulate authenticated user
    useAuth.mockReturnValue({
      user: { id: 1, username: "alice" },
      isLoading: false,
    });

    render(
      <ProtectedRoute>
        <div>Secret content</div>
      </ProtectedRoute>
    );

    expect(screen.getByText("Secret content")).toBeInTheDocument(); // Secret content should be rendered
    expect(screen.queryByText("Redirect to /login")).toBeNull(); // No redirect should occur
  });
});
