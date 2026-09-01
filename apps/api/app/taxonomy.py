"""Taxonomy awal: jenis pekerjaan, topik, intent, dan sentimen.

Semua label antarmuka menggunakan Bahasa Indonesia dan dapat dikelola ulang
oleh admin melalui halaman Data & Pengaturan.
"""

from __future__ import annotations

JOB_ROLES: list[str] = [
    "Sales Promotion Girl/Boy",
    "Merchandiser",
    "Admin",
    "Staf Gudang",
    "Operator",
    "Security",
    "Cleaning Service",
    "Driver",
    "Supervisor Lapangan",
    "Lainnya",
]

INTENTS: list[str] = [
    "Pertanyaan",
    "Keluhan",
    "Pengalaman",
    "Informasi Lowongan",
    "Promosi",
    "Peringatan Penipuan",
]

SENTIMENTS: list[str] = ["Positif", "Netral", "Negatif", "Tidak Yakin"]

LANGUAGES: list[str] = ["id", "en"]

# slug, nama, deskripsi, warna, keywords
TOPIC_SEED: list[tuple[str, str, str, str, list[str]]] = [
    (
        "gaji-benefit",
        "Gaji dan Benefit",
        "Percakapan mengenai besaran gaji, tunjangan, lembur, dan BPJS.",
        "#2563EB",
        [
            "gaji", "upah", "umr", "ump", "umk", "thr", "bonus", "tunjangan",
            "lembur", "bpjs", "slip gaji", "take home pay", "insentif", "uang makan",
        ],
    ),
    (
        "kontrak-status",
        "Kontrak dan Status Kerja",
        "Status karyawan kontrak, outsourcing, probation, dan perpanjangan.",
        "#7C3AED",
        [
            "kontrak", "pkwt", "outsourcing", "alih daya", "probation", "masa percobaan",
            "karyawan tetap", "perpanjangan", "putus kontrak", "status kerja", "yayasan",
        ],
    ),
    (
        "lokasi-penempatan",
        "Lokasi dan Penempatan",
        "Lokasi kerja, penempatan store, mutasi, dan jarak tempuh.",
        "#0891B2",
        [
            "penempatan", "lokasi", "ditempatkan", "store", "cabang", "mutasi",
            "luar kota", "mess", "jarak", "transport", "wilayah",
        ],
    ),
    (
        "shift-jam-kerja",
        "Sistem Shift dan Jam Kerja",
        "Pola shift, jam kerja, hari libur, dan rotasi jadwal.",
        "#F59E0B",
        [
            "shift", "sif", "jam kerja", "masuk pagi", "masuk malam", "rolling",
            "libur", "off", "jadwal", "overtime", "8 jam", "12 jam",
        ],
    ),
    (
        "persyaratan-pendidikan",
        "Persyaratan Pendidikan",
        "Syarat ijazah, jurusan, usia, dan batas minimal pendidikan.",
        "#DB2777",
        [
            "ijazah", "sma", "smk", "d3", "s1", "lulusan", "jurusan", "minimal pendidikan",
            "usia maksimal", "fresh graduate", "syarat", "tinggi badan",
        ],
    ),
    (
        "pengalaman-keahlian",
        "Pengalaman dan Keahlian",
        "Pengalaman kerja, sertifikasi, dan keahlian yang diminta.",
        "#059669",
        [
            "pengalaman", "sertifikat", "sim a", "sim b", "forklift", "excel",
            "skill", "keahlian", "pelatihan", "training", "kursus",
        ],
    ),
    (
        "proses-melamar",
        "Proses Melamar",
        "Alur lamaran, interview, psikotes, dan pengumuman hasil.",
        "#4F46E5",
        [
            "lamaran", "melamar", "interview", "wawancara", "psikotes", "tes",
            "panggilan", "berkas", "cv", "medical check", "pengumuman", "hrd",
        ],
    ),
    (
        "keamanan-penipuan",
        "Keamanan dan Penipuan Lowongan",
        "Indikasi lowongan palsu, pungutan biaya, dan modus penipuan.",
        "#DC2626",
        [
            "penipuan", "loker palsu", "lowongan palsu", "scam", "bayar",
            "pungli", "biaya administrasi", "modus", "waspada", "hati-hati", "tipu",
        ],
    ),
    (
        "pengalaman-kandidat",
        "Pengalaman Kandidat",
        "Cerita pelamar mengenai proses seleksi dan perlakuan yang diterima.",
        "#0EA5E9",
        [
            "ditolak", "diterima", "ghosting", "nunggu kabar", "dikabari",
            "pengalaman melamar", "ramah", "antre", "lama banget", "responsif",
        ],
    ),
    (
        "reputasi-perusahaan",
        "Reputasi Perusahaan Outsourcing",
        "Persepsi publik terhadap vendor penyalur dan perusahaan pengguna.",
        "#64748B",
        [
            "vendor", "penyalur", "perusahaan outsourcing", "reputasi", "review",
            "rekomendasi", "amanah", "bagus ga", "gimana kerjanya", "testimoni",
        ],
    ),
]

TOPIC_NAMES: list[str] = [t[1] for t in TOPIC_SEED]

# Batasan produk yang wajib terlihat pada metodologi, laporan, dan onboarding.
PRODUCT_LIMITATIONS: list[str] = [
    "Percakapan di X tidak mewakili seluruh populasi pencari kerja.",
    "Sentimen otomatis dapat salah memahami slang, sarkasme, dan konteks lokal.",
    "Volume percakapan bukan ukuran langsung kebutuhan tenaga kerja.",
    "Engagement tinggi tidak selalu berarti informasi paling benar.",
    "Data demo bersifat sintetis dan tidak boleh dibaca sebagai kondisi aktual.",
    "Dashboard mendukung eksplorasi informasi, bukan keputusan rekrutmen individu.",
    "Setiap insight harus diverifikasi oleh manusia sebelum digunakan.",
]
