# CLAUDE.md — Konteks Kerja TalentPulse

Catatan untuk sesi Claude Code berikutnya. Tujuannya: bisa langsung melanjutkan
tanpa membaca ulang seluruh repositori.

## 1. Apa ini

Prototipe tugas akhir **TalentPulse** — dashboard internal Recruitment/HR untuk
mengeksplorasi percakapan publik pencari kerja di media sosial X.
Spesifikasi lengkap ada di `TalentPulse_Full_Project_Prompt.md` (34 KB, berbahasa
Indonesia) dan **itu sumber kebenaran** untuk lingkup, IA, dan acceptance criteria.

Batas produk yang tidak boleh dilanggar: bukan sistem seleksi, tanpa profiling
kandidat, tanpa inferensi atribut sensitif, tanpa scraping, tanpa pencarian
berbasis identitas personal, ekspor mentah dibatasi Post ID + tautan, dan tidak
mengklaim afiliasi dengan X. Detail: `docs/ethics.md`.

## 2. Status per 29 Agustus 2026

**Seluruh fitur wajib MVP selesai** (bagian 7 dokumen spesifikasi). Semua
halaman, endpoint, migration, Docker, dokumentasi, dan pengujian sudah ada.

| Lapisan | Status |
| --- | --- |
| Backend `apps/api` | 8 router, 11 tabel, Alembic revisi awal `e41ab7dc6ea3`, 61 pytest lolos |
| Frontend `apps/web` | 8 halaman + login, 43 Vitest lolos, `tsc`/ESLint bersih, `next build` sukses |
| E2E `tests/e2e` | 20 skenario Playwright lolos: Tugas 1–5, peran & data, aksesibilitas (axe-core WCAG 2.1 AA), visual QA |
| Dokumentasi | `README.md`, `CLAUDE.md`, 9 berkas `docs/`, `data/data_dictionary.md`, 32 screenshot |
| Git | **Belum ada commit sama sekali** — semua masih untracked di branch `master` |

Yang **belum** dikerjakan (sengaja, sesuai urutan dokumen): semantic search,
alert terjadwal, ringkasan LLM, SSO, notifikasi, live streaming. Daftar dan
catatan implementasinya: `docs/features.md`.

## 3. Menjalankan

```bash
# Backend (dari apps/api) — venv sudah ada di apps/api/.venv
./.venv/Scripts/python.exe -m uvicorn app.main:app --port 8000
./.venv/Scripts/python.exe -m app.seed --reset      # bila DB kosong

# Frontend (dari apps/web)
npm run dev            # http://localhost:3000

# Pengujian
cd apps/api && ./.venv/Scripts/python.exe -m pytest -q
cd apps/web && npx vitest run && npx tsc --noEmit && npx next lint
npm run typecheck      # dari root: memeriksa tests/e2e + playwright.config.ts
npx playwright test    # dari root; backend harus sudah menyala
```

Akun demo: `admin@` / `analyst@` / `viewer@talentpulse.local`, sandi
`TalentPulse123!`. Basis data lokal SQLite `apps/api/talentpulse.db` (gitignored).

## 4. Hal khas lingkungan ini (mudah bikin terjebak)

- **Windows + Git Bash.** `pkill` tidak mematikan proses native; pakai
  PowerShell `Get-CimInstance Win32_Process | ... Stop-Process`.
- **Heredoc panjang gagal** di Bash tool (`ENAMETOOLONG`) — tulis berkas besar
  dengan tool Write, bukan `cat <<EOF`.
- **Restart backend wajib** setelah mengubah kode Python; server dijalankan tanpa
  `--reload`, jadi perubahan tidak terpakai sampai proses dinyalakan ulang.
- **`npm run start` gagal setelah e2e**: Playwright menjalankan `npm run dev`
  yang menimpa `.next`. Jalankan `npm run build` lagi sebelum mode produksi.
- **Playwright ada di root**, bukan di `apps/web` (`playwright.config.ts` +
  `package.json` root). Frontend dinyalakan otomatis lewat `webServer`; backend
  tidak. Berkas TypeScript di root dicakup `tsconfig.json` root (butuh
  `@types/node` untuk `process` dan `Buffer`), terpisah dari `apps/web`.
- Setelan editor bersama ada di `.vscode/settings.json` (interpreter Python ke
  `apps/api/.venv`, pytest, ESLint diarahkan ke `apps/web`, peringatan at-rule
  CSS Tailwind dimatikan). Tanpa itu editor menandai merah padahal build bersih.
