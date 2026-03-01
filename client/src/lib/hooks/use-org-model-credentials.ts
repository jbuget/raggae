"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  activateOrgModelCredential,
  createOrgModelCredential,
  deactivateOrgModelCredential,
  deleteOrgModelCredential,
  listOrgModelCredentials,
} from "@/lib/api/org-model-credentials";
import type { SaveModelCredentialRequest } from "@/lib/types/api";
import { useAuth } from "./use-auth";

export function useOrgModelCredentials(organizationId: string) {
  const { token } = useAuth();

  return useQuery({
    queryKey: ["org-model-credentials", organizationId],
    queryFn: () => listOrgModelCredentials(token!, organizationId),
    enabled: !!token,
  });
}

export function useCreateOrgModelCredential(organizationId: string) {
  const { token } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: SaveModelCredentialRequest) =>
      createOrgModelCredential(token!, organizationId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["org-model-credentials", organizationId] });
    },
  });
}

export function useActivateOrgModelCredential(organizationId: string) {
  const { token } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (credentialId: string) =>
      activateOrgModelCredential(token!, organizationId, credentialId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["org-model-credentials", organizationId] });
    },
  });
}

export function useDeactivateOrgModelCredential(organizationId: string) {
  const { token } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (credentialId: string) =>
      deactivateOrgModelCredential(token!, organizationId, credentialId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["org-model-credentials", organizationId] });
    },
  });
}

export function useDeleteOrgModelCredential(organizationId: string) {
  const { token } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (credentialId: string) =>
      deleteOrgModelCredential(token!, organizationId, credentialId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["org-model-credentials", organizationId] });
    },
  });
}
