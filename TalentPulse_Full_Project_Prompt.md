# FULL PROJECT PROMPT — TALENTPULSE

> Salin atau attach seluruh file ini ke AI coding agent. Bangun proyek secara utuh, bukan hanya mockup statis. Jangan menunggu klarifikasi untuk keputusan kecil; gunakan default yang ditentukan dalam dokumen ini. Jika ada keterbatasan layanan eksternal, selesaikan seluruh aplikasi memakai mode demo dan sediakan abstraction layer untuk integrasi produksi.

---

## 1. Peran dan Mandat

Anda adalah tim gabungan yang terdiri dari product designer, UX researcher, information architect, data analyst, NLP engineer, full-stack engineer, QA engineer, dan technical writer.

Tugas Anda adalah merancang dan membangun **TalentPulse**, sebuah dashboard web internal yang membantu tim Recruitment/HR PT Siprama Cakrawala mengeksplorasi percakapan publik pencari kerja di media sosial X untuk mendukung komunikasi rekrutmen yang lebih jelas, relevan, dan responsif.

Bangun produk sebagai prototipe tugas akhir berbasis karya yang:

- benar-benar dapat dijalankan;
- memiliki kualitas visual setara produk industri;
- desktop-first tetapi tetap responsif;
- menggunakan Bahasa Indonesia untuk seluruh antarmuka;
- memiliki data demo yang realistis tetapi sepenuhnya sintetis;
- siap dihubungkan ke X API resmi tanpa mengubah arsitektur utama;
- menunjukkan penerapan teori Sains Informasi dalam fitur dan alur pengguna;
- dapat digunakan untuk usability testing dengan staf Recruitment/HR;
- tidak mengklaim afiliasi resmi dengan X;
- tidak menggunakan data pribadi atau post nyata tanpa dasar izin yang sesuai.

---

## 2. Nama Produk dan Judul Akademis

### Nama produk

**TalentPulse**

### Tagline

**Dengar percakapan kandidat. Perjelas komunikasi rekrutmen.**

### Judul tugas akhir sementara

**Perancangan TalentPulse sebagai Dashboard Interaktif Eksplorasi Percakapan Pencari Kerja pada Media Sosial X untuk Mendukung Komunikasi Rekrutmen PT Siprama Cakrawala**

Judul dan identitas PT Siprama Cakrawala harus diperlakukan sebagai konfigurasi yang dapat diubah. Jangan menampilkan logo perusahaan sebelum aset dan persetujuan resmi tersedia. Gunakan placeholder identitas teks selama pengembangan.

---

## 3. Latar Belakang dan Masalah

PT Siprama Cakrawala bergerak pada penyediaan dan pengelolaan tenaga alih daya untuk beragam posisi, seperti sales promotion, merchandiser, staf gudang, admin, operator, keamanan, cleaning service, dan driver.

Hipotesis masalah yang perlu divalidasi melalui wawancara mitra:

1. Percakapan pencari kerja mengenai lowongan, proses melamar, kontrak, gaji, lokasi penempatan, sistem shift, dan penipuan lowongan tersebar di media sosial.
2. Tim rekrutmen membutuhkan waktu untuk menemukan isu dan pertanyaan yang relevan secara manual.
3. Informasi yang tersebar sulit dibandingkan berdasarkan waktu, jenis pekerjaan, sentimen, atau kategori kekhawatiran.
4. Tim rekrutmen belum memiliki tampilan terpadu untuk mengubah percakapan publik menjadi bahan FAQ, konten edukasi, dan perbaikan komunikasi lowongan.

TalentPulse tidak boleh mengklaim dapat menentukan keputusan penerimaan kandidat. Produk ini hanya menjadi **media informasi pendukung komunikasi rekrutmen**, bukan sistem seleksi, profiling, scoring kandidat, atau pengambilan keputusan ketenagakerjaan otomatis.

---

## 4. Tujuan Produk

TalentPulse harus memungkinkan pengguna untuk:

1. mencari percakapan publik berdasarkan kata kunci rekrutmen;
2. melihat perubahan volume percakapan dari waktu ke waktu;
3. mengidentifikasi topik, pertanyaan, dan kekhawatiran yang sering muncul;
4. membandingkan percakapan berdasarkan jenis pekerjaan, topik, periode, dan sentimen;
5. menemukan post yang paling relevan sebagai konteks, bukan sebagai dasar profiling individu;
6. menyimpan query monitoring;
7. menghasilkan ringkasan insight yang dapat ditinjau manusia;
8. mengekspor laporan agregat untuk kebutuhan internal;
9. mengurangi waktu dan jumlah langkah pencarian dibandingkan pencarian manual.

---

## 5. Pengguna, Stakeholder, dan Subjek Data

### Pengguna utama

- staf Recruitment;
- staf HR;
- Recruitment Marketing;
- Employer Branding;
- Social Media atau Corporate Communication yang mendukung rekrutmen.

