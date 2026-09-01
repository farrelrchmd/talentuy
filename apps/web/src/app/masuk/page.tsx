"use client";

import { Eye, EyeOff, Loader2, ShieldCheck } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent } from "react";

import { useAuth } from "@/hooks/useAuth";
import { ApiError, apiRequest } from "@/lib/api";

interface DemoAccount {
  email: string;
  role: string;
  description: string;
}

export default function LoginPage() {
  const router = useRouter();
  const { user, isLoading, login } = useAuth();

  const [email, setEmail] = useState("analyst@talentpulse.local");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [accounts, setAccounts] = useState<DemoAccount[]>([]);
  const [demoPassword, setDemoPassword] = useState<string>("");

  useEffect(() => {
    if (!isLoading && user) router.replace("/ringkasan");
  }, [isLoading, user, router]);

  useEffect(() => {
    apiRequest<{ accounts: DemoAccount[]; password: string }>("/auth/demo-accounts")
      .then((data) => {
        setAccounts(data.accounts);
        setDemoPassword(data.password);
      })
      .catch(() => {
        /* Pada environment produksi daftar akun demo memang tidak tersedia. */
      });
  }, []);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);

    if (!email.trim()) return setError("Email wajib diisi.");
    if (!password) return setError("Kata sandi wajib diisi.");

    setSubmitting(true);
    try {
      await login(email.trim(), password);
      router.replace("/ringkasan");
    } catch (caught) {
      setError(
        caught instanceof ApiError
          ? caught.userMessage
          : "Terjadi kesalahan tidak terduga.",
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="grid min-h-screen lg:grid-cols-[1.1fr_1fr]">
      {/* Panel kiri: konteks produk, bukan klaim afiliasi dengan platform mana pun. */}
      <section className="relative hidden flex-col justify-between bg-sidebar p-10 text-slate-300 lg:flex">
        <div className="flex items-center gap-2.5 text-white">
          <span className="grid h-9 w-9 place-items-center rounded-lg bg-primary text-sm font-bold">
            TP
          </span>
          <span className="text-lg font-semibold tracking-tight">TalentPulse</span>
        </div>

        <div className="max-w-lg">
          <h1 className="text-3xl font-semibold leading-tight text-white">
            Dengar percakapan kandidat.
            <br />
            Perjelas komunikasi rekrutmen.
          </h1>
          <p className="mt-4 text-sm leading-relaxed text-slate-400">
            Dashboard internal untuk menelusuri pertanyaan, kekhawatiran, dan
            pengalaman pencari kerja pada percakapan publik — sebagai bahan menyusun
            informasi lowongan yang lebih jelas.
          </p>

          <dl className="mt-8 grid grid-cols-3 gap-4 border-t border-white/10 pt-6 text-xs">
            {[
              ["Topik terkelola", "10 kategori"],
              ["Rentang data demo", "90 hari"],
              ["Metrik", "Dihitung backend"],
            ].map(([label, value]) => (
              <div key={label}>
                <dt className="text-slate-400">{label}</dt>
                <dd className="mt-1 font-medium text-white">{value}</dd>
              </div>
            ))}
          </dl>
        </div>

        <p className="text-[11px] leading-relaxed text-slate-400">
          Prototipe tugas akhir berbasis karya untuk PT Siprama Cakrawala. Tidak
          berafiliasi resmi dengan X. Tidak digunakan untuk profiling atau keputusan
          penerimaan kandidat.
        </p>
      </section>

      <section className="flex items-center justify-center px-5 py-10">
        <div className="w-full max-w-sm">
          <div className="mb-6 lg:hidden">
            <span className="grid h-9 w-9 place-items-center rounded-lg bg-primary text-sm font-bold text-white">
              TP
            </span>
            <h1 className="mt-3 text-lg font-semibold">TalentPulse</h1>
          </div>

          <h2 className="text-xl font-semibold tracking-tight">Masuk ke dashboard</h2>
          <p className="mt-1.5 text-xs leading-relaxed text-muted">
            Aplikasi ini adalah prototipe internal. Data yang ditampilkan pada mode
            demo bersifat sintetis dan bukan kondisi aktual.
          </p>

          <form onSubmit={handleSubmit} className="mt-6 space-y-4" noValidate>
            <div>
              <label htmlFor="email" className="tp-label">
                Email
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="username"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                aria-invalid={Boolean(error)}
                className="tp-input"
                placeholder="nama@talentpulse.local"
              />
            </div>

            <div>
              <label htmlFor="password" className="tp-label">
                Kata sandi
              </label>
              <div className="relative">
                <input
                  id="password"
                  name="password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="current-password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  aria-invalid={Boolean(error)}
                  className="tp-input pr-11"
                  placeholder="Masukkan kata sandi"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((value) => !value)}
                  className="absolute right-2 top-1/2 -translate-y-1/2 rounded p-1.5 text-muted transition hover:text-ink"
                  aria-label={showPassword ? "Sembunyikan kata sandi" : "Tampilkan kata sandi"}
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4" aria-hidden />
                  ) : (
                    <Eye className="h-4 w-4" aria-hidden />
                  )}
                </button>
              </div>
            </div>

            {error && (
              <p
                role="alert"
                className="rounded-lg border border-negative/20 bg-negative/5 px-3 py-2 text-xs text-negative-strong"
              >
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={submitting}
              className="tp-btn tp-btn-primary w-full py-2.5"
            >
              {submitting && <Loader2 className="h-4 w-4 animate-spin" aria-hidden />}
              {submitting ? "Memproses…" : "Masuk"}
            </button>
          </form>

          {accounts.length > 0 && (
            <div className="mt-6 rounded-card border border-line bg-surface-muted p-4">
              <p className="flex items-center gap-1.5 text-xs font-medium text-ink">
                <ShieldCheck className="h-3.5 w-3.5 text-primary" aria-hidden />
                Akun demo (khusus lingkungan pengembangan)
              </p>
              <ul className="mt-2 space-y-1.5">
                {accounts.map((account) => (
                  <li key={account.email}>
                    <button
                      type="button"
                      onClick={() => {
                        setEmail(account.email);
                        setPassword(demoPassword);
                        setError(null);
                      }}
                      className="w-full rounded-md border border-transparent px-2 py-1.5 text-left transition hover:border-line hover:bg-surface"
                    >
                      <span className="block text-xs font-medium capitalize text-ink">
                        {account.role}
                      </span>
                      <span className="block text-[11px] text-muted">{account.email}</span>
                    </button>
                  </li>
                ))}
              </ul>
              <p className="mt-2 text-[11px] text-muted">
                Klik salah satu akun untuk mengisi formulir secara otomatis.
              </p>
            </div>
          )}
        </div>
      </section>
    </main>
  );
}
