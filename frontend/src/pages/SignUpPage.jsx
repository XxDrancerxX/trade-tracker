// src/pages/SignupPage.jsx
import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext"; // adjust path if needed

function SignupPage() {
    const { user, isLoading, register } = useAuth(); // Custom hook to access auth context.
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

    // Turn DRF error payload into one friendly message
    function normalizeError(err) {
        if (!err) return "Signup failed.";
        const body = err.body || {};

        if (Array.isArray(body.non_field_errors) && body.non_field_errors.length) {
            return body.non_field_errors[0];
        }
        if (Array.isArray(body.username) && body.username.length) {
            return `Username: ${body.username[0]}`;
        }
        if (Array.isArray(body.password) && body.password.length) {
            return `Password: ${body.password[0]}`;
        }
        if (typeof err.message === "string") {
            return err.message;
        }
        return "Signup failed.";
    }

    async function handleSubmit(e) {
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

        if (password.length < 8) {
            setError("Password must be at least 8 characters.");
            return;
        }

        setIsSubmitting(true);
        const { ok, error: err } = await register(username.trim(), password); // Call register from auth context
        setIsSubmitting(false);

        if (!ok) {
            setError(normalizeError(err));
            return;
        }

        // Success: user created, cookies set, AuthContext.user updated
        navigate("/", { replace: true });


    }

    return (
        // Top-level div to center the signup form with max width and margin.
        <div style={{ maxWidth: 400, margin: "2rem auto" }}>
            {/* Simple header with link back to login */}
            <div style={{ marginBottom: "1rem", display: "flex", justifyContent: "space-between" }}>
                <span>Trade Tracker</span>
                <Link to="/login">Login</Link>
            </div>

            <h1>Sign up</h1>

            {/* Signup form Container */}
            <form onSubmit={handleSubmit} noValidate>
                <div style={{ marginBottom: "0.5rem" }}>
                    <label>
                        Username
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
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

                <button
                    type="submit"
                    style={{ width: "100%", marginTop: "0.5rem" }}
                    disabled={isSubmitting}
                >
                    {isSubmitting ? "creating account..." : "Create account"}
                </button>
            </form>
        </div>
    );
}

export default SignupPage;
