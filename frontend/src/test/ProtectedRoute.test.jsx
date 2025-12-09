// filepath: frontend/src/test/ProtectedRoute.test.jsx
import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { ProtectedRoute } from "../auth/ProtectedRoute.jsx";
import { Navigate, useLocation } from "react-router-dom";



// 🧪 Mock useAuth from AuthContext
//Replaces the entire AuthContext.jsx module with a fake version
//the fake version only exports useAuth as a mock function (vi.fn())
//We just want to test how ProtectedRoute reacts to different auth states
// By mocking useAuth, we can easily simulate: loading, logged in, logged out
vi.mock("../auth/AuthContext.jsx", () => ({
  useAuth: vi.fn(),
}));

vi.mock("react-router-dom", () => ({
  Navigate: ({ to }) => <div>Redirect to {to}</div>,
  useLocation: () => ({ pathname: "/some-path" }),
}));


//We import here to set up the mock return values
import { useAuth } from "../auth/AuthContext.jsx";


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
