import { describe, expect, it } from "vitest";

import {
  changeTone,
  formatChange,
  formatNumber,
  formatPercent,
  formatRelative,
  truncate,
} from "@/lib/format";

describe("format angka Bahasa Indonesia", () => {
  it("memakai pemisah ribuan titik", () => {
    expect(formatNumber(1245)).toBe("1.245");
  });

  it("menampilkan tanda pisah untuk nilai kosong", () => {
    expect(formatNumber(null)).toBe("–");
    expect(formatPercent(undefined)).toBe("–");
  });

  it("memakai koma desimal pada persentase", () => {
    expect(formatPercent(18.44)).toBe("18,4%");
  });

  // Pembagi nol tidak boleh tampil sebagai 0% agar tidak menyesatkan.
  it("menyatakan perubahan yang tidak dapat dihitung", () => {
    expect(formatChange(null)).toBe("Tidak dapat dibandingkan");
    expect(changeTone(null)).toBe("unknown");
  });

  it("menambahkan tanda pada perubahan positif", () => {
    expect(formatChange(12.34)).toBe("+12,3%");
    expect(formatChange(-4)).toBe("-4,0%");
  });

  it("menganggap perubahan kecil sebagai stabil", () => {
    expect(changeTone(0.4)).toBe("flat");
    expect(changeTone(6)).toBe("up");
    expect(changeTone(-6)).toBe("down");
  });

  it("menyatakan data belum pernah diperbarui", () => {
    expect(formatRelative(null)).toBe("belum pernah");
    expect(formatRelative(new Date().toISOString())).toBe("baru saja");
  });

  it("memotong teks panjang pada batas kata", () => {
    const text = "kata ".repeat(60);
    const result = truncate(text, 40);
    expect(result.length).toBeLessThanOrEqual(41);
    expect(result.endsWith("…")).toBe(true);
  });
});
