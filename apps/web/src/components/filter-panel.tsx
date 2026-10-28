"use client";

import { Bookmark, SlidersHorizontal, X } from "lucide-react";
import { useEffect, useState } from "react";

import { useQueries as useSavedQueries, useTaxonomy } from "@/hooks/useApi";
import { useFilters } from "@/hooks/useFilters";
import { cn } from "@/lib/cn";
import { DATE_PRESETS, DATA_TYPE_LABELS, type DataType } from "@/lib/filters";

function Section({
  title,
  hint,
  children,
}: {
  title: string;
  hint?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="border-b border-line px-4 py-3.5 last:border-b-0">
      <p className="tp-label mb-2">{title}</p>
      {hint && <p className="mb-2 text-[11px] leading-relaxed text-muted">{hint}</p>}
      {children}
    </div>
  );
}

function CheckboxList({
  options,
  selected,
  onToggle,
  name,
}: {
  options: string[];
  selected: string[];
  onToggle: (value: string) => void;
  name: string;
}) {
  return (
    <fieldset className="space-y-1.5">
      <legend className="sr-only">{name}</legend>
      {options.map((option) => (
        <label
          key={option}
          className="flex cursor-pointer items-center gap-2 text-[13px] text-ink"
        >
          <input
            type="checkbox"
            checked={selected.includes(option)}
            onChange={() => onToggle(option)}
            className="h-3.5 w-3.5 rounded border-line text-primary focus:ring-primary/30"
          />
          <span className="truncate">{option}</span>
        </label>
      ))}
    </fieldset>
  );
}

/**
 * Filter global. Nilai bertahan antar halaman melalui URL, dan setiap
 * perubahan menerapkan cross-filter ke seluruh visualisasi.
 */
