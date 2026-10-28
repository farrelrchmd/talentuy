/**
 * Identitas perusahaan dan warna merek.
 *
 * Nilai disimpan pada perangkat pengguna (localStorage) sehingga prototipe
 * dapat diuji dengan identitas mitra tanpa menyentuh kode. Logo resmi tidak
 * ditampilkan sebelum aset dan persetujuan tersedia — hanya placeholder teks.
 */

export interface Branding {
  companyName: string;
  productName: string;
  primaryColor: string;
}

export const DEFAULT_BRANDING: Branding = {
  companyName: "PT Siprama Cakrawala (placeholder)",
  productName: "TID",
  primaryColor: "#2563eb",
};

const STORAGE_KEY = "talentpulse.branding";
const HEX_PATTERN = /^#[0-9a-fA-F]{6}$/;
const LEGACY_DEFAULT_PRIMARY = "#2b5f48";

export function isValidHex(value: string): boolean {
  return HEX_PATTERN.test(value.trim());
}

export function loadBranding(): Branding {
  if (typeof window === "undefined") return DEFAULT_BRANDING;
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return DEFAULT_BRANDING;
    const parsed = JSON.parse(raw) as Partial<Branding>;
    const savedPrimary = parsed.primaryColor?.toLowerCase();
    const primaryColor =
      savedPrimary === LEGACY_DEFAULT_PRIMARY
        ? DEFAULT_BRANDING.primaryColor
        : isValidHex(parsed.primaryColor ?? "")
          ? (parsed.primaryColor as string)
          : DEFAULT_BRANDING.primaryColor;
    return {
      companyName: parsed.companyName?.trim() || DEFAULT_BRANDING.companyName,
      productName: /^talent\s*(pulse|pluse)$/i.test(parsed.productName?.trim() ?? "")
        ? DEFAULT_BRANDING.productName
        : parsed.productName?.trim() || DEFAULT_BRANDING.productName,
      // Migrasikan warna hijau bawaan lama, tetapi pertahankan warna kustom pengguna.
      primaryColor,
    };
  } catch {
    return DEFAULT_BRANDING;
  }
}

export function saveBranding(branding: Branding): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(branding));
  } catch {
    /* penyimpanan browser tidak tersedia — pengaturan hanya berlaku sesi ini */
  }
}

function toChannels(hex: string): [number, number, number] {
  const value = hex.replace("#", "");
  const [r, g, b] = [0, 2, 4].map((offset) =>
    parseInt(value.slice(offset, offset + 2), 16),
  );
  return [r, g, b];
}

/** Campur warna dengan putih/hitam untuk varian soft dan strong. */
function mix(
  channels: [number, number, number],
  target: [number, number, number],
  ratio: number,
): string {
  return channels
    .map((channel, index) => Math.round(channel + (target[index] - channel) * ratio))
    .join(" ");
}

/**
 * Tulis warna merek ke CSS variable sehingga seluruh komponen ikut berubah.
 * Nilai ditulis sebagai kanal RGB agar modifier opacity Tailwind tetap bekerja.
 */
export function applyBranding(branding: Branding): void {
  if (typeof document === "undefined") return;
  const root = document.documentElement;
  const channels = toChannels(
    isValidHex(branding.primaryColor)
      ? branding.primaryColor
      : DEFAULT_BRANDING.primaryColor,
  );
  root.style.setProperty("--tp-primary", channels.join(" "));
  root.style.setProperty("--tp-primary-soft", mix(channels, [255, 255, 255], 0.9));
  root.style.setProperty("--tp-primary-strong", mix(channels, [0, 0, 0], 0.18));
}
