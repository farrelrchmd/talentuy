# Skrip Usability Testing TalentPulse

## 1. Tujuan

Menguji apakah staf Recruitment/HR dapat menemukan isu percakapan pencari kerja,
membandingkannya antar periode dan jenis pekerjaan, lalu menyusun bahan
komunikasi — dengan langkah lebih sedikit dibanding pencarian manual di media
sosial.

## 2. Peserta

- 5–8 peserta: staf Recruitment, HR, Recruitment Marketing, Employer Branding,
  atau Corporate Communication yang mendukung rekrutmen.
- Kemampuan teknis menengah; tidak perlu latar belakang analisis data.
- Perangkat: laptop kantor, resolusi 1366×768 atau 1920×1080, browser Chrome/Edge.

## 3. Persiapan fasilitator

1. Jalankan aplikasi dan pastikan dataset demo terisi:
   `docker compose exec backend python -m app.seed --reset`.
2. Login dengan akun `analyst@talentpulse.local` (kecuali Tugas 5 memerlukan admin).
3. Reset filter ke bawaan sebelum setiap peserta.
4. Siapkan pencatatan: waktu per tugas, jumlah langkah, jumlah kesalahan.
5. Sampaikan bahwa **data bersifat sintetis** dan yang diuji adalah produk,
   bukan peserta.

Naskah pembuka (dibacakan):

> "Terima kasih sudah meluangkan waktu. Ini prototipe dashboard internal untuk
> membaca percakapan publik pencari kerja. Seluruh datanya buatan, jadi angkanya
> tidak menggambarkan kondisi nyata. Saya akan memberi lima tugas. Kerjakan
> seperti biasa dan ceritakan apa yang Anda pikirkan sambil mengerjakan. Kalau
> ada yang membingungkan, itu masukan berharga bagi kami."

## 4. Tugas

### Tugas 1 — Menemukan topik dominan (target ≤ 2 menit)

> "Temukan tiga topik yang paling banyak dibicarakan mengenai pekerjaan **staf
> gudang** selama 30 hari terakhir."

Jalur ideal: filter Jenis pekerjaan → "Staf Gudang" → Overview / Eksplorasi Topik.
Sukses bila peserta menyebut tiga topik teratas beserta jumlah post.

### Tugas 2 — Menemukan pertanyaan berulang (target ≤ 3 menit)

> "Temukan pertanyaan yang paling sering muncul mengenai **sistem shift**, lalu
> buka tiga post yang mewakili."

Jalur ideal: topik "Sistem Shift dan Jam Kerja" → daftar pertanyaan → detail post.
Sukses bila tiga post dibuka melalui panel detail tanpa kehilangan filter.

### Tugas 3 — Membandingkan sentimen (target ≤ 3 menit)

> "Bandingkan sentimen percakapan mengenai pekerjaan **admin** dan **sales
> promotion**."

Jalur ideal: Overview → grafik sentimen per jenis pekerjaan, atau Analisis Tren
dengan breakdown sentimen. Sukses bila peserta menyebut perbedaan porsi negatif.

### Tugas 4 — Monitoring (target ≤ 3 menit)

> "Simpan pemantauan untuk **penipuan lowongan**, lalu bandingkan dua periode."

Jalur ideal: Pemantauan Tersimpan → Monitor baru → isi kata kunci → baca
perubahan 7 hari. Sukses bila monitor tersimpan dan arah tren terbaca.

### Tugas 5 — Menyusun laporan (target ≤ 5 menit)

> "Buat laporan insight yang memuat dua grafik dan tiga temuan."

Jalur ideal: Laporan Insight → "Saran dari data" → simpan tiga draft → tinjau →
"Susun laporan" pilih dua grafik → pratinjau/ekspor. Sukses bila laporan tersimpan
dan peserta menyadari label "Rekomendasi untuk Ditinjau".

## 5. Metrik yang dicatat

| Metrik | Cara pengambilan |
| --- | --- |
| Task success rate | Observasi fasilitator (berhasil / berhasil dengan bantuan / gagal) |
| Time on task | Stopwatch, dicocokkan dengan log `duration_ms` |
| Error count | Jumlah jalan buntu, salah halaman, atau salah filter |
| Navigation steps | Jumlah perpindahan halaman/klik utama (`step_count`) |
| Filter usage | Nama filter yang dipakai (`filter_keys`) — **nilai filter tidak dicatat** |
| SUS | Kuesioner 10 pernyataan setelah seluruh tugas |
| Search relevance | Penilaian relevan/tidak untuk 5 hasil teratas pada Tugas 2 |

Instrumentasi aplikasi: `POST /usability/events` menyimpan `session_key`,
`task_code`, `event_type`, `step_count`, `duration_ms`, dan `filter_keys` saja.
Isi pencarian, teks post, dan credential tidak pernah dikirim. Rekap tersedia di
halaman Metodologi & Etika bagi admin.

## 6. Kuesioner SUS (skala 1–5)

1. Saya ingin sering memakai dashboard ini.
2. Dashboard ini terasa lebih rumit dari yang seharusnya.
3. Dashboard ini mudah digunakan.
4. Saya butuh bantuan orang teknis untuk memakainya.
5. Fungsi-fungsinya terasa menyatu dengan baik.
6. Ada terlalu banyak hal yang tidak konsisten.
7. Kebanyakan orang akan cepat mempelajarinya.
8. Dashboard ini terasa merepotkan saat dipakai.
9. Saya merasa percaya diri saat memakainya.
10. Saya perlu belajar banyak hal dulu sebelum bisa memakainya.

Skor SUS = (jumlah kontribusi item) × 2,5. Ganjil: nilai − 1. Genap: 5 − nilai.

## 7. Wawancara penutup

1. Bagian mana yang paling membantu pekerjaan Anda sehari-hari?
2. Angka mana yang tadi sempat membingungkan? Apa yang Anda kira artinya?
3. Bila harus menjelaskan temuan ini ke atasan, apa yang masih kurang?
4. Dibanding cara Anda mencari informasi sekarang, mana yang lebih cepat?
5. Apakah ada yang membuat Anda ragu terhadap keakuratan data?
6. Fitur apa yang paling Anda inginkan berikutnya?

## 8. Ambang keberhasilan

| Indikator | Target |
| --- | --- |
| Task success rate | ≥ 80% tanpa bantuan untuk Tugas 1–4 |
| Time on task | Sesuai target masing-masing tugas |
| SUS | ≥ 68 (rata-rata industri) |
| Search relevance | ≥ 3 dari 5 hasil teratas dinilai relevan |
| Kesadaran data sintetis | 100% peserta menyadari data bersifat demo |