### Stakeholder utama

- PT Siprama Cakrawala sebagai mitra;
- pimpinan atau supervisor Recruitment/HR;
- peneliti/mahasiswa sebagai perancang produk.

### Penerima manfaat tidak langsung

Pencari kerja yang memperoleh informasi lowongan, proses melamar, dan FAQ yang lebih jelas.

### Subjek data

Pengguna X yang membuat post publik. Mereka **bukan pengguna dashboard** dan tidak boleh diprofilkan, diberi skor kelayakan kerja, atau diklasifikasikan berdasarkan atribut sensitif.

### Persona utama

**Nama:** Rani Prameswari  
**Peran:** Recruitment Communication Officer  
**Tujuan:** Menemukan isu dan pertanyaan pencari kerja untuk menyusun komunikasi lowongan dan konten edukasi.  
**Kendala:** Informasi tersebar, pencarian manual memakan waktu, sulit membandingkan tren, dan sulit mengetahui konteks di balik lonjakan percakapan.  
**Perangkat:** Laptop kantor, resolusi utama 1366×768 dan 1920×1080.  
**Kemampuan teknis:** Menengah; memahami dashboard tetapi bukan data scientist.

---

## 6. Landasan Sains Informasi

Teori harus terlihat dalam desain fitur, user flow, dan evaluasi. Jangan hanya menuliskannya di halaman “Tentang”.

### 6.1 Ellis’s Information-Seeking Behaviour Model

| Tahap Ellis | Kebutuhan pengguna | Implementasi fitur |
|---|---|---|
| Starting | Memulai pencarian tanpa query kompleks | Preset topik, contoh query, dan pencarian terpandu |
| Chaining | Mengikuti petunjuk menuju informasi lain | Hashtag, kata kunci, topik, dan jenis pekerjaan terkait yang dapat diklik |
| Browsing | Menjelajah informasi secara luas | Overview, grafik tren, topic cards, dan tampilan eksplorasi |
| Differentiating | Memilah informasi yang paling relevan | Filter tanggal, pekerjaan, topik, sentimen, engagement, dan relevansi |
| Monitoring | Mengikuti perubahan isu tertentu | Saved query, perbandingan periode, dan indikator perubahan tren |
| Extracting | Mengambil informasi untuk digunakan | Detail post, ringkasan insight, catatan, dan ekspor laporan agregat |

### 6.2 Information Foraging Theory

| Konsep | Penerapan dalam antarmuka |
|---|---|
| Information scent | Label jelas, cuplikan teks, jumlah post, perubahan persentase, dan indikator sentimen |
| Information patch | Percakapan dikelompokkan menjadi topik, pekerjaan, dan periode |
| Cost of information | Cross-filter, drill-down, pencarian cepat, dan sedikit perpindahan halaman |
| Value of information | Topik dan post diberi prioritas berdasarkan relevansi, volume, serta momentum |
| Navigation between patches | Pengguna berpindah dari grafik ke topik, kemudian ke post dan insight tanpa kehilangan filter |

### 6.3 Konsep teknis pendukung

Konsep berikut mendukung sistem, tetapi bukan teori utama:

- Information Retrieval untuk indexing, pencarian, filtering, dan ranking;
- Information Architecture untuk organization, labeling, navigation, dan search system;
- topic classification/topic modeling untuk pengelompokan percakapan;
- sentiment analysis untuk konteks eksplorasi;
- interactive data visualization untuk sensemaking;
- human-in-the-loop untuk verifikasi insight.

---

## 7. Ruang Lingkup MVP

### Wajib tersedia

1. Login demo dan role dasar.
2. Global search dan query builder.
3. Dashboard Overview.
4. Trend Analysis.
5. Topic Explorer.
6. Post Explorer.
7. Related Keywords.
8. Saved Monitoring.
9. Insight Report.
10. Data Import dan pengaturan sumber data.
11. Dataset demo sintetis.
12. Responsive layout.
13. Empty, loading, error, dan no-result states.
14. README, dokumentasi setup, dan pengujian dasar.

### Fitur tambahan setelah MVP stabil

- semantic search;
- alert terjadwal;
- perbandingan kompetitor;
- summarization dengan LLM;
- integrasi single sign-on;
- notifikasi email/Telegram;
- live streaming data.

Jangan mengerjakan fitur tambahan sebelum seluruh fitur wajib selesai dan dapat digunakan.

---

## 8. Information Architecture

### Navigasi utama

1. **Overview**
2. **Analisis Tren**
3. **Eksplorasi Topik**
4. **Pencarian Post**
5. **Monitoring**
6. **Laporan Insight**
7. **Data & Pengaturan**

### Navigasi global

- logo teks TalentPulse;
- global command search;
- rentang tanggal aktif;
- status sumber data: Demo atau Live;
- tombol reset filter;
- menu profil pengguna;
- bantuan singkat mengenai cara membaca dashboard.

