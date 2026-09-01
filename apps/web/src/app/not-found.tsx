import Link from "next/link";

export default function NotFound() {
  return (
    <main className="grid min-h-screen place-items-center px-4">
      <div className="max-w-md text-center">
        <p className="text-xs font-medium uppercase tracking-wide text-muted">
          Halaman tidak ditemukan
        </p>
        <h1 className="mt-2 text-2xl font-semibold tracking-tight">
          Alamat ini tidak tersedia
        </h1>
        <p className="mt-2 text-xs leading-relaxed text-muted">
          Tautan mungkin sudah berubah. Kembali ke Overview untuk melanjutkan
          eksplorasi dengan filter yang sama.
        </p>
        <Link href="/ringkasan" className="tp-btn tp-btn-primary mt-5 inline-flex">
          Kembali ke Overview
        </Link>
      </div>
    </main>
  );
}
