"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  activateModelCredential,
  createModelCredential,
  deleteModelCredential,
  listModelCredentials,
} from "@/lib/api/model-credentials";
import type { SaveModelCredentialRequest } from "@/lib/types/api";
import { useAuth } from "./use-auth";

export function useModelCredentials() {
  const { token } = useAuth();

  return useQuery({
    queryKey: ["model-credentials"],
    queryFn: () => listModelCredentials(token!),
    enabled: !!token,
  });
}

export function useCreateModelCredential() {
  const { token } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: SaveModelCredentialRequest) => createModelCredential(token!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["model-credentials"] });
    },
  });
}

export function useActivateModelCredential() {
  const { token } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (credentialId: string) => activateModelCredential(token!, credentialId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["model-credentials"] });
    },
  });
}

export function useDeleteModelCredential() {
  const { token } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (credentialId: string) => deleteModelCredential(token!, credentialId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["model-credentials"] });
    },
  });
}