### Prinsip navigasi

- filter global bertahan ketika pengguna berpindah halaman;
- setiap grafik mendukung klik untuk cross-filter;
- filter aktif selalu terlihat sebagai chips;
- tersedia “Hapus semua filter”;
- browser back tidak menghilangkan konteks;
- URL menyimpan state filter penting agar tampilan dapat dibagikan secara internal;
- setiap drill-down memiliki breadcrumb atau tombol kembali yang jelas.

---

## 9. User Flow Utama

### Flow A — Menemukan isu rekrutmen

1. Pengguna login.
2. Pengguna memilih preset “Kerja Outsourcing” atau mengetik query.
3. Pengguna menentukan periode 30 hari.
4. Overview menampilkan KPI dan perubahan tren.
5. Pengguna mengeklik topik yang meningkat.
6. Topic Explorer menampilkan subtopik, sentimen, dan kata terkait.
7. Pengguna membuka Post Explorer untuk melihat konteks.
8. Pengguna menandai insight yang relevan.
9. Pengguna membuat laporan agregat.

### Flow B — Menjawab pertanyaan bisnis

Pertanyaan contoh:

> “Apa tiga pertanyaan yang paling sering muncul mengenai pekerjaan gudang dalam 30 hari terakhir?”

1. Pilih pekerjaan “Staf Gudang”.
2. Pilih kategori “Pertanyaan Kandidat”.
3. Urutkan topik berdasarkan volume.
4. Periksa post representatif.
5. Simpan tiga insight.
6. Ekspor ringkasan sebagai PDF/CSV agregat.

### Flow C — Monitoring

1. Buat query baru.
2. Beri nama monitor.
3. Simpan keyword dan filter.
4. Bandingkan 7 hari terakhir dengan 7 hari sebelumnya.
5. Tampilkan indikator naik, turun, atau stabil.

---

## 10. Spesifikasi Halaman

### 10.1 Login

- sederhana dan profesional;
- akun demo tersedia dari seed;
- tampilkan informasi bahwa aplikasi adalah prototipe internal;
- jangan menggunakan logo X sebagai identitas produk;
- dukung show/hide password dan validasi error.

### 10.2 Overview

#### Header

- judul: “Ringkasan Percakapan Kandidat”;
- subjudul dinamis yang menyebut query dan periode aktif;
- badge jelas: `DATA DEMO` atau `DATA LIVE`;
- last updated timestamp.

#### KPI cards

- Total Post;
- Perubahan Volume;
- Topik Aktif;
- Sentimen Dominan;
- Pertanyaan Terdeteksi;
- Jenis Pekerjaan Teratas.

Setiap KPI memiliki tooltip definisi, perbandingan periode, dan aksi drill-down.

#### Visualisasi

1. Area/line chart volume percakapan harian.
2. Horizontal bar chart topik terbanyak.
3. Stacked bar sentimen berdasarkan jenis pekerjaan.
4. Heatmap jenis pekerjaan × kategori kekhawatiran.
5. Daftar “Isu yang Perlu Diperhatikan”.
6. Daftar pertanyaan kandidat teratas.

#### Interaksi

- klik titik lonjakan untuk membuka detail tanggal;
- klik bar topik untuk menerapkan filter;
- klik sel heatmap untuk membuka Post Explorer;
- hover menampilkan angka, definisi, dan perubahan.

### 10.3 Analisis Tren

- perbandingan periode;
- granularitas harian/mingguan;
- breakdown berdasarkan pekerjaan, topik, dan sentimen;
- anotasi otomatis pada lonjakan terbesar;
- tabel peak events;
- toggle absolute count vs indexed change;
- jangan membuat klaim kausalitas otomatis.

### 10.4 Eksplorasi Topik

- ranked topic list;
- topic cards berisi volume, perubahan, sentimen, dan kata terkait;
- topic detail drawer;
- related keyword network sederhana dan dapat dibaca;
- daftar pertanyaan populer;
- contoh post representatif;
- kemampuan menggabungkan atau mengubah label topik hanya untuk admin;
- topic labels harus human-readable dalam Bahasa Indonesia.

Kategori awal:

1. Gaji dan Benefit
2. Kontrak dan Status Kerja
3. Lokasi dan Penempatan
4. Sistem Shift dan Jam Kerja
5. Persyaratan Pendidikan
6. Pengalaman dan Keahlian
7. Proses Melamar
8. Keamanan dan Penipuan Lowongan
9. Pengalaman Kandidat
10. Reputasi Perusahaan Outsourcing

### 10.5 Pencarian Post

- search input dengan boolean sederhana: AND, OR, exclude;
- filters: tanggal, pekerjaan, topik, sentimen, engagement, dan bahasa;
- sort: relevansi, terbaru, engagement tertinggi;
- hasil berbentuk list/table yang nyaman dibaca;
- highlight kata yang cocok;
- relevance score dijelaskan sebagai skor pencarian, bukan skor pengguna;
- detail drawer menampilkan teks, metadata publik minimum, label analisis, dan link ke post asli;
- jangan menampilkan informasi sensitif atau inferensi demografi;
- pagination atau virtualized list;
- state no-result memberi saran memperluas query.

