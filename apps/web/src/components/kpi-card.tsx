"use client";

import { ArrowRight } from "lucide-react";
import type { ReactNode } from "react";

import { ChangeBadge, InfoTooltip } from "@/components/ui";
import { cn } from "@/lib/cn";

interface KpiCardProps {
  label: string;
  value: ReactNode;
  definition: string;
  comparison?: string;
  change?: number | null;
  invertChangeColors?: boolean;
  footer?: ReactNode;
  onDrillDown?: () => void;
  drillDownLabel?: string;
  emphasis?: boolean;
}

/**
 * Kartu KPI: nilai, definisi (tooltip), pembanding periode, dan aksi drill-down.
 * Bobot visual sengaja dibedakan agar tidak semua elemen terasa sama penting.
 */
export function KpiCard({
  label,
  value,
  definition,
  comparison,
  change,
  invertChangeColors,
  footer,
  onDrillDown,
  drillDownLabel = "Telusuri",
  emphasis = false,
}: KpiCardProps) {
  return (
    <div
      className={cn(
        "flex flex-col justify-between rounded-card border bg-surface px-4 py-3.5 transition",
        emphasis ? "border-primary/30 shadow-card" : "border-line",
      )}
    >
      <div>
        <p className="flex items-center gap-1 text-[11px] font-medium uppercase tracking-wide text-muted">
          <span className="truncate">{label}</span>
          <InfoTooltip label={label} text={definition} />
        </p>
        <p
          className={cn(
            "mt-1.5 tabular font-semibold leading-tight text-ink",
            emphasis ? "text-[28px]" : "text-2xl",
          )}
        >
          {value}
        </p>
      </div>

      <div className="mt-2 space-y-1.5">
        {change !== undefined && (
          <div className="flex flex-wrap items-center gap-2">
            <ChangeBadge value={change} invertColors={invertChangeColors} />
            {comparison && <span className="text-[11px] text-muted">{comparison}</span>}
          </div>
        )}
        {change === undefined && comparison && (
          <p className="text-[11px] text-muted">{comparison}</p>
        )}
        {footer}
        {onDrillDown && (
          <button
            type="button"
            onClick={onDrillDown}
            className="inline-flex items-center gap-1 text-[11px] font-medium text-primary transition hover:text-primary-strong"
          >
            {drillDownLabel}
            <ArrowRight className="h-3 w-3" aria-hidden />
          </button>
        )}
      </div>
    </div>
  );
}
