import { test, expect } from "@playwright/test";

test("login redirects and shows username", async ({ page }) => {
  await page.goto("/login");

  await page.getByTestId("login-username").fill(process.env.E2E_USER || "superuser");
  await page.getByTestId("login-password").fill(process.env.E2E_PASS || "123456");

  await page.getByTestId("login-submit").click();

  await expect(page).toHaveURL(/\/$/);

  await expect(page.getByTestId("nav-username")).toContainText(
    process.env.E2E_USER || "superuser"
  );
});
