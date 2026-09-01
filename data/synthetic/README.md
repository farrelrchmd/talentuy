# Data Sintetis

Seluruh berkas pada folder ini **buatan** dan tidak berasal dari akun atau post
nyata siapa pun. Isinya menirukan pola pertanyaan pencari kerja Indonesia agar
dashboard dapat diuji tanpa menyentuh data pribadi.

| Berkas | Isi |
| --- | --- |
| `contoh_impor.csv` | 8 baris contoh untuk menguji alur impor pada Data & Pengaturan |

Dataset demo utama (bawaan 1.400 post / 90 hari) tidak disimpan sebagai berkas,
melainkan dibangkitkan ulang oleh generator agar dapat direproduksi:

```bash
cd apps/api
python -m app.seed --reset               # bawaan: 1400 post, 90 hari
python -m app.seed --reset --count 2000 --days 120
```

Generator memakai `SEED_RANDOM_STATE` (bawaan `20260828`) sehingga dataset yang
dihasilkan sama pada setiap mesin. Setiap post ditandai `is_synthetic = true` dan
tampil di antarmuka dengan badge `DATA DEMO`.

Cara menguji impor:

1. Login sebagai `admin@talentpulse.local`.
2. Buka **Data & Pengaturan → Impor data**.
3. Unggah `contoh_impor.csv`.
4. Periksa hasilnya pada **Log proses data** dan **Kualitas data**.
