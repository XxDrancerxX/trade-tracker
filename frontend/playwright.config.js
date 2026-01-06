// frontend/playwright.config.js
import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "e2e",
  testMatch: "**/*.spec.js",
  use: {
    baseURL: process.env.E2E_BASE_URL || "http://localhost:5173",
    headless: true,
  },

  webServer: {
    command: "npm run dev -- --host 0.0.0.0 --port 5173",
    url: process.env.E2E_BASE_URL || "http://localhost:5173",
    reuseExistingServer: !process.env.CI, // local: reuse if already running, CI: always start fresh
    timeout: 120_000,
    env: {
      VITE_API_URL: process.env.VITE_API_URL || "http://localhost:8000",
    },
  },
});
