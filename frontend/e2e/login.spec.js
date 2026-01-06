// frontend/e2e/login.spec.js
import { test, expect } from "@playwright/test";

test("login redirects and shows username", async ({ page }) => {
  await page.goto("/login");

  const userInput = page.getByTestId("login-username");
  const passInput = page.getByTestId("login-password");

  await expect(userInput).toBeVisible({ timeout: 30_000 });
  await userInput.fill(process.env.E2E_USER || "superuser");

  await expect(passInput).toBeVisible({ timeout: 30_000 });
  await passInput.fill(process.env.E2E_PASS || "123456");

  await page.getByTestId("login-submit").click();

  await expect(page).toHaveURL("/", { timeout: 30_000 });
  await expect(page.getByTestId("nav-username")).toContainText("superuser");
});
