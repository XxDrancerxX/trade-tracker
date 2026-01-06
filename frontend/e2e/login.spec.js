import { test, expect } from "@playwright/test";

test("login redirects and shows username", async ({ page }) => {

  // 🔍 DEBUG: listen to backend auth responses
  page.on("response", async (res) => {
    if (res.url().includes("/api/auth/token/")) {
      console.log("TOKEN RESPONSE:", res.status());
      console.log("TOKEN BODY:", await res.text());
    }
  });

  // 🔍 DEBUG: browser console logs
  page.on("console", (msg) => {
    console.log("BROWSER LOG:", msg.type(), msg.text());
  });

  // 1) Open login page
  await page.goto("/login");

  // 2) Fill form
  await page.getByTestId("login-username").fill(
    process.env.E2E_USER || "superuser"
  );

  await page.getByTestId("login-password").fill(
    process.env.E2E_PASS || "123456"
  );

  // 3) Submit
  await page.getByTestId("login-submit").click();

  // 4) FIRST assert login success (user visible)
  await expect(page.getByTestId("nav-username")).toContainText(
    process.env.E2E_USER || "superuser"
  );

  // 5) THEN assert redirect
  await expect(page).toHaveURL(/\/$/);
});
