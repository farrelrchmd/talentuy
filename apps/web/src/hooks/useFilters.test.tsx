import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { FilterProvider, useFilters } from "@/hooks/useFilters";

const replace = vi.fn();
let searchParams = new URLSearchParams();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace, push: vi.fn() }),
  usePathname: () => "/ringkasan",
  useSearchParams: () => searchParams,
}));

/** Meniru interaksi halaman: klik grafik, hapus chip, dan reset filter. */
function Harness() {
  const { filters, chips, activeCount, toggleValue, removeChip, reset } = useFilters();

  return (
    <div>
      <p data-testid="topics">{filters.topics.join(",")}</p>
      <p data-testid="jumlah">{activeCount}</p>
      <p data-testid="chips">{chips.map((chip) => chip.label).join(" | ")}</p>
      <button type="button" onClick={() => toggleValue("topics", "gaji-benefit")}>
        Klik batang topik
      </button>
      <button type="button" onClick={() => chips[0] && removeChip(chips[0])}>
        Hapus chip pertama
      </button>
      <button type="button" onClick={reset}>
        Hapus semua filter
      </button>
    </div>
  );
}

function renderHarness() {
  return render(
    <FilterProvider>
      <Harness />
    </FilterProvider>,
  );
}

describe("filter global lintas halaman", () => {
  beforeEach(() => {
    replace.mockClear();
    searchParams = new URLSearchParams();
  });

  it("membaca filter awal dari URL sehingga tampilan dapat dibagikan", () => {
    searchParams = new URLSearchParams("topics=shift-jam-kerja&q=lembur");
    renderHarness();

    expect(screen.getByTestId("topics")).toHaveTextContent("shift-jam-kerja");
    expect(screen.getByTestId("chips")).toHaveTextContent('Pencarian: "lembur"');
  });

  // Klik pada grafik = cross-filter.
  it("menambah lalu melepas filter saat elemen grafik diklik dua kali", async () => {
    renderHarness();
    const chartBar = screen.getByRole("button", { name: "Klik batang topik" });

    await userEvent.click(chartBar);
    expect(screen.getByTestId("topics")).toHaveTextContent("gaji-benefit");
    expect(replace).toHaveBeenCalledWith(
      "/ringkasan?topics=gaji-benefit",
      expect.objectContaining({ scroll: false }),
    );

    await userEvent.click(chartBar);
    expect(screen.getByTestId("topics")).toHaveTextContent("");
  });

  it("melepas satu filter melalui chip aktif", async () => {
    searchParams = new URLSearchParams("topics=gaji-benefit");
    renderHarness();

    expect(screen.getByTestId("jumlah")).toHaveTextContent("1");
    await userEvent.click(screen.getByRole("button", { name: "Hapus chip pertama" }));
    expect(screen.getByTestId("jumlah")).toHaveTextContent("0");
  });

  it("mengembalikan seluruh filter ke bawaan", async () => {
    searchParams = new URLSearchParams("topics=gaji-benefit&q=shift");
    renderHarness();

    await userEvent.click(screen.getByRole("button", { name: "Hapus semua filter" }));
    expect(screen.getByTestId("jumlah")).toHaveTextContent("0");
    expect(replace).toHaveBeenLastCalledWith(
      "/ringkasan",
      expect.objectContaining({ scroll: false }),
    );
  });
});
