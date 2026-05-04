"use client";

import { useEffect, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  deleteDocument,
  getDocumentChunks,
  listDocuments,
  reindexDocument,
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
  const [progress, setProgress] = useState(0);
  const resetTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const animationRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const processingProgressRef = useRef(0);

  function stopAnimation() {
    if (animationRef.current) {
      clearInterval(animationRef.current);
      animationRef.current = null;
    }
  }

  function startProcessingAnimation(from: number) {
    stopAnimation();
    processingProgressRef.current = from;
    animationRef.current = setInterval(() => {
      // Asymptotic easing toward 95%: slows down as it approaches the cap
      processingProgressRef.current += (95 - processingProgressRef.current) * 0.04;
      setProgress(Math.min(94, Math.round(processingProgressRef.current)));
    }, 250);
  }

  const mutation = useMutation({
    onMutate: () => {
      if (resetTimerRef.current) clearTimeout(resetTimerRef.current);
      stopAnimation();
      setProgress(0);
    },
    mutationFn: (files: File[]) =>
      uploadDocuments(token!, projectId, files, (xhrProgress) => {
        if (xhrProgress >= 100) {
          startProcessingAnimation(50);
        } else {
          setProgress(Math.round(xhrProgress / 2));
        }
      }),
    onSuccess: () => {
      stopAnimation();
      setProgress(100);
      queryClient.invalidateQueries({ queryKey: ["documents", projectId] });
      resetTimerRef.current = setTimeout(() => setProgress(0), 600);
    },
    onError: () => {
      stopAnimation();
      setProgress(0);
    },
  });

  useEffect(() => {
    return () => {
      if (resetTimerRef.current) clearTimeout(resetTimerRef.current);
      stopAnimation();
    };
  }, []);

  return { ...mutation, progress };
}

export function useReindexDocument(projectId: string) {
  const { token } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (documentId: string) =>
      reindexDocument(token!, projectId, documentId),
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

export function useDocumentChunks(
  projectId: string,
  documentId: string | null,
) {
  const { token } = useAuth();

  return useQuery({
    queryKey: ["document-chunks", projectId, documentId],
    queryFn: () => getDocumentChunks(token!, projectId, documentId!),
    enabled: !!token && !!projectId && !!documentId,
  });
}
