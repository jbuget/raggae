"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  deleteDocument,
  listDocuments,
  uploadDocuments,
} from "@/lib/api/documents";
import { useAuth } from "./use-auth";

export function useDocuments(projectId: string) {
  const { token } = useAuth();

  return useQuery({
    queryKey: ["documents", projectId],
    queryFn: () => listDocuments(token!, projectId),
    enabled: !!token && !!projectId,
  });
}

export function useUploadDocument(projectId: string) {
  const { token } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (files: File[]) => uploadDocuments(token!, projectId, files),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents", projectId] });
    },
  });
}

export function useDeleteDocument(projectId: string) {
  const { token } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (documentId: string) =>
      deleteDocument(token!, projectId, documentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents", projectId] });
    },
  });
}
