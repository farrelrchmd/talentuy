import { describe, expect, it } from "vitest";

import { HEATMAP_SCALE, SENTIMENT_COLORS, heatLevel } from "@/components/charts";

/** Kontras relatif menurut WCAG 2.1 (1–21). */
function contrastRatio(foreground: string, background: string): number {
  const luminance = (hex: string) => {
    const channels = [0, 2, 4].map((offset) => {
      const value = parseInt(hex.slice(1 + offset, 3 + offset), 16) / 255;
      return value <= 0.03928 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4;
    });
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2];
  };
  const a = luminance(foreground);
  const b = luminance(background);
  return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
}

describe("skala heatmap", () => {
  it("memetakan sel kosong ke tingkat paling terang", () => {
    expect(heatLevel(0, 0)).toBe(0);
  });

  it("menaikkan tingkat seiring intensitas", () => {
    expect(heatLevel(1, 0.05)).toBe(1);
    expect(heatLevel(20, 0.5)).toBe(3);
    expect(heatLevel(40, 1)).toBe(5);
  });

  it("tidak pernah melampaui batas skala", () => {
    expect(heatLevel(999, 1.4)).toBe(HEATMAP_SCALE.length - 1);
  });

  // Angka pada sel harus tetap terbaca di seluruh tingkat warna.
  it("setiap tingkat memenuhi kontras WCAG AA", () => {
    for (const level of HEATMAP_SCALE) {
      expect(
        contrastRatio(level.color, level.backgroundColor),
        `kontras kurang pada latar ${level.backgroundColor}`,
      ).toBeGreaterThanOrEqual(4.5);
    }
  });
});

describe("warna sentimen", () => {
  it("menyediakan warna untuk seluruh label termasuk Tidak Yakin", () => {
    expect(Object.keys(SENTIMENT_COLORS).sort()).toEqual([
      "Negatif",
      "Netral",
      "Positif",
      "Tidak Yakin",
    ]);
  });
});
