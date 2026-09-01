"use client";

import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import type { ResponseMeta } from "@/lib/types";

interface MetaState {
  meta?: ResponseMeta;
  setMeta: (meta: ResponseMeta | undefined) => void;
}

const MetaContext = createContext<MetaState | null>(null);

/**
 * Menyimpan metadata response terakhir (periode, mode data, kesegaran) agar
 * top bar dapat menampilkan badge DATA DEMO dan timestamp yang konsisten
 * dengan data yang sedang ditampilkan halaman.
 */
export function MetaProvider({ children }: { children: ReactNode }) {
  const [meta, setMeta] = useState<ResponseMeta | undefined>(undefined);
  const value = useMemo(() => ({ meta, setMeta }), [meta]);
  return <MetaContext.Provider value={value}>{children}</MetaContext.Provider>;
}

export function useMeta(): MetaState {
  const context = useContext(MetaContext);
  if (!context) throw new Error("useMeta harus dipakai di dalam MetaProvider.");
  return context;
}

/** Dipanggil halaman untuk mendaftarkan metadata response-nya. */
export function useReportMeta(meta: ResponseMeta | undefined): void {
  const { setMeta } = useMeta();
  useEffect(() => {
    if (meta) setMeta(meta);
  }, [meta, setMeta]);
}
