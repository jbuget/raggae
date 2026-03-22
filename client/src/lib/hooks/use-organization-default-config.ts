"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  getOrganizationDefaultConfig,
  upsertOrganizationDefaultConfig,
} from "@/lib/api/organizations";
import type { UpsertOrganizationDefaultConfigRequest } from "@/lib/types/api";
import { useAuth } from "./use-auth";

export function useOrganizationDefaultConfig(organizationId: string) {
  const { token } = useAuth();
  return useQuery({
    queryKey: ["organization-default-config", organizationId],
    queryFn: () => getOrganizationDefaultConfig(token!, organizationId),
    enabled: !!token && !!organizationId,
  });
}

export function useUpsertOrganizationDefaultConfig(organizationId: string) {
  const { token } = useAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: UpsertOrganizationDefaultConfigRequest) =>
      upsertOrganizationDefaultConfig(token!, organizationId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["organization-default-config", organizationId],
      });
    },
  });
}
