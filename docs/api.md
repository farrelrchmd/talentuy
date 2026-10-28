# API TalentPulse

Base URL pengembangan: `http://localhost:8000`
Dokumentasi interaktif: `/docs` (Swagger) dan `/redoc`. Skema OpenAPI: `/openapi.json`.

## 1. Autentikasi

Seluruh endpoint kecuali `/health`, `/methodology`, dan `/auth/*` memerlukan
header `Authorization: Bearer <token>`. Token JWT diperoleh dari `/auth/login`
dan berlaku 12 jam (`JWT_EXPIRE_MINUTES`).

| Method | Path | Role | Keterangan |
| --- | --- | --- | --- |
| POST | `/auth/login` | – | Body `{ "email", "password" }` → `{ access_token, user }` |
| GET | `/auth/me` | viewer+ | Profil pengguna aktif |
| GET | `/auth/demo-accounts` | – | Daftar akun demo (hanya mode development) |

Hierarki role: `viewer < analyst < admin`.

## 2. Filter global

Endpoint analitik menerima parameter berikut. Semua bersifat opsional; bila
`date_from`/`date_to` kosong dipakai 30 hari terakhir.

| Parameter | Tipe | Catatan |
| --- | --- | --- |
| `date_from`, `date_to` | ISO 8601 | Dinormalisasi ke awal/akhir hari |
| `query_id` | string | ID query tersimpan; filternya digabung dengan filter aktif |
| `job_roles` | string (berulang) | Contoh `?job_roles=Admin&job_roles=Driver` |
| `topics` | string (berulang) | Slug topik |
| `sentiments` | string (berulang) | `Positif`, `Netral`, `Negatif`, `Tidak Yakin` |
| `intents` | string (berulang) | Kategori intent |
| `languages` | string (berulang) | `id`, `en` |
| `min_engagement`, `max_engagement` | float ≥ 0 | Rentang skor interaksi |
| `q` | string | Operator `AND`, `OR`, `-kata`, frasa berkutip |

Setiap response analitik memuat blok `meta`:

```json
{
  "record_count": 412,
  "period_start": "2026-07-31T00:00:00",
  "period_end": "2026-08-29T23:59:59",
  "period_label": "31 Jul – 29 Agu 2026",
  "comparison_start": "2026-07-01T00:00:00",
  "comparison_end": "2026-07-30T23:59:59",
  "data_source_mode": "demo",
  "is_synthetic": true,
  "last_updated": "2026-08-29T02:10:00",
  "is_stale": false,
  "model_version": "baseline-1.0.0",
  "search_provider": "sqlite-like",
  "applied_filters": { "topics": ["gaji-benefit"] }
}
```

## 3. Dashboard

| Method | Path | Role | Isi |
| --- | --- | --- | --- |
| GET | `/dashboard/overview` | viewer+ | KPI, deret volume, puncak, topik, sentimen per pekerjaan, heatmap, isu perhatian, pertanyaan teratas, keterbatasan |
| GET | `/dashboard/trends` | viewer+ | `granularity=daily\|weekly`, `breakdown=topic\|job_role\|sentiment\|none` |
| GET | `/dashboard/topics` | viewer+ | Ringkasan seluruh topik + `partitions` (kombinasi kategori isu × jenis pekerjaan: jumlah, porsi, pertanyaan, porsi negatif) + kata kunci terkait + pertanyaan |
| GET | `/dashboard/topics/{slug}` | viewer+ | Detail satu topik: deret, sentimen, intent, pekerjaan, ringkasan usulan |
| GET | `/dashboard/heatmap` | viewer+ | Matriks jenis pekerjaan × topik kekhawatiran |
| GET | `/dashboard/questions` | viewer+ | Post ber-intent Pertanyaan (parameter `limit`) |
| GET | `/dashboard/keywords` | viewer+ | Jaringan kata kunci terkait (parameter `limit`) |
| GET | `/dashboard/insight-suggestions` | viewer+ | Draft insight berbasis template; wajib ditinjau manusia |

