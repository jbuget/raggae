"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { ScrollArea } from "@/components/ui/scroll-area";
import { MessageBubble } from "./message-bubble";
import { MessageInput } from "./message-input";
import { StreamingIndicator } from "./streaming-indicator";
import { useMessages, useSendMessage } from "@/lib/hooks/use-chat";
import type { MessageResponse } from "@/lib/types/api";
import { Button } from "@/components/ui/button";

interface ChatPanelProps {
  projectId: string;
  conversationId: string | null;
}

export function ChatPanel({ projectId, conversationId }: ChatPanelProps) {
  const router = useRouter();
  const { data: existingMessages } = useMessages(projectId, conversationId);
  const { send, state, streamedContent, chunks } = useSendMessage(projectId);
  const [optimisticMessages, setOptimisticMessages] = useState<MessageResponse[]>([]);
  const [showChunks, setShowChunks] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  const messages = useMemo(() => {
    if (existingMessages) return [...existingMessages, ...optimisticMessages];
    return optimisticMessages;
  }, [existingMessages, optimisticMessages]);
  const lastMessage = messages.at(-1);
  const citedDocuments = useMemo(() => {
    const unique = new Map<string, string>();
    for (const chunk of chunks) {
      if (!unique.has(chunk.document_id)) {
        unique.set(
          chunk.document_id,
          chunk.document_file_name || chunk.document_id,
        );
      }
    }
    return Array.from(unique.values());
  }, [chunks]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, streamedContent]);

  async function handleSend(content: string) {
    const userMessage: MessageResponse = {
      id: `temp-${Date.now()}`,
      conversation_id: conversationId ?? "",
      role: "user",
      content,
      created_at: new Date().toISOString(),
    };

    setOptimisticMessages((prev) => [...prev, userMessage]);

    await send(
      {
        message: content,
        conversation_id: conversationId,
      },
      (newConversationId) => {
        setOptimisticMessages([]);
        if (!conversationId) {
          router.push(
            `/projects/${projectId}/chat/${newConversationId}`,
          );
        }
      },
    );
  }

  const shouldRenderTransientAssistant =
    streamedContent.length > 0 &&
    (state === "streaming" || lastMessage?.role !== "assistant");

  function getMessageSourceDocuments(message: MessageResponse): string[] {
    const documents = message.source_documents ?? [];
    const unique = new Map<string, string>();
    for (const document of documents) {
      const name = document.document_file_name || document.document_id;
      if (!unique.has(document.document_id)) {
        unique.set(document.document_id, name);
      }
    }
    return Array.from(unique.values());
  }

  return (
    <div className="flex h-full flex-col">
      <ScrollArea className="flex-1 p-4" ref={scrollRef}>
        <div className="space-y-4">
          {messages.map((msg) => {
            const messageSourceDocuments = getMessageSourceDocuments(msg);
            return (
              <div key={msg.id} className="space-y-2">
                <MessageBubble
                  role={msg.role as "user" | "assistant"}
                  content={msg.content}
                  reliabilityPercent={msg.reliability_percent}
                  timestamp={msg.created_at}
                />
                {msg.role === "assistant" && messageSourceDocuments.length > 0 && (
                  <p className="text-xs text-muted-foreground">
                    Sources: {messageSourceDocuments.join(", ")}
                  </p>
                )}
              </div>
            );
          })}

          {state === "sending" && <StreamingIndicator />}

          {shouldRenderTransientAssistant && (
            <div className="space-y-2">
              <MessageBubble role="assistant" content={streamedContent} />
              {citedDocuments.length > 0 && (
                <p className="text-xs text-muted-foreground">
                  Sources: {citedDocuments.join(", ")}
                </p>
              )}
            </div>
          )}

          {!shouldRenderTransientAssistant &&
            lastMessage?.role === "assistant" &&
            citedDocuments.length > 0 && (
              <p className="text-xs text-muted-foreground">
                Sources: {citedDocuments.join(", ")}
              </p>
            )}
        </div>
      </ScrollArea>

      {chunks.length > 0 && (
        <div className="border-t px-4 py-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowChunks(!showChunks)}
          >
            {showChunks ? "Hide" : "Show"} sources ({citedDocuments.length})
          </Button>
          {showChunks && (
            <div className="mt-2 max-h-48 space-y-2 overflow-y-auto">
              {citedDocuments.map((documentName, i) => (
                <div
                  key={documentName}
                  className="rounded-md bg-muted p-2 text-xs"
                >
                  <p className="font-medium">Source {i + 1}</p>
                  <p className="mt-1 line-clamp-1">{documentName}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      <div className="border-t p-4">
        <MessageInput
          onSend={handleSend}
          disabled={state !== "idle"}
          isThinking={state !== "idle"}
        />
      </div>
    </div>
  );
}
