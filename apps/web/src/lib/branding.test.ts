import { describe, expect, it } from "vitest";

import {
  DEFAULT_BRANDING,
  applyBranding,
  isValidHex,
  loadBranding,
  saveBranding,
} from "@/lib/branding";

describe("identitas dan warna merek", () => {
  it("memakai identitas bawaan bila belum pernah disimpan", () => {
    expect(loadBranding()).toEqual(DEFAULT_BRANDING);
  });

  it("menyimpan lalu memuat kembali identitas", () => {
    saveBranding({
      companyName: "PT Contoh Mitra",
      productName: "TalentPulse",
      primaryColor: "#0f766e",
    });
    expect(loadBranding().companyName).toBe("PT Contoh Mitra");
    expect(loadBranding().primaryColor).toBe("#0f766e");
  });

  it("mengabaikan warna yang tidak valid", () => {
    saveBranding({ ...DEFAULT_BRANDING, primaryColor: "biru tua" });
    expect(loadBranding().primaryColor).toBe(DEFAULT_BRANDING.primaryColor);
    expect(isValidHex("#12ab34")).toBe(true);
    expect(isValidHex("#xyz")).toBe(false);
  });

  it("bertahan ketika penyimpanan browser berisi data rusak", () => {
    window.localStorage.setItem("talentpulse.branding", "{bukan json");
    expect(loadBranding()).toEqual(DEFAULT_BRANDING);
  });

  // Token ditulis sebagai kanal RGB agar modifier opacity Tailwind tetap jalan.
  it("menulis warna ke CSS variable sebagai kanal RGB", () => {
    applyBranding({ ...DEFAULT_BRANDING, primaryColor: "#2563eb" });
    const root = document.documentElement.style;
    expect(root.getPropertyValue("--tp-primary").trim()).toBe("37 99 235");
    expect(root.getPropertyValue("--tp-primary-soft").trim()).not.toBe("");
    expect(root.getPropertyValue("--tp-primary-strong").trim()).not.toBe("");
  });
});
