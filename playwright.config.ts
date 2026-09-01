import { defineConfig, devices } from "@playwright/test";

/**
 * E2E TalentPulse.
 *
 * Skenario mengikuti Tugas 1–5 pada `docs/usability_test.md` agar pengujian
 * otomatis dan pengujian bersama pengguna memakai alur yang sama.
 *
 * Backend harus berjalan lebih dulu:
 *   cd apps/api && python -m app.seed        (sekali, untuk data demo)
 *   cd apps/api && uvicorn app.main:app --port 8000
 *
 * Frontend dijalankan otomatis oleh Playwright bila belum menyala.
 */
const WEB_URL = process.env.E2E_WEB_URL ?? "http://localhost:3000";

export default defineConfig({
  testDir: "./tests/e2e",
  timeout: 60_000,
  expect: { timeout: 10_000 },
  fullyParallel: false,
  workers: 1,
  retries: process.env.CI ? 1 : 0,
  reporter: [["list"], ["html", { open: "never", outputFolder: "playwright-report" }]],
  use: {
    baseURL: WEB_URL,
    locale: "id-ID",
    timezoneId: "Asia/Jakarta",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [
    {
      name: "desktop-1366",
      use: { ...devices["Desktop Chrome"], viewport: { width: 1366, height: 768 } },
    },
  ],
  webServer: {
    command: "npm run dev",
    cwd: "apps/web",
    url: WEB_URL,
    reuseExistingServer: true,
    timeout: 120_000,
  },
});
