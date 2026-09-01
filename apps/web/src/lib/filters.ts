/**
 * Filter global TalentPulse.
 *
 * State disimpan pada URL query string agar tampilan dapat dibagikan secara
 * internal, bertahan saat berpindah halaman, dan tidak hilang ketika pengguna
 * menekan tombol back browser.
 */

import { daysAgo, toIsoDate } from "@/lib/format";

export interface GlobalFilters {
  date_from: string;
  date_to: string;
  query_id?: string;
  job_roles: string[];
  topics: string[];
  sentiments: string[];
  intents: string[];
  languages: string[];
  min_engagement?: number;
  max_engagement?: number;
  q?: string;
}

export const DEFAULT_WINDOW_DAYS = 30;

export const DATE_PRESETS: Array<{ label: string; days: number }> = [
  { label: "7 hari", days: 7 },
  { label: "14 hari", days: 14 },
  { label: "30 hari", days: 30 },
  { label: "90 hari", days: 90 },
];

export function defaultFilters(): GlobalFilters {
  return {
    date_from: toIsoDate(daysAgo(DEFAULT_WINDOW_DAYS - 1)),
    date_to: toIsoDate(new Date()),
    job_roles: [],
    topics: [],
    sentiments: [],
    intents: [],
    languages: [],
  };
}

const ARRAY_KEYS = [
  "job_roles",
  "topics",
  "sentiments",
  "intents",
  "languages",
] as const;

export function filtersFromSearchParams(
  params: URLSearchParams | null,
): GlobalFilters {
  const base = defaultFilters();
  if (!params) return base;

  const next: GlobalFilters = {
    ...base,
    date_from: params.get("date_from") ?? base.date_from,
    date_to: params.get("date_to") ?? base.date_to,
    query_id: params.get("query_id") ?? undefined,
    q: params.get("q") ?? undefined,
  };

  for (const key of ARRAY_KEYS) {
    const values = params.getAll(key).filter(Boolean);
    if (values.length) next[key] = values;
  }

  const min = params.get("min_engagement");
  const max = params.get("max_engagement");
  if (min !== null && min !== "") next.min_engagement = Number(min);
  if (max !== null && max !== "") next.max_engagement = Number(max);

  return next;
}

/** Hanya parameter yang berbeda dari default yang ditulis ke URL. */
export function filtersToSearchParams(filters: GlobalFilters): URLSearchParams {
  const params = new URLSearchParams();
  const base = defaultFilters();

  if (filters.date_from !== base.date_from) params.set("date_from", filters.date_from);
  if (filters.date_to !== base.date_to) params.set("date_to", filters.date_to);
  if (filters.query_id) params.set("query_id", filters.query_id);
  if (filters.q) params.set("q", filters.q);

  for (const key of ARRAY_KEYS) {
    filters[key].forEach((value) => params.append(key, value));
  }
  if (filters.min_engagement !== undefined) {
    params.set("min_engagement", String(filters.min_engagement));
  }
  if (filters.max_engagement !== undefined) {
    params.set("max_engagement", String(filters.max_engagement));
  }
  return params;
}

/** Parameter untuk dikirim ke API (selalu menyertakan periode). */
export function filtersToApiParams(
  filters: GlobalFilters,
): Record<string, unknown> {
  return {
    date_from: `${filters.date_from}T00:00:00`,
    date_to: `${filters.date_to}T23:59:59`,
    query_id: filters.query_id,
    job_roles: filters.job_roles,
    topics: filters.topics,
    sentiments: filters.sentiments,
    intents: filters.intents,
    languages: filters.languages,
    min_engagement: filters.min_engagement,
    max_engagement: filters.max_engagement,
    q: filters.q,
  };
}

export interface ActiveFilterChip {
  key: keyof GlobalFilters;
  value: string;
  label: string;
}

/** Daftar chip filter aktif; periode default tidak ditampilkan sebagai chip. */
export function activeFilterChips(filters: GlobalFilters): ActiveFilterChip[] {
  const chips: ActiveFilterChip[] = [];
  if (filters.q) {
    chips.push({ key: "q", value: filters.q, label: `Pencarian: "${filters.q}"` });
  }
  filters.job_roles.forEach((value) =>
    chips.push({ key: "job_roles", value, label: `Pekerjaan: ${value}` }),
  );
  filters.topics.forEach((value) =>
    chips.push({ key: "topics", value, label: `Topik: ${value}` }),
  );
  filters.sentiments.forEach((value) =>
    chips.push({ key: "sentiments", value, label: `Sentimen: ${value}` }),
  );
  filters.intents.forEach((value) =>
    chips.push({ key: "intents", value, label: `Kategori: ${value}` }),
  );
  filters.languages.forEach((value) =>
    chips.push({ key: "languages", value, label: `Bahasa: ${value}` }),
  );
  if (filters.min_engagement !== undefined) {
    chips.push({
      key: "min_engagement",
      value: String(filters.min_engagement),
      label: `Engagement ≥ ${filters.min_engagement}`,
    });
  }
  if (filters.max_engagement !== undefined) {
    chips.push({
      key: "max_engagement",
      value: String(filters.max_engagement),
      label: `Engagement ≤ ${filters.max_engagement}`,
    });
  }
  return chips;
}

export function countActiveFilters(filters: GlobalFilters): number {
  return activeFilterChips(filters).length + (filters.query_id ? 1 : 0);
}

/** Toggle satu nilai pada filter bertipe array (dipakai cross-filter chart). */
export function toggleArrayValue(values: string[], value: string): string[] {
  return values.includes(value)
    ? values.filter((item) => item !== value)
    : [...values, value];
}