### 10.6 Monitoring

- daftar query tersimpan;
- nama monitor, pemilik, keyword, filter, tanggal dibuat;
- tren 7 hari dan perubahan dibanding periode sebelumnya;
- quick open;
- duplicate, edit, archive;
- alert hanya berupa simulasi pada mode demo;
- jangan menyatakan real-time jika tidak memakai koneksi live.

### 10.7 Laporan Insight

- pengguna memilih insight dari dashboard;
- pengguna dapat menambahkan catatan manusia;
- laporan memuat periode, query, metodologi singkat, statistik agregat, grafik terpilih, dan disclaimer;
- rekomendasi diberi label “Rekomendasi untuk Ditinjau”;
- ekspor PDF dan CSV agregat;
- export post-level hanya berupa Post ID dan link bila diperbolehkan;
- semua laporan mode demo memiliki watermark `DATA SINTETIS — BUKAN TEMUAN AKTUAL`.

### 10.8 Data & Pengaturan

- status connector;
- import CSV/JSON;
- data quality summary;
- daftar keyword pekerjaan;
- taxonomy topik;
- kamus sentimen/domain terms;
- tombol re-run analysis;
- log proses yang mudah dipahami;
- pengaturan identitas perusahaan dan warna merek;
- jangan pernah menampilkan API secret di browser.

---

## 11. Sistem Filter Global

Filter global minimal:

- date range;
- query/monitor;
- jenis pekerjaan;
- topik;
- sentimen;
- kategori intent: pertanyaan, keluhan, pengalaman, informasi, promosi;
- engagement range;
- bahasa.

Perilaku filter:

- cross-filter seluruh komponen;
- debounced update;
- tampilkan jumlah hasil;
- dapat di-reset;
- dapat disimpan sebagai query;
- hindari refresh penuh halaman;
- simpan filter penting pada URL query parameters.

---

## 12. Sistem Visual dan UI

### Arah visual

Gunakan gaya **modern HR intelligence platform**: profesional, tenang, data-rich, tetapi tidak terasa seperti template admin generik. Prioritaskan hierarchy, whitespace, keterbacaan angka, dan interaksi eksplorasi.

### Palet awal

- Background utama: `#F6F8FC`
- Surface: `#FFFFFF`
- Sidebar/navy: `#0B1220`
- Primary/cobalt: `#2563EB`
- Secondary/cyan: `#06B6D4`
- Text utama: `#111827`
- Text sekunder: `#667085`
- Border: `#E4E7EC`
- Positive: `#16A34A`
- Warning: `#F59E0B`
- Negative: `#DC2626`
- Neutral sentiment: `#64748B`

Palet harus mudah diganti setelah brand guideline resmi diberikan.

### Tipografi

- gunakan Inter, Geist, atau Plus Jakarta Sans;
- angka KPI memakai tabular numerals;
- ukuran body minimum 14px desktop;
- hierarchy jelas tanpa terlalu banyak bold.

### Layout

- sidebar dapat collapse;
- top bar ringkas;
- content max-width cukup lebar untuk dashboard;
- 12-column grid;
- hindari lebih dari empat KPI dalam satu baris pada resolusi 1366px;
- chart cards memiliki judul, deskripsi, aksi, dan definisi metrik;
- gunakan detail drawer untuk menjaga konteks eksplorasi.

### Aturan desain

- jangan membuat semua elemen berbentuk kartu dengan bobot visual sama;
- gunakan warna sentimen secara konsisten;
- jangan bergantung pada warna saja;
- semua ikon memiliki label atau tooltip;
- chart axis dan legend harus jelas;
- angka besar memakai format Indonesia, misalnya `1.245`;
- persentase maksimal dua angka desimal, tetapi utamakan satu angka desimal;
- skeleton loading harus menyerupai layout akhir;
- dark mode tidak wajib untuk MVP.

### Responsivitas

- desktop adalah pengalaman utama;
- tablet mempertahankan filter dan chart utama;
- mobile menampilkan ringkasan, pencarian, dan list secara vertikal;
- tabel lebar berubah menjadi card list di mobile;
- tidak boleh ada horizontal overflow yang tidak disengaja.

### Aksesibilitas

- target WCAG 2.1 AA;
- keyboard navigation;
- visible focus state;
- label form lengkap;
- semantic HTML;
- contrast memadai;
- chart menyediakan ringkasan teks atau data table alternatif;
- modal/drawer memiliki focus trap dan dapat ditutup dengan Escape.

---

## 13. Data dan Taxonomy

### Jenis pekerjaan awal

- Sales Promotion Girl/Boy
- Merchandiser
- Admin
- Staf Gudang
- Operator
- Security
- Cleaning Service
- Driver
- Supervisor Lapangan
- Lainnya

