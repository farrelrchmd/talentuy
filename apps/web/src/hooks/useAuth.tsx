"use client";

import { useRouter } from "next/navigation";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { ApiError, apiRequest, getToken, setToken } from "@/lib/api";
import type { Role, User } from "@/lib/types";

interface AuthState {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  /** Cek hak akses minimum berdasarkan hierarki role. */
  can: (minimum: Role) => boolean;
}

const ROLE_RANK: Record<Role, number> = { viewer: 1, analyst: 2, admin: 3 };

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    // Tanpa token tersimpan, tidak perlu memanggil /auth/me (pasti 401).
    if (!getToken()) {
      setIsLoading(false);
      return;
    }
    apiRequest<User>("/auth/me")
      .then((profile) => {
        if (!cancelled) setUser(profile);
      })
      .catch(() => {
        if (!cancelled) setUser(null);
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const response = await apiRequest<{ access_token: string; user: User }>(
      "/auth/login",
      { method: "POST", body: { email, password } },
    );
    setToken(response.access_token);
    setUser(response.user);
  }, []);

  const logout = useCallback(() => {
    setToken(null);
    setUser(null);
    router.push("/masuk");
  }, [router]);

  const can = useCallback(
    (minimum: Role) => (user ? ROLE_RANK[user.role] >= ROLE_RANK[minimum] : false),
    [user],
  );

  const value = useMemo(
    () => ({ user, isLoading, login, logout, can }),
    [user, isLoading, login, logout, can],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthState {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth harus dipakai di dalam AuthProvider.");
  return context;
}

export function isSessionError(error: unknown): boolean {
  return error instanceof ApiError && error.status === 401;
}
