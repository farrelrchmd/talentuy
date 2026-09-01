"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { InlineLoader } from "@/components/ui";
import { useAuth } from "@/hooks/useAuth";

export default function RootPage() {
  const router = useRouter();
  const { user, isLoading } = useAuth();

  useEffect(() => {
    if (isLoading) return;
    router.replace(user ? "/ringkasan" : "/masuk");
  }, [isLoading, user, router]);

  return (
    <div className="grid min-h-screen place-items-center">
      <InlineLoader label="Menyiapkan TalentPulse" />
    </div>
  );
}
