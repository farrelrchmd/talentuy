"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";

import {
  activeFilterChips,
  countActiveFilters,
  defaultFilters,
  filtersFromSearchParams,
  filtersToApiParams,
  filtersToSearchParams,
  toggleArrayValue,
  type ActiveFilterChip,
  type GlobalFilters,
} from "@/lib/filters";

type ArrayFilterKey = "job_roles" | "topics" | "sentiments" | "intents" | "languages";

interface FilterState {
  filters: GlobalFilters;
  /** Nilai ter-debounce untuk dipakai sebagai query key API. */
  debouncedFilters: GlobalFilters;
  apiParams: Record<string, unknown>;
  chips: ActiveFilterChip[];
  activeCount: number;
  setFilters: (next: Partial<GlobalFilters>) => void;
  toggleValue: (key: ArrayFilterKey, value: string) => void;
  removeChip: (chip: ActiveFilterChip) => void;
  setPeriodDays: (days: number) => void;
  reset: () => void;
}

const FilterContext = createContext<FilterState | null>(null);

const DEBOUNCE_MS = 280;

export function FilterProvider({ children }: { children: ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const [filters, setLocalFilters] = useState<GlobalFilters>(() =>
    filtersFromSearchParams(searchParams),
  );
  const [debouncedFilters, setDebouncedFilters] = useState(filters);
  const skipUrlSync = useRef(false);
  const pendingUrlPush = useRef(false);

  // URL adalah sumber kebenaran: tombol back browser mengembalikan konteks.
  useEffect(() => {
    if (skipUrlSync.current) {
      skipUrlSync.current = false;
      return;
    }
    setLocalFilters(filtersFromSearchParams(searchParams));
  }, [searchParams]);

  useEffect(() => {
    const timer = window.setTimeout(() => setDebouncedFilters(filters), DEBOUNCE_MS);
    return () => window.clearTimeout(timer);
  }, [filters]);

  /**
   * Perubahan filter ditulis ke URL setelah render selesai. Navigasi tidak
   * boleh dipanggil dari dalam updater state karena updater dieksekusi saat
   * render — React akan memperingatkan pembaruan Router di tengah render.
   */
  useEffect(() => {
    if (!pendingUrlPush.current) return;
    pendingUrlPush.current = false;
    skipUrlSync.current = true;
    const query = filtersToSearchParams(filters).toString();
    router.replace(query ? `${pathname}?${query}` : pathname, { scroll: false });
  }, [filters, pathname, router]);

  const setFilters = useCallback((partial: Partial<GlobalFilters>) => {
    pendingUrlPush.current = true;
    setLocalFilters((current) => ({ ...current, ...partial }));
  }, []);

  const toggleValue = useCallback((key: ArrayFilterKey, value: string) => {
    pendingUrlPush.current = true;
    setLocalFilters((current) => ({
      ...current,
      [key]: toggleArrayValue(current[key], value),
    }));
  }, []);

  const removeChip = useCallback((chip: ActiveFilterChip) => {
    pendingUrlPush.current = true;
    setLocalFilters((current) => {
      if (chip.key === "data_type") return { ...current, data_type: undefined };
      if (chip.key === "q") return { ...current, q: undefined };
      if (chip.key === "min_engagement" || chip.key === "max_engagement") {
        return { ...current, [chip.key]: undefined };
      }
      const key = chip.key as ArrayFilterKey;
      return { ...current, [key]: current[key].filter((v) => v !== chip.value) };
    });
  }, []);

  const setPeriodDays = useCallback(
    (days: number) => {
      const end = new Date();
      const start = new Date();
      start.setDate(start.getDate() - (days - 1));
      const iso = (date: Date) =>
        `${date.getFullYear()}-${`${date.getMonth() + 1}`.padStart(2, "0")}-${`${date.getDate()}`.padStart(2, "0")}`;
      setFilters({ date_from: iso(start), date_to: iso(end) });
    },
    [setFilters],
  );

  const reset = useCallback(() => {
    pendingUrlPush.current = true;
    setLocalFilters(defaultFilters());
  }, []);

  const value = useMemo<FilterState>(
    () => ({
      filters,
      debouncedFilters,
      apiParams: filtersToApiParams(debouncedFilters),
      chips: activeFilterChips(filters),
      activeCount: countActiveFilters(filters),
      setFilters,
      toggleValue,
      removeChip,
      setPeriodDays,
      reset,
    }),
    [filters, debouncedFilters, setFilters, toggleValue, removeChip, setPeriodDays, reset],
  );

  return <FilterContext.Provider value={value}>{children}</FilterContext.Provider>;
}

export function useFilters(): FilterState {
  const context = useContext(FilterContext);
  if (!context) throw new Error("useFilters harus dipakai di dalam FilterProvider.");
  return context;
}
