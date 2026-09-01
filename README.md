# TalentPulse

**Dengar percakapan kandidat. Perjelas komunikasi rekrutmen.**

Dashboard web internal untuk tim Recruitment/HR yang membantu mengeksplorasi
percakapan publik pencari kerja di media sosial X, menemukan pertanyaan dan
kekhawatiran yang berulang, lalu mengubahnya menjadi bahan FAQ, konten edukasi,
dan perbaikan komunikasi lowongan.

> **Prototipe akademis.** TalentPulse tidak berafiliasi resmi dengan X, tidak
> melakukan profiling kandidat, dan tidak boleh dipakai sebagai dasar keputusan
> penerimaan atau penolakan kandidat. Pada mode demo seluruh angka berasal dari
> **dataset sintetis** dan diberi label `DATA SINTETIS — BUKAN TEMUAN AKTUAL`.

## Status

Seluruh fitur wajib MVP selesai dan dapat dijalankan dari clean setup.

| Aspek | Status |
| --- | --- |
| Halaman | 8 halaman utama + login, seluruhnya berbahasa Indonesia |
| Backend | 61 pengujian pytest lolos |
| Frontend | 43 pengujian Vitest lolos · `tsc --noEmit` dan ESLint bersih · `next build` sukses |
| End-to-end | 20 skenario Playwright lolos (Tugas 1–5, peran & data, aksesibilitas, visual QA) |
| Aksesibilitas | Audit axe-core WCAG 2.1 AA pada 9 halaman: nol pelanggaran |
| Performa | `/dashboard/overview` 49 ms pada 1.400 post, 134 ms pada 5.000 post (target < 3 detik) |
| Data demo | 1.400 post sintetis / 90 hari, dapat direproduksi dari generator |
| Fitur lanjutan | Belum dikerjakan sesuai urutan pada [`docs/features.md`](docs/features.md) |

Rincian: [`docs/testing_report.md`](docs/testing_report.md).

---

## Quick start (Docker)

```bash
cp .env.example .env
docker compose up --build
docker compose exec backend python -m app.seed --reset
```

| Layanan       | URL                            |
| ------------- | ------------------------------ |
| Dashboard web | http://localhost:3000          |
| API           | http://localhost:8000          |
| Dokumentasi API (Swagger) | http://localhost:8000/docs |
| Health check  | http://localhost:8000/health   |

### Akun demo

| Email                       | Role    | Hak akses                                                |
| --------------------------- | ------- | -------------------------------------------------------- |
| `admin@talentpulse.local`   | admin   | Seluruh fitur + sumber data, taxonomy, koreksi label, audit log |
| `analyst@talentpulse.local` | analyst | Seluruh dashboard, query, monitor, insight, laporan       |
| `viewer@talentpulse.local`  | viewer  | Membaca dashboard dan laporan saja                        |

Password demo: nilai `DEMO_PASSWORD` pada `.env` (bawaan `TalentPulse123!`).
Password ini **hanya untuk development**; ganti sebelum dipakai di lingkungan
lain.

---

## Menjalankan tanpa Docker

### Backend (FastAPI, Python 3.12)

```bash
cd apps/api
python -m venv .venv
.venv/Scripts/activate          # Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

alembic upgrade head            # membuat skema (SQLite bila DATABASE_URL kosong)
python -m app.seed --reset      # dataset demo sintetis + akun demo
uvicorn app.main:app --reload --port 8000
```

Tanpa `DATABASE_URL`, backend memakai SQLite (`apps/api/talentpulse.db`) sehingga
proyek tetap bisa dijalankan tanpa Docker. Periksa dengan:

```bash
curl http://localhost:8000/health
# {"status":"ok","database":{"connected":true},"data_source_mode":"demo","seeded":true,...}
```

### Frontend (Next.js 15, Node 20+)

```bash
cd apps/web
cp .env.local.example .env.local
npm install
npm run dev                     # http://localhost:3000
```

Buka http://localhost:3000, masuk dengan salah satu akun demo, lalu mulai dari
**Overview**. Badge `DATA DEMO` pada top bar menandakan seluruh angka berasal
dari dataset sintetis.

---

## Struktur repositori

