"use client";

import { usePathname, useRouter } from "next/navigation";
import { Suspense, useEffect, useRef, useState, type ReactNode } from "react";

import { FilterPanel } from "@/components/filter-panel";
import { Sidebar, TopBar } from "@/components/shell";
import { InlineLoader } from "@/components/ui";
import { useAuth } from "@/hooks/useAuth";
import { FilterProvider } from "@/hooks/useFilters";
import { MetaProvider, useMeta } from "@/hooks/useMeta";

function Shell({ children }: { children: ReactNode }) {
  const { meta } = useMeta();
  const pathname = usePathname();
  const mainRef = useRef<HTMLElement>(null);
  const previousPath = useRef<string | null>(null);
  const [collapsed, setCollapsed] = useState(false);
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const [filtersOpen, setFiltersOpen] = useState(false);

  // Setelah berpindah halaman, fokus dipindahkan ke konten utama agar pengguna
  // keyboard dan pembaca layar mulai dari awal halaman baru, bukan dari posisi
  // tautan navigasi sebelumnya. Muat pertama dibiarkan agar tautan "Lewati ke
  // konten utama" tetap menjadi target Tab pertama.
  // Membandingkan path sebelumnya (bukan penanda "render pertama") karena
  // React Strict Mode menjalankan effect dua kali saat mount.
  useEffect(() => {
    if (previousPath.current !== null && previousPath.current !== pathname) {
      mainRef.current?.focus();
    }
    previousPath.current = pathname;
  }, [pathname]);

  return (
    <div className="flex min-h-screen">
      <Sidebar
        collapsed={collapsed}
        onToggle={() => setCollapsed((value) => !value)}
        mobileOpen={mobileNavOpen}
        onCloseMobile={() => setMobileNavOpen(false)}
      />

      <div className="flex min-w-0 flex-1 flex-col">
        <TopBar
          meta={meta}
          onOpenMobileNav={() => setMobileNavOpen(true)}
          onOpenFilters={() => setFiltersOpen(true)}
        />

        <div className="flex min-w-0 flex-1">
          <main
            id="konten-utama"
            ref={mainRef}
            className="min-w-0 flex-1 px-4 py-5 lg:px-6 focus:outline-none"
            tabIndex={-1}
          >
            <div className="mx-auto w-full max-w-[1440px]">{children}</div>
          </main>

          {/* Panel filter menetap pada layar lebar agar konteks selalu terlihat. */}
          <aside className="no-print sticky top-[86px] hidden h-[calc(100vh-86px)] w-[268px] shrink-0 overflow-hidden border-l border-line xl:block">
            <FilterPanel />
          </aside>
        </div>
      </div>

      {filtersOpen && (
        <div className="no-print fixed inset-0 z-50 flex justify-end xl:hidden">
          <div
            className="absolute inset-0 bg-sidebar/40"
            onClick={() => setFiltersOpen(false)}
            aria-hidden
          />
          <div className="relative h-full w-[290px] animate-slide-in shadow-drawer">
            <FilterPanel onClose={() => setFiltersOpen(false)} />
          </div>
        </div>
      )}
    </div>
  );
}

export default function DashboardLayout({ children }: { children: ReactNode }) {
  const router = useRouter();
  const { user, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading && !user) router.replace("/masuk");
  }, [isLoading, user, router]);

  if (isLoading || !user) {
    return (
      <div className="grid min-h-screen place-items-center">
        <InlineLoader label="Menyiapkan dashboard" />
      </div>
    );
  }

  return (
    <Suspense
      fallback={
        <div className="grid min-h-screen place-items-center">
          <InlineLoader label="Memuat filter" />
        </div>
      }
    >
      <FilterProvider>
        <MetaProvider>
          <Shell>{children}</Shell>
        </MetaProvider>
      </FilterProvider>
    </Suspense>
  );
}
