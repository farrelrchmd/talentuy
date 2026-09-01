"use client";

import { useEffect } from "react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("[TalentPulse]", error);
  }, [error]);

  return (
    <main className="grid min-h-screen place-items-center px-4">
      <div className="max-w-md text-center">
        <h1 className="text-2xl font-semibold tracking-tight">
          Terjadi kesalahan saat menampilkan halaman
        </h1>
        <p className="mt-2 text-xs leading-relaxed text-muted">
          Halaman gagal dirender, tetapi data Anda tetap aman. Coba muat ulang
          bagian ini. Bila terus berulang, hubungi admin dengan menyebutkan kode
          {error.digest ? ` ${error.digest}` : " yang tampil di konsol"}.
        </p>
        <button type="button" onClick={reset} className="tp-btn tp-btn-primary mt-5">
          Muat ulang halaman
        </button>
      </div>
    </main>
  );
}
