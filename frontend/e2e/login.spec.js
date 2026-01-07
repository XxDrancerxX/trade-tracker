// frontend/e2e/login.spec.js
import { test, expect } from "@playwright/test";

test("login redirects and shows username", async ({ page }) => {
  // Navigate to login page
  await page.goto("/login", { waitUntil: "networkidle" });

  // Get form inputs
  const userInput = page.getByTestId("login-username");
  const passInput = page.getByTestId("login-password");
  const submitBtn = page.getByTestId("login-submit");

  // Wait for username input to be visible
  await expect(userInput).toBeVisible({ timeout: 30_000 });
  
  // Fill username
  await userInput.fill(process.env.E2E_USER || "superuser");

  // Wait for password input to be visible
  await expect(passInput).toBeVisible({ timeout: 30_000 });
  
  // Fill password
  await passInput.fill(process.env.E2E_PASS || "123456");

  // Wait for submit button to be visible
  await expect(submitBtn).toBeVisible({ timeout: 30_000 });

  // Click submit and wait for URL to change to home page
  // The login flow is: submit → API call → fetch user → redirect
  await submitBtn.click();
  
  // Wait for the page to navigate away from /login
  // This waits for the actual redirect after successful login
  await page.waitForURL("http://localhost:5173/", { timeout: 30_000 });

  // Verify username is displayed in navbar
  const navUsername = page.getByTestId("nav-username");
  await expect(navUsername).toBeVisible({ timeout: 10_000 });
  await expect(navUsername).toContainText("superuser", { timeout: 5_000 });
});
