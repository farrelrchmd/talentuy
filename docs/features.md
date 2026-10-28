# Daftar Fitur

## 1. Fitur MVP (selesai)

### Autentikasi dan role

- Login demo dengan JWT, tiga role berjenjang (`viewer < analyst < admin`).
- Halaman login menampilkan akun demo, batasan produk, dan penanda data sintetis.
- Aksi di luar hak akses menampilkan state "Akses dibatasi", bukan halaman kosong.

### Pencarian dan filter global

- Pencarian global (Ctrl/⌘ + K) dengan preset topik dan lompatan antar halaman.
- Operator `AND`, `OR`, `-kata`, dan frasa berkutip.
- Filter: rentang tanggal, query tersimpan, jenis pekerjaan, topik, sentimen,
  kategori intent, rentang engagement, bahasa, kata kunci.
- Cross-filter dari grafik, chip filter aktif, "Hapus semua filter".
- State filter tersimpan pada URL; tombol back browser tetap bermakna.

### Halaman

| Halaman | Isi utama |
| --- | --- |
| Overview | 6 KPI, volume harian + puncak, topik teratas, sentimen per pekerjaan, heatmap kekhawatiran, isu perlu perhatian, pertanyaan teratas |
| Analisis Tren | Granularitas harian/mingguan, mode indeks, perbandingan periode sebelumnya, breakdown topik/pekerjaan/sentimen, anotasi lonjakan |
| Eksplorasi Topik | Kartu topik dengan perubahan periode, kartu kombinasi kategori isu × jenis pekerjaan dengan drill-down ke daftar post, detail topik, kata kunci terkait, pertanyaan per topik |
| Pencarian Post | Pencarian, preset kata kunci per kategori isu, pengurutan relevansi/terbaru/engagement, paginasi, penyorotan istilah, panel detail post dengan dasar klasifikasi tiap label dan koreksi/usulan koreksi |
| Monitoring | Daftar monitor, tren 7 hari, perubahan antar periode, buka di dashboard, duplikat, arsip |
| Laporan Insight | Saran insight dari data, alur draft → ditinjau → disetujui, catatan peninjau, penyusun laporan, pratinjau, ekspor PDF/CSV/Post ID |
| Data & Pengaturan | Status connector, kualitas data, impor CSV/JSON, analisis ulang, bangkitkan data demo, taxonomy topik, preset kata kunci, kamus istilah, log proses, audit log, identitas dan warna merek |
| Metodologi & Etika | Sumber dan pengolahan data, etika, keterbatasan, cara membaca dashboard, pemetaan Ellis dan Information Foraging, ringkasan usability |

### Data dan pengolahan

- Generator dataset sintetis (bawaan 1.400 post / 90 hari, `random_state` tetap).
- Impor CSV/JSON dengan validasi kolom, deduplikasi, dan laporan baris gagal.
- Penarikan data nyata dari X API resmi (`POST /data/fetch-live`, admin) memakai
  pipeline yang sama; aktif hanya bila `X_API_BEARER_TOKEN` tersedia di server.
- Pipeline NLP baseline: normalisasi, topik, sentimen, intent, lima jenis pekerjaan, kata kunci.
- Dasar klasifikasi (aturan + kata pemicu) disimpan per label dan ditampilkan di detail post.
- Analisis ulang seluruh post setelah taxonomy berubah.
- Koreksi label manual oleh admin dan usulan koreksi oleh analis dari detail post,
  keduanya tercatat pada audit log.

### Kualitas antarmuka

- State: loading skeleton, kosong, tanpa hasil, error dengan tombol coba lagi,
  izin ditolak, data usang, connector nonaktif, konfirmasi aksi destruktif, toast.
- Setiap grafik memiliki alternatif tabel data dan ringkasan untuk pembaca layar.
- Desktop-first namun responsif hingga layar ponsel.
- Seluruh antarmuka berbahasa Indonesia.

### Kepatuhan

- Badge `DATA DEMO`/`DATA LIVE` pada seluruh halaman.
- Watermark `DATA SINTETIS — BUKAN TEMUAN AKTUAL` pada pratinjau dan ekspor.
- Ekspor post-level dibatasi pada Post ID, waktu, topik, pekerjaan, dan tautan.
- Audit log untuk impor, analisis ulang, taxonomy, koreksi label, insight, ekspor.

## 2. Fitur lanjutan (belum dikerjakan)

Dikerjakan hanya setelah seluruh fitur wajib stabil.

| Fitur | Catatan implementasi |
| --- | --- |
| Semantic search | Tambah `SearchProvider` berbasis embedding + pgvector; antarmuka tidak berubah |
| Alert terjadwal | Worker terjadwal membandingkan monitor lalu mengirim notifikasi |
| Perbandingan kompetitor | Perlu kajian etika dan dasar hukum tambahan |
| Ringkasan dengan LLM | Ganti `nlp/summarizer.py`; status draft dan peninjauan manusia tetap wajib |
| Single sign-on | Ganti `security.py` dengan OIDC; hierarki role dipertahankan |
| Notifikasi email/Telegram | Mengikuti alert terjadwal |
| Live streaming data | Perlu langganan X API yang mendukung stream |

## 3. Di luar lingkup (permanen)

Tidak akan dikerjakan karena bertentangan dengan posisi etis produk:

- profiling atau skor kelayakan kerja kandidat;
- inferensi atribut sensitif (agama, suku, gender, kesehatan, politik, orientasi
  seksual, kondisi ekonomi);
- pencarian berbasis identitas personal;
- ekspor massal data mentah post;
- pengambilan keputusan ketenagakerjaan otomatis.