### Intent awal

- Pertanyaan
- Keluhan
- Pengalaman
- Informasi Lowongan
- Promosi
- Peringatan Penipuan

### Sentimen

- Positif
- Netral
- Negatif
- Tidak Yakin

Tampilkan confidence score hanya kepada admin/analyst. Jika confidence rendah, label harus `Tidak Yakin` dan tidak boleh dipaksakan menjadi positif/negatif.

### Dataset demo

Buat seed generator yang menghasilkan minimal **1.200 post sintetis** dalam Bahasa Indonesia informal untuk rentang 90 hari. Dataset harus:

- sepenuhnya sintetis dan tidak meniru akun nyata;
- menggunakan Post ID demo seperti `demo_000001`;
- memiliki variasi slang dan typo yang wajar;
- mencakup seluruh jenis pekerjaan dan topik;
- memiliki beberapa lonjakan terencana agar grafik menarik;
- memiliki distribusi sentimen yang tidak terlalu sempurna;
- mencakup pertanyaan, keluhan, pengalaman, dan informasi;
- mencakup engagement sintetis;
- memiliki field `is_synthetic=true`;
- tidak menggunakan nama individu nyata;
- menyertakan README data dictionary.

Jangan hardcode angka dashboard. Semua KPI dan grafik harus dihitung dari seed data melalui API/backend.

---

## 14. Model Data

Gunakan UUID untuk primary key internal dan string untuk external post ID.

### users

- id
- name
- email
- password_hash
- role: admin, analyst, viewer
- is_active
- created_at

### source_queries

- id
- name
- query_text
- include_keywords
- exclude_keywords
- job_roles
- owner_id
- is_saved
- is_archived
- created_at
- updated_at

### posts

- id
- external_post_id
- source: demo, x_api, import
- text
- created_at_source
- language
- author_public_id nullable
- like_count
- repost_count
- reply_count
- quote_count
- url nullable
- is_synthetic
- ingested_at
- deleted_at nullable

### post_analysis

- id
- post_id
- normalized_text
- sentiment_label
- sentiment_confidence
- intent_label
- intent_confidence
- topic_id
- job_role
- relevance_score
- model_version
- analyzed_at
- needs_review

### topics

- id
- name
- description
- color
- keywords
- is_active

### monitors

- id
- name
- source_query_id
- owner_id
- comparison_window
- is_active
- created_at

### insights

- id
- title
- summary
- evidence_filters JSON
- metric_snapshot JSON
- created_by
- human_status: draft, reviewed, approved
- created_at

### reports

- id
- title
- period_start
- period_end
- query_snapshot JSON
- insight_ids
- created_by
- generated_at

### ingestion_runs

- id
- source
- started_at
- completed_at
- records_received
- records_processed
- records_failed
- status
- error_summary

Tambahkan index pada tanggal, topic, sentiment, job role, external_post_id, dan full-text search field.

---

## 15. Arsitektur Teknis

### Frontend

- Next.js 15 atau versi stabil terbaru yang tersedia;
- TypeScript;
- Tailwind CSS;
- shadcn/ui atau komponen aksesibel setara;
- Apache ECharts atau Recharts untuk visualisasi;
- TanStack Table untuk tabel;
- TanStack Query untuk server state;
- Zod untuk validation;
- Lucide untuk ikon.

### Backend

- Python 3.12;
- FastAPI;
- SQLAlchemy 2;
- Alembic migrations;
- PostgreSQL;
- Pydantic;
- pandas dan scikit-learn untuk pipeline baseline;
- pytest.

### Infrastruktur lokal

- Docker Compose;
- service: frontend, backend, database;
- `.env.example` tanpa secret;
- health check;
- seed command;
- one-command local startup.

### Search

MVP menggunakan PostgreSQL full-text search dan `pg_trgm`. Buat interface `SearchProvider` agar Elasticsearch/OpenSearch atau semantic search dapat ditambahkan kemudian.

### NLP

Gunakan interface terpisah:

- `SentimentAnalyzer`;
- `TopicClassifier`;
- `IntentClassifier`;
- `KeywordExtractor`;
- `InsightSummarizer`.

Default demo harus berjalan tanpa download model besar. Gunakan baseline rule/keyword + model ringan yang deterministik. Sediakan adapter opsional untuk model Bahasa Indonesia tanpa menjadikannya dependency wajib.

### Connector data

Buat interface:

```text
SocialDataConnector
├── MockXConnector        # default, selalu tersedia
├── CsvImportConnector    # wajib
└── OfficialXApiConnector # optional, hanya aktif jika credential tersedia
```

Jangan menggunakan browser scraping atau library yang melanggar kebijakan platform. Jangan menyimpan API token di frontend.

---

## 16. API Minimum

Sediakan OpenAPI docs dan endpoint minimal:

