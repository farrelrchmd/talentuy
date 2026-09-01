/** Format angka dan tanggal dalam konvensi Bahasa Indonesia. */

const numberFormatter = new Intl.NumberFormat("id-ID");
const dateFormatter = new Intl.DateTimeFormat("id-ID", {
  day: "numeric",
  month: "short",
  year: "numeric",
});
const dateTimeFormatter = new Intl.DateTimeFormat("id-ID", {
  day: "numeric",
  month: "short",
  year: "numeric",
  hour: "2-digit",
  minute: "2-digit",
});
const shortDateFormatter = new Intl.DateTimeFormat("id-ID", {
  day: "numeric",
  month: "short",
});

/** 1245 -> "1.245" */
export function formatNumber(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "–";
  return numberFormatter.format(value);
}

/** Persentase satu angka desimal: 18,4% */
export function formatPercent(
  value: number | null | undefined,
  decimals = 1,
): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "–";
  return `${value.toFixed(decimals).replace(".", ",")}%`;
}

/** Perubahan dengan tanda eksplisit. Null berarti tidak dapat dihitung. */
export function formatChange(value: number | null | undefined): string {
  if (value === null || value === undefined) return "Tidak dapat dibandingkan";
  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toFixed(1).replace(".", ",")}%`;
}

export function changeTone(
  value: number | null | undefined,
): "up" | "down" | "flat" | "unknown" {
  if (value === null || value === undefined) return "unknown";
  if (value > 1) return "up";
  if (value < -1) return "down";
  return "flat";
}

export function formatDate(value: string | Date | null | undefined): string {
  if (!value) return "–";
  const date = typeof value === "string" ? new Date(value) : value;
  if (Number.isNaN(date.getTime())) return "–";
  return dateFormatter.format(date);
}

export function formatShortDate(value: string | Date | null | undefined): string {
  if (!value) return "–";
  const date = typeof value === "string" ? new Date(value) : value;
  if (Number.isNaN(date.getTime())) return "–";
  return shortDateFormatter.format(date);
}

export function formatDateTime(value: string | Date | null | undefined): string {
  if (!value) return "–";
  const date = typeof value === "string" ? new Date(value) : value;
  if (Number.isNaN(date.getTime())) return "–";
  return dateTimeFormatter.format(date);
}

/** "3 menit lalu" — dipakai pada indikator kesegaran data. */
export function formatRelative(value: string | null | undefined): string {
  if (!value) return "belum pernah";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "belum pernah";
  const diffMs = Date.now() - date.getTime();
  const minutes = Math.round(diffMs / 60000);
  if (minutes < 1) return "baru saja";
  if (minutes < 60) return `${minutes} menit lalu`;
  const hours = Math.round(minutes / 60);
  if (hours < 24) return `${hours} jam lalu`;
  const days = Math.round(hours / 24);
  return `${days} hari lalu`;
}

export function toIsoDate(date: Date): string {
  const year = date.getFullYear();
  const month = `${date.getMonth() + 1}`.padStart(2, "0");
  const day = `${date.getDate()}`.padStart(2, "0");
  return `${year}-${month}-${day}`;
}

export function daysAgo(days: number): Date {
  const date = new Date();
  date.setDate(date.getDate() - days);
  return date;
}

/** Potong teks panjang pada batas kata terdekat. */
export function truncate(text: string, max = 180): string {
  if (text.length <= max) return text;
  const cut = text.slice(0, max);
  const lastSpace = cut.lastIndexOf(" ");
  return `${cut.slice(0, lastSpace > 60 ? lastSpace : max)}…`;
}