export function FilterPanel({ onClose }: { onClose?: () => void }) {
  const { filters, setFilters, toggleValue, reset, activeCount } = useFilters();
  const { data: taxonomy } = useTaxonomy();
  const { data: savedQueries } = useSavedQueries();

  const [minEngagement, setMinEngagement] = useState(
    filters.min_engagement !== undefined ? String(filters.min_engagement) : "",
  );

  useEffect(() => {
    setMinEngagement(
      filters.min_engagement !== undefined ? String(filters.min_engagement) : "",
    );
  }, [filters.min_engagement]);

  const activeDays =
    (new Date(filters.date_to).getTime() - new Date(filters.date_from).getTime()) /
      86_400_000 +
    1;

  return (
    <div className="flex h-full flex-col bg-surface">
      <div className="flex items-center justify-between border-b border-line px-4 py-3">
        <p className="flex items-center gap-2 text-sm font-semibold text-ink">
          <SlidersHorizontal className="h-4 w-4 text-muted" aria-hidden />
          Filter
          {activeCount > 0 && (
            <span className="rounded-full bg-primary px-1.5 py-0.5 text-[10px] text-white">
              {activeCount}
            </span>
          )}
        </p>
        <div className="flex items-center gap-1">
          <button
            type="button"
            onClick={reset}
            className="text-xs text-primary hover:underline"
          >
            Hapus semua
          </button>
          {onClose && (
            <button
              type="button"
              onClick={onClose}
              className="tp-btn px-1.5 py-1 xl:hidden"
              aria-label="Tutup filter"
            >
              <X className="h-3.5 w-3.5" aria-hidden />
            </button>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto">
        <Section title="Sumber data" hint="Pisahkan post nyata dari data demo sintetis.">
          <select
            aria-label="Sumber data"
            className="tp-input w-full"
            value={filters.data_type ?? "all"}
            onChange={(event) => setFilters({ data_type: event.target.value as DataType })}
          >
            {Object.entries(DATA_TYPE_LABELS).map(([value, label]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
        </Section>
        <Section title="Periode">
          <div className="mb-2 flex flex-wrap gap-1.5">
            {DATE_PRESETS.map((preset) => (
              <button
                key={preset.days}
                type="button"
                onClick={() => {
                  const end = new Date();
                  const start = new Date();
                  start.setDate(start.getDate() - (preset.days - 1));
                  const iso = (date: Date) =>
                    `${date.getFullYear()}-${`${date.getMonth() + 1}`.padStart(2, "0")}-${`${date.getDate()}`.padStart(2, "0")}`;
                  setFilters({ date_from: iso(start), date_to: iso(end) });
                }}
                className={cn(
                  "rounded-md border px-2 py-1 text-xs transition",
                  Math.round(activeDays) === preset.days
                    ? "border-primary bg-primary-soft text-primary-strong"
                    : "border-line text-muted hover:border-primary/40 hover:text-ink",
                )}
              >
                {preset.label}
              </button>
            ))}
          </div>
          <div className="grid grid-cols-2 gap-2">
            <label className="text-[11px] text-muted">
              Dari
              <input
                type="date"
                value={filters.date_from}
                max={filters.date_to}
                onChange={(event) => setFilters({ date_from: event.target.value })}
                className="tp-input mt-1 px-2 py-1.5 text-xs"
              />
            </label>
            <label className="text-[11px] text-muted">
              Sampai
              <input
                type="date"
                value={filters.date_to}
                min={filters.date_from}
                onChange={(event) => setFilters({ date_to: event.target.value })}
                className="tp-input mt-1 px-2 py-1.5 text-xs"
              />
            </label>
          </div>
        </Section>

        <Section
          title="Query tersimpan"
          hint="Terapkan kata kunci dan filter yang sudah disimpan tim."
        >
          <select
            value={filters.query_id ?? ""}
            onChange={(event) =>
              setFilters({ query_id: event.target.value || undefined })
            }
            className="tp-input py-1.5 text-xs"
            aria-label="Pilih query tersimpan"
          >
            <option value="">Tanpa query tersimpan</option>
            {savedQueries?.map((query) => (
              <option key={query.id} value={query.id}>
                {query.name}
              </option>
            ))}
          </select>
          {filters.query_id && (
            <p className="mt-1.5 flex items-center gap-1 text-[11px] text-primary">
              <Bookmark className="h-3 w-3" aria-hidden />
              Filter query tersimpan digabung dengan filter aktif.
            </p>
          )}
        </Section>

        <Section title="Jenis pekerjaan">
          <CheckboxList
            name="Jenis pekerjaan"
            options={taxonomy?.job_roles ?? []}
            selected={filters.job_roles}
            onToggle={(value) => toggleValue("job_roles", value)}
          />
        </Section>

        <Section title="Topik">
          <CheckboxList
            name="Topik"
            options={(taxonomy?.topics ?? []).map((topic) => topic.name)}
            selected={(taxonomy?.topics ?? [])
              .filter((topic) => filters.topics.includes(topic.slug))
              .map((topic) => topic.name)}
            onToggle={(name) => {
              const topic = taxonomy?.topics.find((item) => item.name === name);
              if (topic) toggleValue("topics", topic.slug);
            }}
          />
        </Section>

        <Section title="Sentimen">
          <CheckboxList
            name="Sentimen"
            options={taxonomy?.sentiments ?? []}
            selected={filters.sentiments}
            onToggle={(value) => toggleValue("sentiments", value)}
          />
        </Section>

        <Section title="Kategori percakapan">
          <CheckboxList
            name="Kategori percakapan"
            options={taxonomy?.intents ?? []}
            selected={filters.intents}
            onToggle={(value) => toggleValue("intents", value)}
          />
        </Section>

        <Section
          title="Engagement minimum"
          hint={taxonomy?.engagement_formula ?? "likes + repost + reply + quote berbobot"}
        >
          <div className="flex items-center gap-2">
            <input
              type="number"
              min={0}
              value={minEngagement}
              onChange={(event) => setMinEngagement(event.target.value)}
              onBlur={() =>
                setFilters({
                  min_engagement:
                    minEngagement === "" ? undefined : Number(minEngagement),
                })
              }
              placeholder="0"
              aria-label="Engagement minimum"
              className="tp-input py-1.5 text-xs"
            />
            <button
              type="button"
              className="tp-btn shrink-0 px-2 py-1.5 text-xs"
              onClick={() =>
                setFilters({
                  min_engagement:
                    minEngagement === "" ? undefined : Number(minEngagement),
                })
              }
            >
              Terapkan
            </button>
          </div>
        </Section>

        <Section title="Bahasa">
          <CheckboxList
            name="Bahasa"
            options={taxonomy?.languages ?? ["id", "en"]}
            selected={filters.languages}
            onToggle={(value) => toggleValue("languages", value)}
          />
        </Section>
      </div>
    </div>
  );
}

/** Chip filter aktif — selalu terlihat di atas konten. */
export function ActiveFilterChips() {
  const { chips, removeChip, reset } = useFilters();
  const { data: taxonomy } = useTaxonomy();
  const labelFor = (chip: (typeof chips)[number]) => chip.key === "topics"
    ? `Topik: ${taxonomy?.topics.find((topic) => topic.slug === chip.value)?.name ?? chip.value}`
    : chip.label;
  if (chips.length === 0) return null;

  return (
    <div className="mb-4 flex flex-wrap items-center gap-1.5">
      <span className="text-[11px] uppercase tracking-wide text-muted">Filter aktif</span>
      {chips.map((chip) => (
        <button
          key={`${chip.key}-${chip.value}`}
          type="button"
          onClick={() => removeChip(chip)}
          className="tp-chip transition hover:border-negative hover:text-negative-strong"
          aria-label={`Hapus filter ${labelFor(chip)}`}
        >
          {labelFor(chip)}
          <X className="h-3 w-3" aria-hidden />
        </button>
      ))}
      <button
        type="button"
        onClick={reset}
        className="text-[11px] text-primary hover:underline"
      >
        Hapus semua filter
      </button>
    </div>
  );
}
