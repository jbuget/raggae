"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useCallback, useState } from "react";
import {
  deleteConversation,
  listConversations,
  listMessages,
  streamMessage,
} from "@/lib/api/chat";
import type {
  RetrievedChunkResponse,
  SendMessageRequest,
  StreamDoneEvent,
  StreamTokenEvent,
} from "@/lib/types/api";
import { useAuth } from "./use-auth";

export function useConversations(projectId: string) {
  const { token } = useAuth();

  return useQuery({
    queryKey: ["conversations", projectId],
    queryFn: () => listConversations(token!, projectId),
    enabled: !!token && !!projectId,
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

        for await (const event of streamMessage(token, projectId, data)) {
          if ("token" in event) {
            accumulated += (event as StreamTokenEvent).token;
            setStreamedContent(accumulated);
          } else if ("done" in event) {
            const doneEvent = event as StreamDoneEvent;
            setChunks(doneEvent.chunks);
            if (doneEvent.conversation_id) {
              onConversationId?.(doneEvent.conversation_id);
              queryClient.invalidateQueries({
                queryKey: ["conversations", projectId],
              });
              queryClient.invalidateQueries({
                queryKey: [
                  "messages",
                  projectId,
                  doneEvent.conversation_id,
                ],
              });
            }
          }
        }
      } finally {
        setState("idle");
      }
    },
    [token, projectId, queryClient],
  );

  return { send, state, streamedContent, chunks };
}
