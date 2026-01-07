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

  // Wait for either navigation or the loading button state change
  // This ensures the form is actually processing before we check URL
  const [response] = await Promise.all([
    page.waitForResponse(
      response => 
        response.url().includes("/api/auth/token/") && 
        (response.status() === 200 || response.status() === 400),
      { timeout: 30_000 }
    ),
    submitBtn.click()
  ]);

  // If login succeeded (200), wait for redirect to home
  if (response.status() === 200) {
    await page.waitForURL("/", { timeout: 30_000 });
    
    // Verify username is displayed in navbar
    const navUsername = page.getByTestId("nav-username");
    await expect(navUsername).toBeVisible({ timeout: 10_000 });
    await expect(navUsername).toContainText("superuser", { timeout: 5_000 });
  } else {
    // Login failed - should stay on login page or show error
    throw new Error("Login API returned status " + response.status());
  }
});
