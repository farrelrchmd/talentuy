import type { SVGProps } from "react";

/** Dua sisi kebutuhan yang dipertemukan melalui analisis. */
export function BrandMark(props: SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 32 32" fill="none" aria-hidden="true" {...props}>
      <path
        d="M8 8L16 16L24 8M8 24L16 16L24 24"
        stroke="currentColor"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path d="M16 11L21 16L16 21L11 16Z" fill="currentColor" />
      <g stroke="currentColor" strokeWidth="2.5">
        <circle cx="6" cy="6" r="3" />
        <circle cx="26" cy="6" r="3" />
        <circle cx="6" cy="26" r="3" />
        <circle cx="26" cy="26" r="3" />
      </g>
    </svg>
  );
}
