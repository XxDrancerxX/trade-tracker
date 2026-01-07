// frontend/e2e/login.spec.js
import { test, expect } from "@playwright/test";

test("login redirects and shows username", async ({ page }) => {
  // Navigate to login page with explicit timeout
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

  // Wait for submit button and click
  await expect(submitBtn).toBeVisible({ timeout: 30_000 });
  await submitBtn.click();

  // Wait for navigation to home page
  await expect(page).toHaveURL("/", { timeout: 30_000 });
  
  // Verify username is displayed in navbar
  await expect(page.getByTestId("nav-username")).toContainText("superuser", { timeout: 30_000 });
});
