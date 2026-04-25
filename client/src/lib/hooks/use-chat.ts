"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useCallback, useState } from "react";
import {
  deleteConversation,
  getConversation,
  listConversations,
  listMessages,
  renameConversation,
  sendMessage,
  streamMessage,
} from "@/lib/api/chat";
import type {
  RetrievedChunkResponse,
  SendMessageRequest,
  StreamDoneEvent,
  StreamTokenEvent,
} from "@/lib/types/api";
import { useAuth } from "./use-auth";

export function useConversations(projectId: string, limit = 50) {
  const { token } = useAuth();

  return useQuery({
    queryKey: ["conversations", projectId, limit],
    queryFn: () => listConversations(token!, projectId, limit),
    enabled: !!token && !!projectId,
  });
}

export function useConversation(projectId: string, conversationId: string) {
  const { token } = useAuth();

  return useQuery({
    queryKey: ["conversation", projectId, conversationId],
    queryFn: () => getConversation(token!, projectId, conversationId),
    enabled: !!token && !!projectId && !!conversationId,
  });
}

export function useMessages(projectId: string, conversationId: string | null) {
  const { token } = useAuth();

  return useQuery({
    queryKey: ["messages", projectId, conversationId],
    queryFn: () => listMessages(token!, projectId, conversationId!),
    enabled: !!token && !!projectId && !!conversationId,
  });
}

export function useRenameConversation(projectId: string) {
  const { token } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ conversationId, title }: { conversationId: string; title: string }) =>
      renameConversation(token!, projectId, conversationId, title),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["conversations", projectId] });
    },
  });
}

export function useDeleteConversation(projectId: string) {
  const { token } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (conversationId: string) =>
      deleteConversation(token!, projectId, conversationId),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["conversations", projectId],
      });
    },
  });
}

export type ChatState = "idle" | "sending" | "streaming";

export function useSendMessage(projectId: string) {
  const { token } = useAuth();
  const queryClient = useQueryClient();
  const [state, setState] = useState<ChatState>("idle");
  const [streamedContent, setStreamedContent] = useState("");
  const [chunks, setChunks] = useState<RetrievedChunkResponse[]>([]);

  const send = useCallback(
    async (
      data: SendMessageRequest,
      onConversationId?: (id: string) => void,
    ) => {
      if (!token) return;

      setState("sending");
      setStreamedContent("");
      setChunks([]);

      try {
        setState("streaming");
        let accumulated = "";

        try {
          for await (const event of streamMessage(token, projectId, data)) {
            if ("token" in event) {
              accumulated += (event as StreamTokenEvent).token;
              setStreamedContent(accumulated);
            } else if ("done" in event) {
              const doneEvent = event as StreamDoneEvent;
              setChunks(doneEvent.chunks);
              const effectiveConversationId =
                doneEvent.conversation_id || data.conversation_id;
              if (effectiveConversationId) {
                onConversationId?.(effectiveConversationId);
                queryClient.invalidateQueries({
                  queryKey: ["conversations", projectId],
                });
                queryClient.invalidateQueries({
                  queryKey: [
                    "messages",
                    projectId,
                    effectiveConversationId,
                  ],
                });
              }
            }
          }
        } catch {
          let retryConversationId = data.conversation_id ?? null;
          if (!retryConversationId) {
            const latestConversations = await listConversations(
              token,
              projectId,
              1,
              0,
            );
            const latest = latestConversations[0];
            if (latest) {
              retryConversationId = latest.id;
            }
          }

          const response = await sendMessage(token, projectId, {
            ...data,
            conversation_id: retryConversationId,
          });
          setStreamedContent(response.answer);
          setChunks(response.chunks);
          onConversationId?.(response.conversation_id);
          queryClient.invalidateQueries({
            queryKey: ["conversations", projectId],
          });
          queryClient.invalidateQueries({
            queryKey: [
              "messages",
              projectId,
              response.conversation_id,
            ],
          });
        }
      } finally {
        setState("idle");
      }
    },
    [token, projectId, queryClient],
  );

  return { send, state, streamedContent, chunks };
}
