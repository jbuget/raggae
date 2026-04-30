"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { getUserProjectDefaults, upsertUserProjectDefaults } from "@/lib/api/auth";
import type { UpsertUserProjectDefaultsRequest } from "@/lib/types/api";
import { useAuth } from "./use-auth";

export function useUserProjectDefaults() {
  const { token } = useAuth();

  return useQuery({
    queryKey: ["user-project-defaults"],
    queryFn: () => getUserProjectDefaults(token!),
    enabled: !!token,
  });
}

export function useUpsertUserProjectDefaults() {
  const { token } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: UpsertUserProjectDefaultsRequest) =>
      upsertUserProjectDefaults(token!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["user-project-defaults"] });
    },
  });
}