```text
POST   /auth/login
GET    /auth/me

GET    /dashboard/overview
GET    /dashboard/trends
GET    /dashboard/topics
GET    /dashboard/heatmap
GET    /dashboard/questions

GET    /posts
GET    /posts/{id}

GET    /queries
POST   /queries
PATCH  /queries/{id}
DELETE /queries/{id}

GET    /monitors
POST   /monitors
PATCH  /monitors/{id}

GET    /insights
POST   /insights
PATCH  /insights/{id}

GET    /reports
POST   /reports
GET    /reports/{id}/export

POST   /data/import
POST   /data/seed
GET    /data/runs
GET    /health
```

Semua dashboard endpoint menerima filter konsisten:

- `date_from`
- `date_to`
- `query_id`
- `job_roles[]`
- `topics[]`
- `sentiments[]`
- `intents[]`
- `min_engagement`
- `q`

Response harus menyertakan metadata jumlah record, periode, data source mode, dan last updated.

---

## 17. Logika Analitik

### KPI

- Total Post = jumlah post setelah filter.
- Perubahan Volume = perbandingan dengan periode sebelumnya yang memiliki panjang sama.
- Topik Aktif = jumlah topik dengan minimal threshold data.
- Sentimen Dominan = label dengan jumlah terbesar, sertakan persentase.
- Pertanyaan Terdeteksi = jumlah post dengan intent pertanyaan.
- Jenis Pekerjaan Teratas = job role dengan volume tertinggi.

### Engagement score

Gunakan formula konfigurabel dan jelaskan di tooltip. Contoh awal:

```text
engagement_score = likes + (2 × reposts) + (1.5 × replies) + (1.5 × quotes)
```

### Trend change

Gunakan perbandingan terhadap periode sebelumnya. Tangani pembagi nol tanpa menampilkan infinity.

### Peak detection

Gunakan moving average atau z-score sederhana. Label sebagai “lonjakan terdeteksi”, bukan penyebab.

### Relevance

Gunakan full-text rank + keyword match + recency sebagai baseline. Engagement tidak boleh mendominasi relevansi tekstual.

### Topic dan sentiment

- simpan model version;
- tampilkan confidence;
- sediakan kategori Tidak Yakin;
- memungkinkan koreksi manual oleh admin;
- jangan menyamakan sentimen negatif dengan kandidat buruk.

### Insight generation

Template insight harus berbasis data dan menyertakan evidence:

```text
Topik {topic} mencakup {share}% percakapan pada periode {period},
{direction} {change}% dibandingkan periode sebelumnya.
Pertanyaan yang sering muncul berkaitan dengan {keywords}.
```

Semua insight otomatis harus dapat diedit dan disetujui manusia.

---

## 18. Etika, Privasi, dan Kepatuhan

1. Gunakan hanya data publik yang diperoleh melalui jalur resmi atau data sintetis.
2. Jangan melakukan profiling kandidat.
3. Jangan menginferensikan agama, suku, kesehatan, politik, gender, orientasi seksual, kondisi ekonomi, atau atribut sensitif lainnya.
4. Jangan menggunakan dashboard untuk keputusan penerimaan atau penolakan kandidat.
5. Jangan menyediakan pencarian berdasarkan identitas personal.
6. Minimalkan tampilan username; gunakan public ID atau tautan post hanya jika diperlukan dan diizinkan.
7. Hormati penghapusan dan perubahan status post.
8. Ekspor data mentah dibatasi; prioritaskan data agregat dan Post ID.
9. Tampilkan sumber, periode, metode, keterbatasan, dan status data sintetis/live.
10. Jangan menampilkan logo atau nama X seolah-olah TalentPulse merupakan partner resmi.
11. Simpan audit log untuk import, re-analysis, dan approval insight.
12. Credential disimpan hanya di server environment.

Tambahkan halaman atau dialog “Metodologi & Etika Data” yang mudah diakses.

---

## 19. State yang Wajib Dirancang

Untuk setiap halaman, implementasikan:

- loading skeleton;
- first-use onboarding;
- empty state;
- no search result;
- partial data;
- connector offline;
- request error;
- permission denied;
- stale data;
- demo data warning;
- success feedback;
- confirmation untuk aksi destruktif.

Jangan hanya membuat happy path.

---

## 20. Autentikasi dan Role

### Admin

- mengelola data source;
- import dan re-run analysis;
- mengelola taxonomy;
- mengoreksi label;
- mengelola pengguna;
- melihat audit log.

### Analyst

- menggunakan seluruh dashboard;
- membuat query, monitor, insight, dan report;
- mengedit insight miliknya.

### Viewer

- melihat dashboard dan laporan;
- tidak dapat mengubah data atau taxonomy.

Seed akun demo:

- `admin@talentpulse.local`
- `analyst@talentpulse.local`
- `viewer@talentpulse.local`

Password demo harus ditulis di README lokal dan hanya digunakan pada development environment.

---

