"use client";

import { useQuery } from "@tanstack/react-query";
import { getSystemDefaults } from "@/lib/api/system";

export function useSystemDefaults() {
  return useQuery({
    queryKey: ["system-defaults"],
    queryFn: getSystemDefaults,
    staleTime: Number.POSITIVE_INFINITY,
  });
}