```text
talentpulse/
├── apps/
│   ├── api/                    # FastAPI, SQLAlchemy, Alembic, NLP baseline
│   │   ├── app/
│   │   │   ├── routers/        # auth, dashboard, posts, queries, insights, reports, data, system
│   │   │   ├── nlp/            # pipeline label topik, sentimen, intent (dapat dijelaskan)
│   │   │   ├── search/         # abstraksi pencarian (SQL provider)
│   │   │   └── connectors/     # mock X, X API resmi, impor CSV/JSON
│   │   ├── alembic/            # database migration
│   │   └── tests/              # pytest
│   └── web/                    # Next.js App Router, Tailwind, Recharts
│       └── src/
│           ├── app/(dashboard)/# 8 halaman utama
│           ├── components/     # shell, chart, filter, state UI
│           ├── hooks/          # auth, filter global, data fetching
│           └── lib/            # klien API, format ID, design token merek
├── data/
│   ├── synthetic/              # contoh berkas impor
│   └── data_dictionary.md
├── docs/                       # arsitektur, IA, API, etika, usability, deployment
│   └── screenshots/            # 8 halaman × 4 ukuran layar (dihasilkan e2e)
├── tests/e2e/                  # Playwright: Tugas 1–5 + visual QA
├── docker-compose.yml
├── playwright.config.ts
├── .env.example
└── README.md
```

---

## Fitur MVP

1. Login demo dan tiga role (admin/analyst/viewer).
2. Pencarian global dengan operator `AND`, `OR`, `-kata`, dan frasa berkutip.
3. **Overview** — KPI, volume harian, puncak percakapan, isu yang perlu perhatian.
4. **Analisis Tren** — granularitas harian/mingguan, perbandingan periode, breakdown.
5. **Eksplorasi Topik** — kartu topik, drill-down, kata kunci terkait.
6. **Pencarian Post** — pencarian, pengurutan relevansi/waktu/engagement, detail post.
7. **Pemantauan Tersimpan** — query tersimpan, tren 7 hari, duplikat/arsip.
8. **Laporan Insight** — alur draft → ditinjau → disetujui, ekspor PDF/CSV agregat.
9. **Data & Pengaturan** — status connector, impor CSV/JSON, kualitas data, taxonomy,
   analisis ulang, log proses, audit log, identitas dan warna merek.
10. **Metodologi & Etika** — sumber data, pengolahan, keterbatasan, landasan teori.
11. Filter global lintas halaman yang tersimpan pada URL.
12. State loading, kosong, tanpa hasil, error, izin ditolak, dan data usang.

Daftar lengkap beserta fitur lanjutan: [`docs/features.md`](docs/features.md).

---

## Perintah yang sering dipakai

| Perintah | Keterangan |
| --- | --- |
| `cd apps/api && pytest` | Unit test backend |
| `cd apps/api && python -m app.seed --reset` | Bangkitkan ulang dataset demo |
| `cd apps/api && alembic upgrade head` | Terapkan migration |
| `cd apps/api && alembic revision --autogenerate -m "pesan"` | Migration baru |
| `cd apps/web && npm run dev` | Frontend mode pengembangan |
| `cd apps/web && npm run typecheck` | Pemeriksaan tipe TypeScript (strict) |
| `cd apps/web && npm run lint` | ESLint |
| `cd apps/web && npm run test` | Unit test frontend (Vitest) |
| `cd apps/web && npm run build && npm run start` | Build lalu jalankan mode produksi |
| `npm run typecheck` (dari root) | Periksa tipe `tests/e2e` dan `playwright.config.ts` |
| `npm run e2e` (dari root) | End-to-end + visual QA |

---

## Pengujian

### Backend

```bash
cd apps/api
pytest                      # 58 pengujian: KPI, filter, relevansi, role, impor CSV
```

### Frontend

```bash
cd apps/web
npm run typecheck && npm run lint
npm run test                # 38 pengujian: filter, format, state UI, login
```

### End-to-end dan visual QA

Sekali saja, dari root:

```bash
npm install                 # @playwright/test
npm run e2e:install         # unduh Chromium
```

Backend **harus** sudah menyala dan basis datanya terisi; frontend dijalankan
otomatis oleh Playwright (`webServer` pada `playwright.config.ts` menjalankan
`npm run dev` di `apps/web`, dan memakai server yang sudah ada bila ditemukan).

```bash
cd apps/api && python -m app.seed --reset          # sekali
cd apps/api && uvicorn app.main:app --port 8000    # terminal terpisah

npm run e2e                       # dari root: seluruh 20 skenario
npm run e2e -- usability-tasks    # Tugas 1–5
npm run e2e -- accessibility      # audit axe-core + keyboard + focus trap
npm run e2e -- roles-and-data     # pembatasan peran, impor CSV, taxonomy
npm run e2e -- visual-qa          # screenshot + cek overflow
```

Skenario `tests/e2e/usability-tasks.spec.ts` persis mengikuti Tugas 1–5 pada
[`docs/usability_test.md`](docs/usability_test.md), sehingga pengujian otomatis
dan pengujian bersama pengguna memakai alur yang sama.
`tests/e2e/visual-qa.spec.ts` menyimpan 32 tangkapan layar ke
`docs/screenshots/<ukuran>/<halaman>.png` sekaligus memastikan tidak ada
overflow horizontal pada 1366×768, 1920×1080, tablet 768 px, dan mobile 390 px.