## 21. Usability Testing Readiness

Produk harus mendukung skenario pengujian berikut:

### Task 1

Temukan tiga topik yang paling banyak dibicarakan mengenai pekerjaan staf gudang selama 30 hari terakhir.

### Task 2

Temukan pertanyaan yang paling sering muncul mengenai sistem shift dan buka tiga post representatif.

### Task 3

Bandingkan sentimen percakapan mengenai pekerjaan admin dan sales promotion.

### Task 4

Simpan monitor untuk “penipuan lowongan” dan bandingkan dua periode.

### Task 5

Buat laporan insight berisi dua grafik dan tiga temuan.

Log secara privacy-preserving:

- task completion;
- time on task;
- error count;
- navigation steps;
- filter usage.

Jangan merekam isi sensitif atau credential pengguna.

Instrumen evaluasi yang disiapkan:

- System Usability Scale (SUS);
- task success rate;
- time on task;
- search relevance judgement untuk Top 5 hasil;
- wawancara singkat kegunaan dan kecocokan alur.

---

## 22. Acceptance Criteria

Proyek dianggap selesai hanya jika seluruh kriteria berikut terpenuhi:

### Fungsional

- aplikasi dapat dijalankan dari clean setup;
- login dan role bekerja;
- seed menghasilkan minimal 1.200 post sintetis;
- seluruh KPI dihitung dari backend;
- global filter memengaruhi seluruh visualisasi relevan;
- klik chart melakukan cross-filter/drill-down;
- search, sort, filter, dan pagination bekerja;
- saved query tersimpan di database;
- insight dapat dibuat, diedit, dan ditinjau;
- laporan dapat diekspor;
- CSV import memiliki validasi;
- mode demo dapat digunakan tanpa API key;
- error state tidak membuat aplikasi blank.

### Visual

- konsisten pada 1366×768 dan 1920×1080;
- responsive pada tablet dan mobile;
- tidak ada text clipping atau horizontal overflow;
- tooltip, legend, axis, dan empty state jelas;
- `DATA DEMO` terlihat pada semua halaman saat memakai data sintetis;
- desain tidak terasa seperti template admin default.

### Teknis

- TypeScript strict mode;
- lint dan formatting lolos;
- backend tests untuk KPI, filter, dan search;
- frontend tests untuk alur utama;
- database migrations tersedia;
- API docs tersedia;
- tidak ada secret dalam repository;
- dependency dan setup terdokumentasi;
- Docker Compose berjalan;
- health endpoint tersedia.

### Etika

- tidak ada profiling kandidat;
- tidak ada scoring kelayakan kerja;
- tidak ada inferensi atribut sensitif;
- export mentah dibatasi;
- disclaimer metodologi dan data source tersedia;
- data demo benar-benar sintetis.

---

## 23. Testing

### Backend unit tests

- perhitungan KPI;
- comparison period;
- pembagi nol;
- filter kombinasi;
- relevance sorting;
- role permission;
- CSV validation;
- insight template;
- synthetic badge metadata.

### Frontend tests

- login;
- filter persistence;
- chart click → filter update;
- post detail drawer;
- save monitor;
- create report;
- loading/error/empty states;
- keyboard navigation dasar.

### End-to-end tests

Gunakan Playwright untuk Task 1–5 pada bagian usability testing readiness.

### Visual QA

Ambil screenshot minimal pada:

- 1366×768;
- 1920×1080;
- tablet 768px;
- mobile 390px.

Periksa overlap, clipping, chart readability, dan responsive behavior.

---

## 24. Deliverables

Hasil akhir wajib berisi:

1. source code frontend;
2. source code backend;
3. database migration;
4. seed generator data sintetis;
5. Docker Compose;
6. `.env.example`;
7. README setup dan arsitektur;
8. data dictionary;
9. API documentation;
10. design tokens;
11. screenshots halaman utama;
12. testing report;
13. usability testing script;
14. limitations dan ethical considerations;
15. deployment guide;
16. daftar fitur MVP dan fitur lanjutan.

README harus menyediakan quick start singkat:

```bash
cp .env.example .env
docker compose up --build
docker compose exec backend python -m app.seed
```

Sesuaikan perintah jika struktur implementasi berbeda, tetapi pertahankan pengalaman one-command setup.

---

## 25. Struktur Repository yang Disarankan

```text
talentpulse/
├── apps/
│   ├── web/
│   └── api/
├── packages/
│   └── shared-types/
├── data/
│   ├── synthetic/
│   └── data_dictionary.md
├── docs/
│   ├── architecture.md
│   ├── information_architecture.md
│   ├── ethics.md
│   ├── usability_test.md
│   └── api.md
├── tests/
│   └── e2e/
├── docker-compose.yml
├── .env.example
└── README.md
```

Jika monorepo memperlambat implementasi, frontend dan backend boleh ditempatkan di folder terpisah yang lebih sederhana. Prioritaskan keterbacaan dan kemudahan menjalankan proyek.

