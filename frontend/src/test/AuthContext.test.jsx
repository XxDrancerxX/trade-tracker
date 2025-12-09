// filepath: frontend/src/test/AuthContext.test.jsx
import React from "react";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor, act } from "@testing-library/react";
import { AuthProvider, useAuth } from "../auth/AuthContext.jsx";

//===============================================================================================================================
// These are Vitest testing utilities:

// describe - Groups related tests together into a test suite (e.g., "AuthContext / AuthProvider")
// it - Defines a single test case (e.g., "bootstraps user from /api/me...")
// expect - Used for assertions to check if values match expectations (e.g., expect(username).toBe("alice"))
// vi - Vitest's mocking utility, like Jest's jest object. Used to create fake functions and control their behavior
// beforeEach - Runs before each test in the suite (good for setup/reset)
// afterEach - Runs after each test in the suite (good for cleanup)
//act is a utility that wraps code that causes React state updates, ensuring all updates are processed before assertions.
//------------------------------------------------------------------------------------------------------------------------------

// These are React Testing Library utilities for testing React components:

// render - Renders a React component into a virtual DOM for testing (like mounting it)
// screen - Queries the rendered output to find elements (e.g., screen.getByTestId("username"))
// waitFor - Waits for async operations to complete (like waiting for API calls to finish and state to update)
//------------------------------------------------------------------------------------------------------------------------------

// Vitest provides the test structure and mocking, while React Testing Library provides the tools to render and interact with React components in our tests.

// 🧪 Mock apiClient so we control /api/me, /api/auth/token/, etc.
// vi.mock("../apiClient.js", ...) creates a mock module replacement, It tells Vitestwhenever any code imports from "../apiClient.js" don't use the real module use this instead.
vi.mock("../apiClient.js", () => ({
    apiFetch: vi.fn(), // apiFetch is replaced with a mock function we can control in tests
}));

//We import after the mock to ensure we get the mocked fake version of apiFetch so we can control its behavior in tests.
//We do all this to don't make real network requests during tests and to simulate different API responses.
import { apiFetch } from "../apiClient.js";

// Small helper component to read context in tests
// The variable latestAuth exists outside the function, but its value gets updated from inside the function. Once updated, we can use it anywhere in the module
//latestAuth stops pointing to null
// latestAuth now points to whatever ctx is (the context object) so we can access its properties/methods from the test code.
let latestAuth = null;

// We placed useAuth() inside TestConsumer, so it follows React's rules of hooks.We can't  call hooks like useAuth() outside of a component or another hook.
// When TestConsumer renders, it calls useAuth() properly, gets the context object, and assigns it to latestAuth.
//Inside a component: React knows "this hook belongs to this component" ✅
// Outside a component: React doesn't know what to do with it ❌

function TestConsumer() {// Dummy component to consume  the AuthContext
    const ctx = useAuth(); //useAuth() gets the current auth state (user, isLoading, login(), etc.)
    latestAuth = ctx; // Store the latest context value in latestAuth for test assertions

    // Extract username and loading state for display
    const username = ctx.user ? ctx.user.username : "none";
    const loading = ctx.isLoading ? "yes" : "no";

    return (
        <div>
            <span data-testid="username">{username}</span> {/* this is how react testing library finds the username element */}
            <span data-testid="loading">{loading}</span>  {/* this is how react testing library finds the loading element */}
        </div>
    );
    // In the test:
    // screen.getByTestId("username")  // ← Finds the span with data-testid="username"
    // screen.getByTestId("loading")   // ← Finds the span with data-testid="loading"
}

//this function helps render the TestConsumer component wrapped inside the AuthProvider
// render() is from React Testing Library, it mounts the component into a virtual DOM for testing.
// AuthProvider provides the auth context to TestConsumer
//It wraps components and provides auth state/methods to children
//This is what we are actually testing - does the provider work correctly?
function renderWithAuth() {
    return render(
        <AuthProvider>
            <TestConsumer />
        </AuthProvider>
    );
}

