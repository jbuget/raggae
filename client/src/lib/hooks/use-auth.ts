"use client";

import { useSession } from "next-auth/react";

export function useAuth() {
  const { data: session, status } = useSession();

  return {
    isAuthenticated: status === "authenticated",
    isLoading: status === "loading",
    token: session?.accessToken ?? null,
    user: session?.user ?? null,
  };
}