---

## 26. Tahapan Implementasi

### Fase 1 — Foundation

- setup repository;
- database dan migration;
- design tokens;
- app shell;
- authentication demo;
- seed generator;
- API health check.

### Fase 2 — Core Exploration

- global filters;
- Overview;
- Trend Analysis;
- Topic Explorer;
- Post Explorer;
- search dan ranking.

### Fase 3 — Monitoring and Reporting

- saved query;
- comparison period;
- insight workflow;
- report builder;
- exports.

### Fase 4 — Quality

- responsive polish;
- accessibility;
- loading/error/empty states;
- unit and E2E tests;
- visual QA;
- performance optimization.

### Fase 5 — Production Readiness

- X API connector interface;
- CSV import;
- audit log;
- deployment docs;
- ethical review;
- usability testing package.

Setelah setiap fase, jalankan lint, tests, build, dan screenshot QA. Jangan menunda seluruh validasi sampai akhir.

---

## 27. Performance

- initial dashboard load target di bawah 3 detik pada data demo lokal;
- server-side aggregation untuk chart besar;
- pagination pada post;
- cache query agregat;
- debounce search;
- batasi response payload;
- gunakan database index;
- hindari mengirim seluruh teks post ke browser jika tidak diperlukan;
- tampilkan last updated dan stale state.

---

## 28. Copywriting Antarmuka

Gunakan Bahasa Indonesia yang profesional, ringkas, dan tidak menghakimi.

Contoh:

- “Percakapan meningkat 18,4% dibandingkan periode sebelumnya.”
- “Topik ini perlu ditinjau lebih lanjut.”
- “Tidak cukup data untuk membuat perbandingan.”
- “Label otomatis memiliki tingkat keyakinan rendah.”
- “Insight ini dihasilkan dari data sintetis dan bukan kondisi aktual.”

Hindari:

- “Kandidat negatif”;
- “Akun bermasalah”;
- “Pencari kerja berkualitas rendah”;
- klaim sebab-akibat tanpa analisis manusia;
- bahasa yang menyatakan hasil model pasti benar.

---

## 29. Batasan yang Harus Terlihat di Produk

1. Percakapan di X tidak mewakili seluruh pencari kerja.
2. Sentimen otomatis dapat salah memahami slang, sarkasme, dan konteks.
3. Volume percakapan bukan ukuran langsung kebutuhan tenaga kerja.
4. Engagement tinggi tidak selalu berarti informasi paling benar.
5. Data demo tidak boleh ditampilkan sebagai kondisi aktual.
6. Dashboard mendukung eksplorasi informasi, bukan keputusan rekrutmen.
7. Setiap insight harus diverifikasi manusia.

Tampilkan batasan ini pada metodologi, report export, dan onboarding pengguna.

---

## 30. Instruksi Eksekusi untuk AI Coding Agent

1. Mulai dengan membaca seluruh dokumen ini.
2. Buat rencana kerja singkat berdasarkan fase implementasi.
3. Periksa apakah repository sudah memiliki kode; pertahankan perubahan pengguna yang tidak terkait.
4. Bangun aplikasi sampai dapat dijalankan, jangan berhenti pada wireframe atau komponen statis.
5. Gunakan data sintetis sebagai default.
6. Jangan meminta API key X agar mode demo dapat selesai.
7. Jangan menggunakan scraping.
8. Implementasikan cross-filter dan drill-down nyata.
9. Hitung semua metrik dari backend/database.
10. Buat setiap chart memiliki definisi, tooltip, dan alternatif data yang dapat dibaca.
11. Pastikan teori Ellis dan Information Foraging tampak dalam fitur serta navigation flow.
12. Jalankan test, build, dan visual QA.
13. Perbaiki seluruh error sebelum menyerahkan hasil.
14. Dokumentasikan keputusan, keterbatasan, dan cara menjalankan proyek.
15. Pada akhir pekerjaan, berikan ringkasan fitur selesai, hasil pengujian, kredensial demo, dan langkah menjalankan aplikasi.

---

## 31. Definisi Keberhasilan Produk

TalentPulse berhasil jika staf Recruitment/HR dapat menggunakan dashboard untuk menyelesaikan pertanyaan informasi seperti:

> “Topik dan pertanyaan apa yang paling sering dibicarakan pencari kerja mengenai pekerjaan gudang selama 30 hari terakhir, bagaimana perubahannya, dan post mana yang memberikan konteks paling relevan?”

Pengguna harus dapat menjawabnya dengan sedikit langkah, memahami sumber dan keterbatasan data, serta menghasilkan ringkasan yang dapat dipakai sebagai bahan komunikasi rekrutmen—tanpa melakukan profiling atau keputusan otomatis terhadap individu.

---

**Mulai implementasi sekarang. Prioritaskan MVP yang utuh, dapat dijalankan, dapat diuji, dan secara visual matang.**