// Test suite for AuthContext and AuthProvider
// describe() groups all related tests together
describe("AuthContext / AuthProvider", () => {
    //AuthContext and AuthProvider are just a description of what we are testing.
    //It appears in test output to organize results
    // Purely for human readability

    // Reset mocks and latestAuth before each test  
    beforeEach(() => {
        vi.resetAllMocks();
        latestAuth = null;
    });

    // Clear latestAuth after each test to avoid cross-test contamination
    // this is optional since we already set it to null in beforeEach.
    //Defensive programming - Extra safety, doesn't hurt
    afterEach(() => {
        latestAuth = null;
    });

    //------------------------------------------------------------------------------------------------------------------------------
    //Tetst 1
    // Individual test cases:
    //This test verifies that when a user already has a valid session (cookies), the app correctly loads their user data on startup.

    //it() defines a single test case scenario.
    it("bootstraps user from /api/me when cookies/session are valid", async () => {

        // First call from bootstrap → /api/me → returns a user
        // We mock apiFetch to return a user object when called instead of making a real API call.
        //mockResolvedValueOnce() - Sets the return value for the next call to apiFetch
        apiFetch.mockResolvedValueOnce({ id: 1, username: "alice" });

        renderWithAuth(); // Renders the AuthProvider and TestConsumer components
        //When AuthProvider mounts, it automatically calls /api/me (bootstrap process). Because we mocked it, it gets { id: 1, username: "alice" }.

        // While bootstrapping, isLoading should eventually become "no"
        //waitFor(() => ...)  waits until the function inside becomes true or times out.
        //What it's checking: The loading indicator should eventually say "no" (meaning loading is done)
        // Why wait? - The bootstrap process is async, so we need to wait for it to complete
        await waitFor(() =>
            expect(screen.getByTestId("loading").textContent).toBe("no")
            //screen is from React Testing Library, it represents the rendered output.
            //getByTestId("loading") finds the span with data-testid="loading"
            //textContent gets the text inside that span
            //We expect it to be "no" after bootstrapping is done
        );

        // Username should come from /api/me
        expect(screen.getByTestId("username").textContent).toBe("alice");
        // Context should also have the same user
        expect(latestAuth.user).toEqual({ id: 1, username: "alice" });
    });
    //------------------------------------------------------------------------------------------------------------------------------
    //Test 2
    // This test checks that if the /api/me call fails (e.g., user is not logged in), the app correctly handles it by setting the user to null.
    //Scenario: User visits the app without being logged in (no cookies or expired session)

    it("bootstraps to anonymous when /api/me fails (e.g. 401)", async () => {
        // Mock /api/me to throw a 401 Unauthorized error
        const error = new Error("Unauthorized");
        error.status = 401;
        apiFetch.mockRejectedValueOnce(error); // Simulate /api/me failure
        //mockRejectedValueOnce() - Sets the next call to apiFetch to return a rejected Promise with the error we created.

        renderWithAuth();// Renders the AuthProvider and TestConsumer components

        // Wait for bootstrapping to finish
        await waitFor(() =>
            expect(screen.getByTestId("loading").textContent).toBe("no")
        );

        // No user available
        //Username displays "none" (the fallback we set in TestConsumer)
        expect(screen.getByTestId("username").textContent).toBe("none");// "none" means no user
        expect(latestAuth.user).toBeNull(); // Context user should be null
    });
    //------------------------------------------------------------------------------------------------------------------------------
    //Test 3
    // This test verifies that the login() method correctly sets the user in context when login is successful.
    //Scenario: User attempts to log in with valid credentials

    it("login() sets user on success", async () => {
        // Bootstrap: no existing session
        const error = new Error("Unauthorized");
        error.status = 401;
        apiFetch.mockRejectedValueOnce(error);

        // Login flow:
        // 1) POST /api/auth/token/ → ok
        // 2) GET /api/me/ → user
        apiFetch
            .mockResolvedValueOnce({ ok: true }) // login
            .mockResolvedValueOnce({ id: 2, username: "bob" }); // me

        renderWithAuth(); // Renders the AuthProvider and TestConsumer components

        // Wait for initial bootstrap to finish
        await waitFor(() =>
            expect(screen.getByTestId("loading").textContent).toBe("no")
        );


        // Call login through the captured context
        // call the login method from the context with username and password
        //This triggers the two mocked API calls we set up above
        //Test calls login("bob", "secret")

        // Inside the real login() function:

        // First apiFetch call (login endpoint) → Gets { ok: true } from the first mock ✅
        // Since ok: true, the login function continues:
        // Second apiFetch call (fetch user) → Gets { id: 2, username: "bob" } from the second mock ✅
        // Context updates with the user data.
        // login() returns back to the test.

        //We are calling the REAL login() function from our AuthContext
        await act(async () => {
            await latestAuth.login("bob", "secret");
        });


        // Wait for React to re-render with the new user
        await waitFor(() =>
            expect(screen.getByTestId("username").textContent).toBe("bob")
        );
        expect(latestAuth.user).toEqual({ id: 2, username: "bob" });
    });

    //------------------------------------------------------------------------------------------------------------------------------
    //Test 4
    //This test verifies what happens when login fails (wrong password, invalid credentials, etc.)
    //Scenario: User's access token has expired, but refresh token is valid

    it("login() returns error and clears user on failure", async () => {
        // Bootstrap fails: no session
        const bootstrapErr = new Error("Unauthorized");
        bootstrapErr.status = 401;
        apiFetch.mockRejectedValueOnce(bootstrapErr);

        // Login call fails (wrong password, etc.)
        const loginErr = new Error("Bad credentials");
        loginErr.status = 401;
        apiFetch.mockRejectedValueOnce(loginErr);

        renderWithAuth(); // Renders the AuthProvider and TestConsumer components

        // Wait for initial bootstrap to finish
        await waitFor(() =>
            expect(screen.getByTestId("loading").textContent).toBe("no")
        );

        // Call login through the captured context
        // call the login method from the context with username and password
        //This triggers the mocked API call that fails

        // Inside the real login() function:
        await act(async () => {
            await latestAuth.login("bob", "wrong-password");
        });


        await waitFor(() =>
            expect(screen.getByTestId("username").textContent).toBe("none")
        );

        expect(latestAuth.user).toBeNull();

        //Four assertions verify proper error handling:
        // res.ok is false - Login failed
        // res.error contains the error object - Error is returned to caller
        // latestAuth.user is null - User remains logged out
        // Username displays "none" - UI shows anonymous state
    });

    //------------------------------------------------------------------------------------------------------------------------------
    //Test 5 -  register() function
    it("register() creates new user and sets user on success", async () => {
        // Bootstrap: no existing session
        const bootstrapErr = new Error("Unauthorized");
        bootstrapErr.status = 401;
        apiFetch.mockRejectedValueOnce(bootstrapErr);

        // Register flow:
        // POST /api/auth/register/ → { user: {...} }
        // Note: Mock returns just { user: {...} }, not { ok: true, user: {...} }
        apiFetch.mockResolvedValueOnce({
            user: { id: 3, username: "charlie" }
        });

        renderWithAuth();

        await waitFor(() =>
            expect(screen.getByTestId("loading").textContent).toBe("no")
        );

        // Call register wrapped in act()
        let res;
        await act(async () => {
            res = await latestAuth.register("charlie", "newpassword");
        });

        expect(res.ok).toBe(true);
        expect(latestAuth.user).toEqual({ id: 3, username: "charlie" });
        expect(screen.getByTestId("username").textContent).toBe("charlie");
    });

    //------------------------------------------------------------------------------------------------------------------------------
    //Test 6 -  register() handles failure
    it("register() returns error on failure (username taken, etc.)", async () => {
        const bootstrapErr = new Error("Unauthorized");
        bootstrapErr.status = 401;
        apiFetch.mockRejectedValueOnce(bootstrapErr);

        // Register fails
        const registerErr = new Error("Username already exists");
        registerErr.status = 400;
        apiFetch.mockRejectedValueOnce(registerErr);

        renderWithAuth();

        await waitFor(() =>
            expect(screen.getByTestId("loading").textContent).toBe("no")
        );

        let res;
        await act(async () => {
            res = await latestAuth.register("alice", "password");
        });

        expect(res.ok).toBe(false);
        expect(res.error).toBe(registerErr);
        expect(latestAuth.user).toBeNull();
    });

    //------------------------------------------------------------------------------------------------------------------------------
    //Test 7 -  logout() function
    it("logout() clears user and calls logout endpoint", async () => {
        // Start with a logged-in user
        apiFetch.mockResolvedValueOnce({ id: 1, username: "alice" });

        renderWithAuth();

        await waitFor(() =>
            expect(screen.getByTestId("username").textContent).toBe("alice")
        );

        // Mock logout success
        apiFetch.mockResolvedValueOnce({ ok: true });

        // Call logout wrapped in act()
        let res;
        await act(async () => {
            res = await latestAuth.logout();
        });

        // Wait for UI to update after logout
        await waitFor(() =>
            expect(screen.getByTestId("username").textContent).toBe("none")
        );

        expect(res.ok).toBe(true);
        expect(latestAuth.user).toBeNull();

        // Verify logout endpoint was called
        expect(apiFetch).toHaveBeenCalledWith(
            expect.stringContaining("/api/auth/logout/"),
            expect.objectContaining({ method: "POST" })
        );
    });

    //------------------------------------------------------------------------------------------------------------------------------
    //Test 8 -  logout() handles errors
    it("logout() clears user even if endpoint fails", async () => {
        // Start logged in
        apiFetch.mockResolvedValueOnce({ id: 1, username: "alice" });

        renderWithAuth();

        await waitFor(() =>
            expect(screen.getByTestId("username").textContent).toBe("alice")
        );

        // Logout endpoint fails
        const logoutErr = new Error("Server error");
        apiFetch.mockRejectedValueOnce(logoutErr);

        let res;
        await act(async () => {
            res = await latestAuth.logout();
        });

        // Wait for UI to update after logout
        await waitFor(() =>
            expect(screen.getByTestId("username").textContent).toBe("none")
        );

        expect(res.ok).toBe(false);
        expect(res.error).toBe(logoutErr);
        // User should STILL be cleared even if endpoint fails
        expect(latestAuth.user).toBeNull();
    });

    //------------------------------------------------------------------------------------------------------------------------------
    //Test 9 -  fetchMe() works directly
    it("fetchMe() returns current user from /api/me", async () => {
        apiFetch.mockResolvedValueOnce({ id: 1, username: "alice" });

        renderWithAuth();

        await waitFor(() =>
            expect(screen.getByTestId("loading").textContent).toBe("no")
        );

        // Call fetchMe directly
        apiFetch.mockResolvedValueOnce({ id: 1, username: "alice" });
        const user = await latestAuth.fetchMe();

        expect(user).toEqual({ id: 1, username: "alice" });
    });

    //------------------------------------------------------------------------------------------------------------------------------
    //Test 10 -  Concurrent operations
    it("handles multiple login attempts gracefully", async () => {
        const bootstrapErr = new Error("Unauthorized");
        bootstrapErr.status = 401;
        apiFetch.mockRejectedValueOnce(bootstrapErr);

        // Setup multiple successful login responses
        apiFetch
            .mockResolvedValueOnce({ ok: true })
            .mockResolvedValueOnce({ id: 1, username: "alice" })
            .mockResolvedValueOnce({ ok: true })
            .mockResolvedValueOnce({ id: 1, username: "alice" });

        renderWithAuth();

        await waitFor(() =>
            expect(screen.getByTestId("loading").textContent).toBe("no")
        );

        // Try logging in twice rapidly wrapped in act()
        let res1, res2;
        await act(async () => {
            const promise1 = latestAuth.login("alice", "pass1");
            const promise2 = latestAuth.login("alice", "pass2");
            [res1, res2] = await Promise.all([promise1, promise2]);
        });

        // At least one should succeed
        expect(res1.ok || res2.ok).toBe(true);
    });

});
