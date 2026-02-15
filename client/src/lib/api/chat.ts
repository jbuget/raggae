import type {
  ConversationDetailResponse,
  ConversationResponse,
  MessageResponse,
  SendMessageRequest,
  SendMessageResponse,
  StreamEvent,
} from "@/lib/types/api";
import { apiFetch } from "./client";

export function sendMessage(
  token: string,
  projectId: string,
  data: SendMessageRequest,
): Promise<SendMessageResponse> {
  return apiFetch<SendMessageResponse>(
    `/projects/${projectId}/chat/messages`,
    {
      method: "POST",
      body: JSON.stringify(data),
      token,
    },
  );
}

export async function* streamMessage(
  token: string,
  projectId: string,
  data: SendMessageRequest,
): AsyncGenerator<StreamEvent> {
  const response = await fetch(
    `/api/v1/projects/${projectId}/chat/messages/stream`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    },
  );

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Stream error ${response.status}: ${text}`);
  }

  const reader = response.body?.getReader();
  if (!reader) throw new Error("No response body");

  const decoder = new TextDecoder();
  let buffer = "";

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const data = line.slice(6).trim();
          if (data) {
            try {
              yield JSON.parse(data) as StreamEvent;
            } catch {
              // skip unparseable lines
            }
          }
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}

export function listConversations(
  token: string,
  projectId: string,
  limit = 50,
  offset = 0,
): Promise<ConversationResponse[]> {
  return apiFetch<ConversationResponse[]>(
    `/projects/${projectId}/chat/conversations?limit=${limit}&offset=${offset}`,
    { token },
  );
}

export function getConversation(
  token: string,
  projectId: string,
  conversationId: string,
): Promise<ConversationDetailResponse> {
  return apiFetch<ConversationDetailResponse>(
    `/projects/${projectId}/chat/conversations/${conversationId}`,
    { token },
  );
}

export function deleteConversation(
  token: string,
  projectId: string,
  conversationId: string,
): Promise<void> {
  return apiFetch<void>(
    `/projects/${projectId}/chat/conversations/${conversationId}`,
    { method: "DELETE", token },
  );
}

export function listMessages(
  token: string,
  projectId: string,
  conversationId: string,
  limit = 50,
  offset = 0,
): Promise<MessageResponse[]> {
  return apiFetch<MessageResponse[]>(
    `/projects/${projectId}/chat/conversations/${conversationId}/messages?limit=${limit}&offset=${offset}`,
    { token },
  );
}
