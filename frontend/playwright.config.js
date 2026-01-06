// frontend/playwright.config.js
import { defineConfig } from "@playwright/test";

const PORT = 5173;
const baseURL = process.env.E2E_BASE_URL || `http://localhost:${PORT}`;

export default defineConfig({
  testDir: "e2e",
  testMatch: "**/*.spec.js",
  use: {
    baseURL,
    headless: true,
  },

  // Always let Playwright start the frontend server.
  // In local dev it will reuse an existing server if you already started it.
  webServer: {
    command: `npm run dev -- --host 0.0.0.0 --port ${PORT}`,
    url: baseURL,
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
    env: {
      VITE_API_URL: process.env.VITE_API_URL || "http://localhost:8000",
    },
  },
});
