import { expect, test } from "@playwright/test";

import { ensureApiReady, login } from "./helpers";

/**
 * Visual QA: menangkap screenshot halaman utama pada empat ukuran layar
 * (bagian 23 dokumen spesifikasi) dan memastikan tidak ada overflow horizontal.
 * Hasil disimpan ke `docs/screenshots/`.
 */
const VIEWPORTS = [
  { name: "1366x768", width: 1366, height: 768 },
  { name: "1920x1080", width: 1920, height: 1080 },
  { name: "tablet-768", width: 768, height: 1024 },
  { name: "mobile-390", width: 390, height: 844 },
];

const PAGES = [
  { path: "/", slug: "overview", heading: "Ringkasan Percakapan Kandidat" },
  { path: "/tren", slug: "tren", heading: "Analisis Tren" },
  { path: "/topik", slug: "topik", heading: "Eksplorasi Topik" },
  { path: "/post", slug: "post", heading: "Pencarian Post" },
  { path: "/monitoring", slug: "monitoring", heading: "Monitoring" },
  { path: "/laporan", slug: "laporan", heading: "Laporan Insight" },
  { path: "/data", slug: "data", heading: "Data & Pengaturan" },
  { path: "/metodologi", slug: "metodologi", heading: "Metodologi & Etika Data" },
];

test.beforeAll(async () => {
  await ensureApiReady();
});

for (const viewport of VIEWPORTS) {
  test(`tangkapan layar dan pemeriksaan overflow pada ${viewport.name}`, async ({
    page,
  }) => {
    test.slow();
    await page.setViewportSize({ width: viewport.width, height: viewport.height });
    await login(page, "admin");

    for (const target of PAGES) {
      await page.goto(target.path);
      await expect(page.getByRole("heading", { name: target.heading })).toBeVisible();
      // Beri waktu grafik selesai digambar sebelum ditangkap.
      await page.waitForTimeout(600);

      await page.screenshot({
        path: `docs/screenshots/${viewport.name}/${target.slug}.png`,
        fullPage: false,
      });

      const overflow = await page.evaluate(
        () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
      );
      expect(
        overflow,
        `Halaman ${target.path} memiliki overflow horizontal pada ${viewport.name}`,
      ).toBeLessThanOrEqual(1);
    }
  });
}
