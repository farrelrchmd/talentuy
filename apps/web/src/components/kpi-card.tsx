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
        "tp-metric flex min-w-0 flex-col justify-between p-5",
        emphasis ? "tp-metric-emphasis" : "bg-surface",
      )}
    >
      <div>
        <p className="flex items-center gap-1.5 text-xs font-medium text-muted">
          <span>{label}</span>
          <InfoTooltip label={label} text={definition} />
        </p>
        <p
          className={cn(
            "mt-3 tabular font-medium leading-tight tracking-[-0.055em] text-ink",
            emphasis ? "text-[38px]" : "text-[32px]",
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
            className="inline-flex items-center gap-2 text-xs font-medium text-primary transition hover:text-primary-strong"
          >
            {drillDownLabel}
            <ArrowRight className="h-3 w-3" aria-hidden />
          </button>
        )}
      </div>
    </div>
  );
}
