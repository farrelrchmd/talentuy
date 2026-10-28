import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";

import { ensureApiReady, login, openPage } from "./helpers";

/**
 * Audit aksesibilitas otomatis (WCAG 2.1 A dan AA) untuk seluruh halaman
 * utama, ditambah pemeriksaan manual atas hal yang tidak bisa dideteksi axe:
 * navigasi keyboard, focus trap drawer, dan alternatif tabel untuk grafik.
 */
const PAGES = [
  { path: "/", heading: "Ringkasan Percakapan Kandidat" },
  { path: "/tren", heading: "Analisis Tren" },
  { path: "/topik", heading: "Eksplorasi Topik" },
  { path: "/post", heading: "Pencarian Post" },
  { path: "/monitoring", heading: "Monitoring" },
  { path: "/laporan", heading: "Laporan Insight" },
  { path: "/data", heading: "Data & Pengaturan" },
  { path: "/metodologi", heading: "Metodologi & Etika Data" },
];

const WCAG_TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"];

async function analyze(page: Page) {
  return new AxeBuilder({ page }).withTags(WCAG_TAGS).analyze();
}

test.beforeAll(async () => {
  await ensureApiReady();
});

test("halaman masuk bebas pelanggaran WCAG 2.1 AA", async ({ page }) => {
  await page.goto("/masuk");
  await expect(page.getByRole("heading", { name: "Masuk ke dashboard" })).toBeVisible();

  const results = await analyze(page);
  expect(
    results.violations.map((v) => `${v.id}: ${v.help} (${v.nodes.length} elemen)`),
  ).toEqual([]);
});

test("seluruh halaman dashboard bebas pelanggaran WCAG 2.1 AA", async ({ page }) => {
  test.slow();
  await login(page, "admin");

  const failures: string[] = [];
  for (const target of PAGES) {
    await page.goto(target.path);
    await expect(page.getByRole("heading", { name: target.heading })).toBeVisible();
    await page.waitForTimeout(700); // beri waktu grafik selesai digambar

    const results = await analyze(page);
    for (const violation of results.violations) {
      failures.push(`${target.path} — ${violation.id}: ${violation.help}`);
    }
  }
  expect(failures).toEqual([]);
});

test("dashboard dapat dioperasikan dengan keyboard", async ({ page }) => {
  await login(page, "analyst");
  await page.goto("/"); // muat penuh: uji urutan Tab dari awal dokumen

  // Tautan lewati navigasi harus menjadi target Tab pertama.
  await page.keyboard.press("Tab");
  await expect(page.getByRole("link", { name: "Lewati ke konten utama" })).toBeFocused();

  // Pencarian global terbuka lewat pintasan dan tertutup dengan Escape.
  await page.keyboard.press("Control+k");
  const command = page.getByRole("dialog", { name: "Pencarian global" });
  await expect(command).toBeVisible();
  await expect(command.getByLabel("Kata kunci pencarian")).toBeFocused();
  await page.keyboard.press("Escape");
  await expect(command).toBeHidden();
});

test("fokus berpindah ke konten utama setelah ganti halaman", async ({ page }) => {
  await login(page, "analyst");
  await openPage(page, "Eksplorasi Topik");

  await expect(page.getByRole("heading", { name: "Eksplorasi Topik" })).toBeVisible();
  const mainFocused = await page.evaluate(
    () => document.activeElement?.id === "konten-utama",
  );
  expect(mainFocused, "fokus tidak dipindahkan ke konten utama").toBe(true);
});

test("drawer detail post menahan fokus dan mengembalikannya saat ditutup", async ({
  page,
}) => {
  await login(page, "analyst");
  await page.goto("/post");

  const trigger = page.getByRole("button", { name: /^Buka detail post/ }).first();
  await trigger.click();

  const drawer = page.getByRole("dialog", { name: "Detail post" });
  await expect(drawer).toBeVisible();
  // Drawer memindahkan fokus ke tombol tutup setelah terbuka.
  await expect(drawer.getByRole("button", { name: "Tutup panel detail" })).toBeFocused();

  // Tab berulang tidak boleh keluar dari drawer (focus trap).
  for (let index = 0; index < 12; index += 1) {
    await page.keyboard.press("Tab");
    const inside = await drawer.evaluate((node) =>
      node.contains(document.activeElement),
    );
    expect(inside, "fokus keluar dari drawer setelah Tab").toBe(true);
  }

  await page.keyboard.press("Escape");
  await expect(drawer).toBeHidden();
  await expect(trigger).toBeFocused(); // fokus kembali ke pemicunya
});

test("setiap grafik menyediakan alternatif tabel data", async ({ page }) => {
  await login(page, "analyst");

  const volumeCard = page.getByRole("region", { name: "Volume percakapan harian" });
  await volumeCard.getByRole("button", { name: "Lihat sebagai tabel" }).click();

  const table = volumeCard.locator("table");
  await expect(table).toBeVisible();
  await expect(table.locator("caption")).toHaveCount(1); // ringkasan untuk pembaca layar
  await expect(table.locator("thead th").first()).toBeVisible();
});
