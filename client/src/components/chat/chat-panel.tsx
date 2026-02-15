"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { ScrollArea } from "@/components/ui/scroll-area";
import { MessageBubble } from "./message-bubble";
import { MessageInput } from "./message-input";
import { StreamingIndicator } from "./streaming-indicator";
import { useMessages, useSendMessage } from "@/lib/hooks/use-chat";
import { useDocumentChunks } from "@/lib/hooks/use-documents";
import type { MessageResponse } from "@/lib/types/api";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

interface ChatPanelProps {
  projectId: string;
  conversationId: string | null;
}

interface MessageSourceDocument {
  documentId: string;
  documentName: string;
}

export function ChatPanel({ projectId, conversationId }: ChatPanelProps) {
  const router = useRouter();
  const { data: existingMessages } = useMessages(projectId, conversationId);
  const { send, state, streamedContent, chunks } = useSendMessage(projectId);
  const [optimisticMessages, setOptimisticMessages] = useState<MessageResponse[]>([]);
  const [showChunks, setShowChunks] = useState(false);
  const [selectedSourceDocument, setSelectedSourceDocument] =
    useState<MessageSourceDocument | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const { data: selectedDocumentChunks, isLoading: isSelectedDocumentLoading } =
    useDocumentChunks(projectId, selectedSourceDocument?.documentId ?? null);

  const messages = useMemo(() => {
    if (existingMessages) return [...existingMessages, ...optimisticMessages];
    return optimisticMessages;
  }, [existingMessages, optimisticMessages]);
  const lastMessage = messages.at(-1);
  const citedDocuments = useMemo<MessageSourceDocument[]>(() => {
    const unique = new Map<string, MessageSourceDocument>();
    for (const chunk of chunks) {
      if (!unique.has(chunk.document_id)) {
        unique.set(chunk.document_id, {
          documentId: chunk.document_id,
          documentName: chunk.document_file_name || chunk.document_id,
        });
      }
    }
    return [...unique.values()];
  }, [chunks]);

  useEffect(() => {
    const viewport = scrollRef.current?.querySelector<HTMLElement>(
      "[data-slot='scroll-area-viewport']",
    );
    if (viewport) {
      viewport.scrollTop = viewport.scrollHeight;
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

  function getMessageSourceDocuments(
    message: MessageResponse,
  ): MessageSourceDocument[] {
    const documents = message.source_documents ?? [];
    const unique = new Map<string, MessageSourceDocument>();
    for (const document of documents) {
      if (!unique.has(document.document_id)) {
        unique.set(document.document_id, {
          documentId: document.document_id,
          documentName: document.document_file_name || document.document_id,
        });
      }
    }
    return [...unique.values()];
  }

  return (
    <div className="flex h-full min-h-0 flex-col">
      <ScrollArea className="min-h-0 flex-1 p-4" ref={scrollRef}>
        <div className="space-y-4">
          {messages.map((msg) => {
            const messageSourceDocuments = getMessageSourceDocuments(msg);
            return (
              <div key={msg.id} className="space-y-2">
                <MessageBubble
                  role={msg.role as "user" | "assistant"}
                  content={msg.content}
                  sourceDocuments={
                    msg.role === "assistant" ? messageSourceDocuments : []
                  }
                  onSourceClick={setSelectedSourceDocument}
                  reliabilityPercent={msg.reliability_percent}
                  timestamp={msg.created_at}
                />
              </div>
            );
          })}

          {state === "sending" && <StreamingIndicator />}

          {shouldRenderTransientAssistant && (
            <div className="space-y-2">
              <MessageBubble
                role="assistant"
                content={streamedContent}
                sourceDocuments={citedDocuments}
                onSourceClick={setSelectedSourceDocument}
              />
            </div>
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
              {citedDocuments.map((document, i) => (
                <div
                  key={document.documentId}
                  className="rounded-md bg-muted p-2 text-xs"
                >
                  <p className="font-medium">Source {i + 1}</p>
                  <p className="mt-1 line-clamp-1">{document.documentName}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      <div className="sticky bottom-0 border-t bg-background p-4">
        <MessageInput
          onSend={handleSend}
          disabled={state !== "idle"}
          isThinking={state !== "idle"}
        />
      </div>

      <Dialog
        open={selectedSourceDocument !== null}
        onOpenChange={(open) => {
          if (!open) {
            setSelectedSourceDocument(null);
          }
        }}
      >
        <DialogContent className="max-h-[80vh] max-w-3xl overflow-hidden">
          <DialogHeader>
            <DialogTitle>
              {selectedSourceDocument?.documentName || "Document preview"}
            </DialogTitle>
          </DialogHeader>
          <div className="max-h-[60vh] overflow-y-auto rounded-md border bg-muted/20 p-3">
            {isSelectedDocumentLoading && (
              <p className="text-sm text-muted-foreground">Loading document content...</p>
            )}
            {!isSelectedDocumentLoading &&
              (!selectedDocumentChunks || selectedDocumentChunks.chunks.length === 0) && (
                <p className="text-sm text-muted-foreground">
                  No indexed content found for this document.
                </p>
              )}
            {!isSelectedDocumentLoading && selectedDocumentChunks && (
              <div className="space-y-3">
                {selectedDocumentChunks.chunks
                  .sort((a, b) => a.chunk_index - b.chunk_index)
                  .map((chunk) => (
                    <div key={chunk.id} className="space-y-1 rounded-md border bg-background p-2">
                      <p className="text-xs text-muted-foreground">
                        Chunk #{chunk.chunk_index}
                      </p>
                      <p className="whitespace-pre-wrap text-sm">{chunk.content}</p>
                    </div>
                  ))}
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