## 4. Post

| Method | Path | Role | Keterangan |
| --- | --- | --- | --- |
| GET | `/posts` | viewer+ | `sort=relevance\|recent\|engagement`, `page`, `page_size` (5–100) |
| GET | `/posts/{post_id}` | viewer+ | Detail satu post |
| PATCH | `/posts/{post_id}/labels` | admin | Koreksi label manual (human-in-the-loop); nilai label divalidasi terhadap taxonomy |
| POST | `/posts/{post_id}/label-suggestions` | analyst+ | Usulan koreksi `{ "field", "suggested_label", "note" }`; menandai post `needs_review` dan mencatat audit `label.suggest` |

Setiap post memuat `explanation`, yaitu dasar klasifikasi untuk keempat label
(`topic`, `sentiment`, `intent`, `job_role`):

```json
{
  "rule": "Kata kunci taxonomy topik \"Gaji dan Benefit\" paling banyak cocok (2 kata). ...",
  "triggers": ["gaji", "umr"],
  "corrected": false,
  "auto_rule": ""
}
```

Kata pemicu dicocokkan pada teks ternormalisasi, sehingga sebagian (mis. hasil
ekspansi slang) tidak muncul persis pada teks asli. Saat admin mengoreksi label,
`corrected` menjadi `true`, `rule` menyebut label sebelumnya, dan aturan otomatis
semula disimpan di `auto_rule`. Post yang dianalisis sebelum kolom ini ada
mengembalikan objek kosong sampai analisis ulang dijalankan.

Nilai keyakinan model hanya dikirim untuk role analyst dan admin. Respons tidak
pernah memuat identitas personal penulis; hanya `external_post_id` dan tautan.

## 5. Query dan monitor

| Method | Path | Role |
| --- | --- | --- |
| GET/POST | `/queries` | viewer+ / analyst+ |
| PATCH/DELETE | `/queries/{id}` | analyst+ |
| GET/POST | `/monitors` | viewer+ / analyst+ |
| PATCH | `/monitors/{id}` | analyst+ |
| POST | `/monitors/{id}/duplicate` | analyst+ |

Response monitor memuat `current_count`, `previous_count`, `change_percent`,
`trend_direction`, dan `sparkline` yang dihitung ulang setiap permintaan —
bukan aliran data real-time.

## 6. Insight dan laporan

| Method | Path | Role | Keterangan |
| --- | --- | --- | --- |
| GET | `/insights` | viewer+ | Filter opsional `status=draft\|reviewed\|approved` |
| POST | `/insights` | analyst+ | Insight baru selalu berstatus draft bila tidak ditentukan |
| PATCH | `/insights/{id}` | analyst+ | Analyst hanya boleh mengubah miliknya sendiri |
| DELETE | `/insights/{id}` | analyst+ | |
| GET/POST | `/reports` | viewer+ / analyst+ | `charts` maksimal 6 kunci |
| GET | `/reports/{id}` | viewer+ | |
| GET | `/reports/{id}/preview` | viewer+ | Isi laporan tanpa mengunduh berkas |
| GET | `/reports/{id}/export?format=pdf\|csv\|posts` | viewer+ | `posts` hanya berisi Post ID, waktu, topik, pekerjaan, dan tautan |
| DELETE | `/reports/{id}` | analyst+ | |

Kunci grafik yang tersedia: `volume`, `topics`, `sentiment`, `job_roles`,
`intents`. Seluruh ekspor pada mode demo memuat watermark
`DATA SINTETIS — BUKAN TEMUAN AKTUAL`.

## 7. Data dan pengaturan

