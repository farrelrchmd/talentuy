# Kamus Data TalentPulse

Seluruh tabel memakai primary key `id` bertipe `String(36)` berisi UUID4.
Kolom waktu disimpan sebagai UTC naive (`DateTime`).

## users

Pengguna dashboard (bukan subjek data).

| Kolom | Tipe | Keterangan |
| --- | --- | --- |
| `id` | String(36) | UUID |
| `name` | String(120) | Nama tampilan |
| `email` | String(255), unik, indeks | Identitas login |
| `password_hash` | String(255) | bcrypt |
| `role` | String(20) | `admin`, `analyst`, `viewer` |
| `is_active` | Boolean | Akun nonaktif tidak dapat login |
| `created_at` | DateTime | |

## topics

Taxonomy topik percakapan; dapat dikelola admin.

| Kolom | Tipe | Keterangan |
| --- | --- | --- |
| `slug` | String(80), unik | Contoh `gaji-benefit` |
| `name` | String(160) | Label antarmuka |
| `description` | Text | Penjelasan cakupan topik |
| `color` | String(9) | Hex; konsisten antar grafik |
| `keywords` | JSON (list) | Kata kunci penentu klasifikasi |
| `is_active` | Boolean | Topik nonaktif tidak dipakai klasifikasi baru |

Sepuluh topik awal: `gaji-benefit`, `kontrak-status`, `lokasi-penempatan`,
`shift-jam-kerja`, `persyaratan-pendidikan`, `pengalaman-keahlian`,
`proses-melamar`, `keamanan-penipuan`, `pengalaman-kandidat`,
`reputasi-perusahaan`.

## source_queries

Definisi query yang dapat disimpan dan dipakai ulang.

| Kolom | Tipe | Keterangan |
| --- | --- | --- |
| `name` | String(160) | Nama query |
| `query_text` | Text | Ekspresi pencarian mentah |
| `include_keywords` | JSON (list) | Kata kunci yang harus ada (OR) |
| `exclude_keywords` | JSON (list) | Kata kunci yang mengecualikan |
| `job_roles`, `topics`, `sentiments`, `intents` | JSON (list) | Filter tersimpan |
| `created_by` | FK users | Pemilik |
| `is_saved`, `is_archived` | Boolean | Status penyimpanan |
| `created_at`, `updated_at` | DateTime | |

## posts

Post publik atau sintetis. Tidak menyimpan atribut sensitif maupun identitas
personal yang dapat langsung mengidentifikasi seseorang.

| Kolom | Tipe | Keterangan |
| --- | --- | --- |
| `external_post_id` | String(80), unik, indeks | ID post pada sumber; kunci deduplikasi |
| `source` | String(20) | `demo`, `x_api`, `import` |
| `text` | Text | Isi post |
| `created_at_source` | DateTime, indeks | Waktu publikasi di sumber |
| `language` | String(8) | `id`, `en` |
| `author_public_id` | String(80), nullable | ID publik; **tidak ditampilkan di UI** |
| `like_count`, `repost_count`, `reply_count`, `quote_count` | Integer | Metrik interaksi |
| `url` | String(400), nullable | Tautan post |
| `is_synthetic` | Boolean | `true` untuk data demo |
| `ingested_at` | DateTime | Waktu masuk sistem |
| `deleted_at` | DateTime, nullable, indeks | Soft delete; dikecualikan seluruh query |

Indeks gabungan: `ix_posts_source_created (source, created_at_source)`.

## post_analysis

Hasil pipeline NLP; satu baris per post.

| Kolom | Tipe | Keterangan |
| --- | --- | --- |
| `post_id` | FK posts, unik, cascade | |
| `normalized_text` | Text | Teks ternormalisasi; target pencarian |
| `sentiment_label` | String(20), indeks | `Positif`, `Netral`, `Negatif`, `Tidak Yakin` |
| `sentiment_confidence` | Float | 0–1; 1.0 bila dikoreksi manusia |
| `intent_label` | String(40), indeks | `Pertanyaan`, `Keluhan`, `Pengalaman`, `Informasi Lowongan`, `Promosi`, `Peringatan Penipuan` |
| `intent_confidence` | Float | 0–1 |
| `topic_id` | FK topics, nullable, indeks | `null` = belum masuk topik |
| `job_role` | String(60), indeks | Salah satu jenis pekerjaan taxonomy |
| `relevance_score` | Float | Relevansi terhadap konteks rekrutmen |
| `engagement_score` | Float, indeks | `like×1 + repost×2 + reply×1,5 + quote×1,5` |
| `keywords` | JSON (list) | Kata kunci hasil ekstraksi |
| `model_version` | String(40) | Contoh `baseline-1.0.0`, `baseline-1.0.0+koreksi-manual` |
| `analyzed_at` | DateTime | |
| `needs_review` | Boolean | Keyakinan rendah → perlu tinjauan manusia |
| `corrected_by` | FK users, nullable | Admin yang mengoreksi label |

Indeks gabungan: `ix_analysis_topic_sentiment`, `ix_analysis_role_intent`.

## monitors

Pemantauan tersimpan atas sebuah `source_query`.

