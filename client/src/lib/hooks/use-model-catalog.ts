"use client";

import { useQuery } from "@tanstack/react-query";
import { getModelCatalog } from "@/lib/api/model-catalog";
import { useAuth } from "./use-auth";

export function useModelCatalog() {
  const { token } = useAuth();

  return useQuery({
    queryKey: ["model-catalog"],
    queryFn: () => getModelCatalog(token!),
    enabled: !!token,
  });
}