| Method | Path | Role | Keterangan |
| --- | --- | --- | --- |
| GET | `/data/connectors` | viewer+ | Status connector dan mode data efektif |
| GET | `/data/taxonomy` | viewer+ | Topik, jenis pekerjaan (+ `job_role_codes`), intent, sentimen, bahasa, rumus engagement |
| PATCH | `/data/topics/{id}` | admin | Ubah nama, deskripsi, warna, kata kunci, status aktif |
| GET | `/data/keyword-presets` | viewer+ | Preset kata kunci per kategori isu (termasuk yang nonaktif) |
| POST | `/data/keyword-presets` | admin | `{ topic_slug, label, query_text, sort_order, is_active }` |
| PATCH/DELETE | `/data/keyword-presets/{id}` | admin | Ubah atau hapus preset; tercatat di audit log |
| GET | `/data/quality` | viewer+ | Cakupan analisis, porsi belum terklasifikasi, perlu ditinjau |
| POST | `/data/import` | admin | `multipart/form-data` berisi `file` (CSV/JSON, maks. 8 MB) |
| POST | `/data/import-public-x` | admin | Impor satu post X publik dari body JSON `{ "url": "https://x.com/.../status/..." }` |
| POST | `/data/fetch-live` | admin | Tarik post nyata via X API resmi: `query` (wajib), `days` (1–7), `max_results` (10–100) |
| POST | `/data/seed` | admin | `count` (100–5000), `days` (7–365), `reset` |
| POST | `/data/reanalyze` | admin | Jalankan ulang pipeline NLP untuk seluruh post |
| GET | `/data/runs` | viewer+ | Riwayat proses data (`limit` 1–100) |
| GET | `/data/audit` | admin | Audit log (`limit` 1–200) |

`/data/fetch-live` menjalankan `OfficialXApiConnector` di server lalu memasukkan
hasilnya lewat pipeline yang sama dengan impor (deduplikasi `external_post_id`,
analisis NLP, catatan `ingestion_runs`, audit `data.fetch_live`). Post yang masuk
ditandai `is_synthetic = false` dan `source = "x_api"`. Endpoint menolak dengan:

- **409** bila `X_API_BEARER_TOKEN` belum tersedia di environment server;
- **503** bila X API menolak permintaan atau query kosong.

Catatan: endpoint pencarian resmi yang dipakai (`tweets/search/recent`) hanya
menjangkau 7 hari terakhir dan maksimal 100 post per permintaan.

Kolom wajib berkas impor: `external_post_id`, `text`, `created_at_source`.
Kolom opsional: `like_count`, `repost_count`, `reply_count`, `quote_count`,
`language`, `url`. Contoh berkas: `data/synthetic/contoh_impor.csv`.

## 8. Sistem

| Method | Path | Role | Keterangan |
| --- | --- | --- | --- |
| GET | `/health` | – | Status database, mode data, jumlah post, versi |
| GET | `/methodology` | – | Sumber data, pengolahan, etika, keterbatasan, kesegaran |
| POST | `/usability/events` | viewer+ | Log alur pengujian (tanpa isi pencarian) |
| GET | `/usability/summary` | admin | Agregat durasi dan jumlah langkah per tugas |

## 9. Penanganan error

| Status | Bentuk | Contoh pesan |
| --- | --- | --- |
| 401 | `{"detail": "..."}` | Sesi berakhir — token kedaluwarsa atau tidak valid |
| 403 | `{"detail": "..."}` | Role tidak mencukupi |
| 404 | `{"detail": "..."}` | Entitas tidak ditemukan |
| 413 | `{"detail": "Ukuran berkas melebihi 8 MB."}` | Impor terlalu besar |
| 422 | `{"detail": "...", "errors": [{"field": "...", "message": "..."}]}` | Validasi parameter/berkas |
| 500 | `{"detail": "Terjadi kesalahan pada server. Coba muat ulang halaman."}` | Kesalahan tak tertangani |

Seluruh pesan error ditulis dalam Bahasa Indonesia dan aman ditampilkan kepada
pengguna akhir.