- Warna design token ditulis sebagai **kanal RGB** (`--tp-primary: 37 99 235`)
  agar modifier opacity Tailwind (`bg-warning/10`) bekerja. Jangan kembalikan ke
  format hex.
- Untuk **teks** berwarna pakai varian `text-positive-strong` / `text-warning-strong`
  / `text-negative-strong` / `text-neutral-strong`. Warna dasar hanya lolos
  kontras WCAG AA untuk ikon, garis, dan latar.
- `localhost` pada mesin ini menambah ~2 detik per permintaan CLI (percobaan
  IPv6 lebih dulu). Ukur performa lewat `127.0.0.1`.
- **React Strict Mode aktif**: effect berjalan dua kali saat mount. Jangan pakai
  penanda "render pertama"; bandingkan nilai sebelumnya (lihat fokus rute pada
  `app/(dashboard)/layout.tsx`). Jangan pula memasukkan callback tak stabil ke
  dependency effect yang punya cleanup berefek samping (lihat `Drawer`).

## 5. Peta kode singkat

```
apps/api/app/
  filters.py      FilterSet — satu sumber kebenaran filter seluruh endpoint
  analytics.py    KPI, deret waktu, puncak, breakdown, heatmap, isu perhatian
  meta.py         build_meta() — blok meta di setiap response (mode data, periode)
  nlp/            pipeline leksikon: normalisasi → topik → sentimen → intent
  search/         SearchProvider: PostgreSQL FTS / SQLite LIKE
  connectors/     mock_x (demo), official_x (X API), csv_import
  routers/        auth, dashboard, posts, queries, insights, reports, data, system

apps/web/src/
  app/(dashboard)/  ringkasan, tren, topik, post, pemantauan, laporan, data, metodologi
  hooks/useFilters  filter global; state disinkronkan ke URL query string
  hooks/useApi.ts   seluruh query & mutation TanStack Query
  lib/branding.ts   identitas + warna merek (localStorage → CSS variable)
  components/ui.tsx Card, Drawer, state kosong/error/izin, Toast, ConfirmDialog
```

## 6. Data nyata vs demo

Mode `demo` (bawaan) memakai generator sintetis. Untuk data nyata:

1. **Impor CSV/JSON** — `POST /data/import` (admin). Sertakan kolom
   `is_synthetic=false` agar tidak ditandai data demo.
2. **X API resmi** — `POST /data/fetch-live?query=...` (admin) menjalankan
   `OfficialXApiConnector`. Aktif hanya bila `X_API_BEARER_TOKEN` ada di
   environment server; tanpa itu endpoint menolak dengan 409 dan tombol di UI
   nonaktif. Endpoint `tweets/search/recent` hanya menjangkau 7 hari terakhir,
   maks. 100 post/permintaan, dan butuh langganan berbayar.

Keduanya melewati pipeline yang sama: dedup `external_post_id` → analisis NLP →
`ingestion_runs` → audit log.

## 7. Konvensi yang dipakai konsisten

- **Seluruh teks antarmuka, komentar kode, dan dokumen berbahasa Indonesia.**
- Angka yang tidak dapat dibandingkan ditulis "Tidak dapat dibandingkan", bukan 0%.
- Setiap halaman menyediakan state: loading skeleton, kosong, tanpa hasil, error
  + coba lagi, izin ditolak (`PermissionDenied`), dan konfirmasi aksi destruktif.
- Setiap grafik punya alternatif tabel (`ChartWithTable`) demi pembaca layar.
- Insight otomatis berhenti di status `draft` berlabel "Rekomendasi untuk
  Ditinjau"; persetujuan selalu manusia.
- Aksi yang mengubah data memanggil `write_audit(...)`.
- Komentar kode menjelaskan **alasan**, bukan mengulang isi baris.

## 8. Kalau melanjutkan pekerjaan

1. Baca `docs/features.md` bagian 2 untuk urutan fitur lanjutan.
2. Setelah mengubah kode: jalankan pytest + Vitest + `tsc` + lint, lalu Playwright
   bila menyentuh UI. Perbarui `docs/testing_report.md` bila jumlah tes berubah.
3. Bila mengubah model SQLAlchemy: buat migration
   (`alembic revision --autogenerate -m "..."`) dan periksa hasilnya sebelum commit.
4. Bila menambah halaman: daftarkan di `NAV_ITEMS` (`components/shell.tsx`) dan
   tambahkan ke daftar `PAGES` pada `tests/e2e/visual-qa.spec.ts`.
5. Repositori belum pernah di-commit — tanyakan dulu ke pemilik sebelum membuat
   commit pertama.
