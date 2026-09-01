import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/** Gabungkan className bersyarat sekaligus menyelesaikan konflik utility Tailwind. */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}
