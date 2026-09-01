# Screenshot Halaman Utama

Tangkapan layar delapan halaman utama pada empat ukuran layar. Seluruh berkas
dihasilkan otomatis oleh `tests/e2e/visual-qa.spec.ts`, jadi dapat diperbarui
kapan saja:

```bash
cd apps/api && uvicorn app.main:app --port 8000   # terminal terpisah
npm run e2e -- visual-qa                          # dari root
```

| Folder | Ukuran layar |
| --- | --- |
| `1366x768/` | Laptop kantor (target utama pengujian) |
| `1920x1080/` | Monitor desktop |
| `tablet-768/` | Tablet potret |
| `mobile-390/` | Ponsel |

| Berkas | Halaman |
| --- | --- |
| `overview.png` | Overview (`/ringkasan`) |
| `tren.png` | Analisis Tren |
| `topik.png` | Eksplorasi Topik |
| `post.png` | Pencarian Post |
| `pemantauan.png` | Pemantauan Tersimpan |
| `laporan.png` | Laporan Insight |
| `data.png` | Data & Pengaturan |
| `metodologi.png` | Metodologi & Etika |

Seluruh tangkapan layar memakai dataset **sintetis** pada mode demo; badge
`DATA DEMO` terlihat pada setiap halaman.
