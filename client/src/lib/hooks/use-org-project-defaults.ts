"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  getOrganizationProjectDefaults,
  upsertOrganizationProjectDefaults,
} from "@/lib/api/organizations";
import type { UpsertOrganizationProjectDefaultsRequest } from "@/lib/types/api";
import { useAuth } from "./use-auth";

export function useOrganizationProjectDefaults(organizationId: string | null | undefined) {
  const { token } = useAuth();

  return useQuery({
    queryKey: ["org-project-defaults", organizationId],
    queryFn: () => getOrganizationProjectDefaults(token!, organizationId!),
    enabled: !!token && !!organizationId,
  });
}

export function useUpsertOrganizationProjectDefaults(organizationId: string) {
  const { token } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: UpsertOrganizationProjectDefaultsRequest) =>
      upsertOrganizationProjectDefaults(token!, organizationId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["org-project-defaults", organizationId] });
    },
  });
}