---

## Mode data: demo vs live

| | Demo | Live |
| --- | --- | --- |
| Sumber | Generator sintetis (`MockXConnector`) | `OfficialXConnector` (X API resmi) |
| Aktif bila | Bawaan | `DATA_SOURCE_MODE=live` **dan** `X_API_BEARER_TOKEN` terisi |
| Penanda UI | Badge `DATA DEMO` + watermark laporan | Badge `DATA LIVE` |

Token API hanya dibaca dari environment server dan tidak pernah dikirim ke
browser. Bila token tidak tersedia, aplikasi otomatis kembali ke mode demo tanpa
mengubah arsitektur.

### Memasukkan data nyata

Dua jalur, keduanya melewati pipeline yang sama (deduplikasi → analisis NLP →
`ingestion_runs` → audit log):

1. **Impor berkas** — tersedia tanpa biaya. Siapkan CSV/JSON dengan kolom
   `external_post_id`, `text`, `created_at_source`, tambahkan kolom
   `is_synthetic` bernilai `false` agar tidak ditandai data demo, lalu unggah di
   **Data & Pengaturan → Impor data** sebagai admin. Berkas harus berasal dari
   ekspor resmi atau dataset yang Anda punya dasar izinnya — produk ini tidak
   menyediakan scraping.
2. **X API resmi** — isi `X_API_BEARER_TOKEN` di environment server, jalankan
   ulang backend, lalu pakai **Data & Pengaturan → Tarik data dari X API**
   (atau `POST /data/fetch-live?query=...`). Endpoint pencarian resmi hanya
   menjangkau **7 hari terakhir**, maksimal 100 post per permintaan, dan
   memerlukan langganan X API berbayar. Selama token kosong, tombolnya nonaktif
   dan permintaan ditolak dengan kode 409 beserta penjelasannya.

---

## Pemecahan masalah

| Gejala | Penyebab | Tindakan |
| --- | --- | --- |
| Dashboard kosong tetapi tanpa error | Basis data belum di-seed | `cd apps/api && python -m app.seed --reset` |
| "Tidak dapat terhubung ke server" di UI | Backend belum menyala atau `NEXT_PUBLIC_API_BASE_URL` salah | Cek `curl http://localhost:8000/health`, lalu nilai di `apps/web/.env.local` |
| Permintaan diblokir CORS | Origin frontend belum terdaftar | Tambahkan ke `CORS_ORIGINS`, restart backend |
| `npm run start` gagal: *Could not find a production build* | Folder `.next` berisi artefak `npm run dev` (mis. setelah menjalankan e2e) | Jalankan `npm run build` lagi sebelum `npm run start` |
| E2E gagal di langkah pertama dengan pesan backend tidak terhubung | Backend belum menyala saat Playwright mulai | Nyalakan backend lebih dulu; frontend ditangani Playwright |
| Badge tetap `DATA DEMO` padahal ingin live | `X_API_BEARER_TOKEN` kosong atau tidak valid | Isi token di environment server, lalu restart backend |
| Port 3000/8000 sudah terpakai | Proses lama masih berjalan | Hentikan proses tersebut, atau ubah `WEB_PORT`/`API_PORT` |
| `curl http://localhost:8000/...` terasa lambat ~2 detik | Resolusi IPv6 (`::1`) gagal lebih dulu pada sebagian mesin Windows | Pakai `http://127.0.0.1:8000`; browser tidak terpengaruh |

Panduan operasional lengkap: [`docs/deployment.md`](docs/deployment.md).

---

## Dokumentasi

| Dokumen | Isi |
| --- | --- |
| [`docs/architecture.md`](docs/architecture.md) | Arsitektur sistem, alur data, keputusan teknis |
| [`docs/information_architecture.md`](docs/information_architecture.md) | Navigasi, labeling, filter, penerapan model Ellis |
| [`docs/api.md`](docs/api.md) | Referensi endpoint dan parameter |
| [`docs/design_tokens.md`](docs/design_tokens.md) | Palet, tipografi, spacing, komponen |
| [`docs/ethics.md`](docs/ethics.md) | Etika, privasi, kepatuhan, keterbatasan |
| [`docs/usability_test.md`](docs/usability_test.md) | Skrip pengujian dengan staf Recruitment/HR |
| [`docs/testing_report.md`](docs/testing_report.md) | Cakupan dan hasil pengujian |
| [`docs/screenshots/`](docs/screenshots) | Tangkapan layar 8 halaman pada 4 ukuran layar |
| [`docs/deployment.md`](docs/deployment.md) | Panduan deployment dan operasional |
| [`docs/features.md`](docs/features.md) | Fitur MVP dan roadmap lanjutan |
| [`data/data_dictionary.md`](data/data_dictionary.md) | Kamus data seluruh tabel |