| Kolom | Tipe | Keterangan |
| --- | --- | --- |
| `name` | String(160) | Nama monitor |
| `source_query_id` | FK source_queries, cascade | Definisi filter |
| `owner_id` | FK users, nullable | Pemilik |
| `comparison_window` | Integer | 7, 14, atau 30 hari |
| `is_active`, `is_archived` | Boolean | |
| `created_at` | DateTime | |

Nilai `current_count`, `previous_count`, `change_percent`, `trend_direction`, dan
`sparkline` dihitung saat permintaan, tidak disimpan.

## insights

Temuan yang selalu melewati peninjauan manusia.

| Kolom | Tipe | Keterangan |
| --- | --- | --- |
| `title` | String(240) | |
| `summary` | Text | Ringkasan (template atau tulisan manusia) |
| `human_note` | Text | Catatan peninjau; ikut tercetak pada laporan |
| `evidence_filters` | JSON (dict) | Filter yang menghasilkan temuan |
| `metric_snapshot` | JSON (dict) | Angka pendukung saat insight dibuat |
| `created_by` | FK users, nullable | |
| `human_status` | String(20) | `draft` → `reviewed` → `approved` |
| `is_synthetic_data` | Boolean | `true` bila dibuat saat mode demo |
| `created_at`, `updated_at` | DateTime | |

## reports

Laporan yang menggabungkan insight dan grafik agregat.

| Kolom | Tipe | Keterangan |
| --- | --- | --- |
| `title` | String(240) | |
| `period_start`, `period_end` | DateTime | Periode laporan |
| `query_snapshot` | JSON (dict) | Filter saat laporan disusun |
| `insight_ids` | JSON (list) | Insight yang disertakan |
| `charts` | JSON (list) | `volume`, `topics`, `sentiment`, `job_roles`, `intents` (maks. 6) |
| `notes` | Text | Catatan laporan |
| `created_by` | FK users, nullable | |
| `generated_at` | DateTime | |

## ingestion_runs

Riwayat proses data yang ditampilkan sebagai "Log proses data".

| Kolom | Tipe | Keterangan |
| --- | --- | --- |
| `source` | String(30) | `demo`, `import`, `reanalysis`, `x_api` |
| `started_at`, `completed_at` | DateTime | |
| `records_received` | Integer | Baris diterima |
| `records_processed` | Integer | Baris berhasil |
| `records_failed` | Integer | Baris gagal validasi |
| `status` | String(20) | `running`, `success`, `partial`, `failed` |
| `error_summary` | Text | Ringkasan kesalahan yang mudah dibaca |
| `triggered_by` | FK users, nullable | |

## audit_logs

Jejak perubahan untuk kepatuhan.

| Kolom | Tipe | Keterangan |
| --- | --- | --- |
| `actor_id` | FK users, nullable | |
| `actor_email` | String(255) | Disimpan terpisah agar tetap terbaca setelah reset |
| `action` | String(80), indeks | `data.import`, `data.seed`, `data.reanalyze`, `taxonomy.update`, `label.correct`, `insight.*`, `report.*` |
| `entity`, `entity_id` | String(80) | Objek yang terpengaruh |
| `detail` | JSON (dict) | Ringkasan perubahan |
| `created_at` | DateTime, indeks | |

## usability_events

Log pengujian usability yang privacy-preserving.

| Kolom | Tipe | Keterangan |
| --- | --- | --- |
| `session_key` | String(64), indeks | Kunci sesi anonim |
| `task_code` | String(40) | Kode tugas pengujian |
| `event_type` | String(40) | Contoh `task_start`, `task_complete` |
| `step_count` | Integer | Jumlah langkah navigasi |
| `duration_ms` | Integer | Durasi tugas |
| `filter_keys` | JSON (list) | **Nama** filter yang dipakai, bukan nilainya |
| `created_at` | DateTime | |

## Enumerasi

| Enumerasi | Nilai |
| --- | --- |
| Role | `admin`, `analyst`, `viewer` |
| Sentimen | `Positif`, `Netral`, `Negatif`, `Tidak Yakin` |
| Intent | `Pertanyaan`, `Keluhan`, `Pengalaman`, `Informasi Lowongan`, `Promosi`, `Peringatan Penipuan` |
| Jenis pekerjaan | `Sales Promotion Girl/Boy`, `Merchandiser`, `Admin`, `Staf Gudang`, `Operator`, `Security`, `Cleaning Service`, `Driver`, `Supervisor Lapangan`, `Lainnya` |
| Status insight | `draft`, `reviewed`, `approved` |
| Status ingestion | `running`, `success`, `partial`, `failed` |
| Bahasa | `id`, `en` |

## Format impor

Kolom wajib: `external_post_id`, `text`, `created_at_source`.
Kolom opsional: `like_count`, `repost_count`, `reply_count`, `quote_count`,
`language`, `url`.

Format tanggal yang dikenali: ISO 8601 (`2026-08-29T10:15:00`), `YYYY-MM-DD HH:MM:SS`,
`YYYY-MM-DD`, dan `DD/MM/YYYY`. Baris dengan `external_post_id` yang sudah ada
akan dilewati, bukan digandakan. Contoh berkas: `data/synthetic/contoh_impor.csv`.
