// src/pages/SignupPage.jsx
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext"; // adjust path if needed

function SignupPage() {
    const { user, isLoading } = useAuth();
    const navigate = useNavigate(); // Hook to programmatically navigate between routes. 
    const [username, setUsername] = useState(""); //creates React state stored in memory for this component.
    const [password, setPassword] = useState(""); //creates React state stored in memory for this component.
    const [passwordConfirm, setPasswordConfirm] = useState(""); //creates React state stored in memory for this component.
    const [error, setError] = useState("");
    const [isSubmitting, setIsSubmitting] = useState(false);// State to track if form is being submitted.

    // If already logged in, don't allow visiting /signup
    useEffect(() => { // runs after every render when dependencies change
        //We wait for isLoading to be false(bootstrap finished) and check if user is truthy (someone is logged in).
        //If both are true, we  call navigate to redirect to home page using ("/") and replace: true to avoid adding a new entry in history stack.
        if (!isLoading && user) { // If not loading and user is logged in, redirect to home page
            navigate("/", { replace: true }); // replace: true prevents adding a new entry to the history stack.
        }
    }, [user, isLoading, navigate]); // dependencies for useEffect hook, so it runs when these change.

    function handleSubmit(e) {
        e.preventDefault();// Prevent default form submission behavior
        setError(""); // Clear previous errors

        // Basic required fields:
        // Trim removes whitespace from both ends of a string.
        // "   " (three spaces) is considered a non-empty string in JavaScript.
        // " ".trim() becomes "", so !password.trim() returns true and you block the submission.
        if (!username.trim() || !password.trim() || !passwordConfirm.trim()) {
            setError("Please fill in all fields.");
            return;
        }

        //Passwor match check
        if (password !== passwordConfirm) {
            setError("Passwords do not match");
            return;
        }

        setIsSubmitting(true);
        console.log("Signup form submit:", { username, password, passwordConfirm });
        setIsSubmitting(false);
    }

    return (
        //Top-level div to center the signup form with max width and margin.
        <div style={{ maxWidth: 400, margin: "2rem auto" }}>
            <h1>Sign up</h1>

            {/* Signup form Container, it groups the inputs and manages submission*/}
            <form onSubmit={handleSubmit}> {/* When the form is submitted, it triggers handleSubmit function. */}
                {/* groups label/input pair for layout. */}
                <div style={{ marginBottom: "0.5rem" }}>
                    {/*  wraps text and input. Clicking the label focuses the input because the input is nested. */}
                    <label>
                        Username
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)} // updates the state every time the user types.
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
                            style={{ width: "100%", padding: "0.25rem" }}
                        />
                    </label>
                </div>

                <div style={{ marginBottom: "0.5rem" }}>
                    <label>
                        Confirm password
                        <input
                            type="password"
                            value={passwordConfirm}
                            onChange={(e) => setPasswordConfirm(e.target.value)}
                            style={{ width: "100%", padding: "0.25rem" }}
                        />
                    </label>
                </div>
                {error && (
                    <p style={{ color: "crimson", marginTop: "0.5rem" }}>
                        {error}
                    </p>
                )}
                {/* disabled greys out the button when isSubmitting is true.
                When we start the submit handler, we call setIsSubmitting(true) → button disables.
                When the handler finishes, we call setIsSubmitting(false) → button re-enables.
                This prevents double-submits while the request is in flight. */}
                <button type="submit" style={{ width: "100%", marginTop: "0.5rem" }} disabled={isSubmitting}>{/* Type of button triggers form submission onSubmit, disabled when submitting to prevent multiple submissions */}
                    {isSubmitting ? "creating account..." : "Create account"}
                </button>
            </form>
        </div>
    );
}

export default SignupPage;
