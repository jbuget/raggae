"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { ScrollArea } from "@/components/ui/scroll-area";
import { MessageBubble } from "./message-bubble";
import { MessageInput } from "./message-input";
import { StreamingIndicator } from "./streaming-indicator";
import { useMessages, useSendMessage } from "@/lib/hooks/use-chat";
import { useAuth } from "@/lib/hooks/use-auth";
import type { MessageResponse } from "@/lib/types/api";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { getDocumentFileBlob } from "@/lib/api/documents";

interface ChatPanelProps {
  projectId: string;
  conversationId: string | null;
  disabled?: boolean;
  disabledMessage?: string;
}

interface MessageSourceDocument {
  documentId: string;
  documentName: string;
  chunkIds: string[];
}

export function ChatPanel({
  projectId,
  conversationId,
  disabled = false,
  disabledMessage,
}: ChatPanelProps) {
  const router = useRouter();
  const { token } = useAuth();
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(
    conversationId,
  );
  const { data: existingMessages } = useMessages(projectId, currentConversationId);
  const { send, state, streamedContent, chunks } = useSendMessage(projectId);
  const [optimisticMessages, setOptimisticMessages] = useState<MessageResponse[]>([]);
  const [showChunks, setShowChunks] = useState(false);
  const [selectedSourceDocument, setSelectedSourceDocument] =
    useState<MessageSourceDocument | null>(null);
  const [selectedDocumentUrl, setSelectedDocumentUrl] = useState<string | null>(null);
  const [selectedDocumentType, setSelectedDocumentType] = useState<string | null>(null);
  const [isSelectedDocumentLoading, setIsSelectedDocumentLoading] = useState(false);
  const [selectedDocumentError, setSelectedDocumentError] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setCurrentConversationId(conversationId);
  }, [conversationId]);

  const messages = useMemo(() => {
    if (existingMessages) return [...existingMessages, ...optimisticMessages];
    return optimisticMessages;
  }, [existingMessages, optimisticMessages]);
  const lastMessage = messages.at(-1);
  const citedDocuments = useMemo<MessageSourceDocument[]>(() => {
    const unique = new Map<string, MessageSourceDocument>();
    for (const chunk of chunks) {
      const existing = unique.get(chunk.document_id);
      if (existing) {
        existing.chunkIds.push(chunk.chunk_id);
      } else {
        unique.set(chunk.document_id, {
          documentId: chunk.document_id,
          documentName: chunk.document_file_name || chunk.document_id,
          chunkIds: [chunk.chunk_id],
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

  useEffect(() => {
    return () => {
      if (selectedDocumentUrl) {
        URL.revokeObjectURL(selectedDocumentUrl);
      }
    };
  }, [selectedDocumentUrl]);

  async function handleSend(content: string) {
    if (disabled) return;
    const effectiveConversationId = currentConversationId ?? conversationId;
    const userMessage: MessageResponse = {
      id: `temp-${Date.now()}`,
      conversation_id: effectiveConversationId ?? "",
      role: "user",
      content,
      created_at: new Date().toISOString(),
    };

    setOptimisticMessages((prev) => [...prev, userMessage]);

    await send(
      {
        message: content,
        conversation_id: effectiveConversationId,
        start_new_conversation: !effectiveConversationId,
      },
      (newConversationId) => {
        setOptimisticMessages([]);
        setCurrentConversationId(newConversationId);
        if (!effectiveConversationId) {
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
          chunkIds: document.chunk_ids ?? [],
        });
      }
    }
    return [...unique.values()];
  }

  async function handleSourceClick(source: MessageSourceDocument) {
    if (!token) return;

    if (selectedDocumentUrl) {
      URL.revokeObjectURL(selectedDocumentUrl);
    }
    setSelectedSourceDocument(source);
    setSelectedDocumentUrl(null);
    setSelectedDocumentType(null);
    setSelectedDocumentError(null);
    setIsSelectedDocumentLoading(true);
    try {
      const blob = await getDocumentFileBlob(token, projectId, source.documentId);
      const objectUrl = URL.createObjectURL(blob);
      setSelectedDocumentUrl(objectUrl);
      setSelectedDocumentType(blob.type || "application/octet-stream");
    } catch {
      setSelectedDocumentError("Unable to load this document.");
    } finally {
      setIsSelectedDocumentLoading(false);
    }
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
                  onSourceClick={handleSourceClick}
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
                onSourceClick={handleSourceClick}
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
        {disabled && (
          <p className="mb-2 text-xs text-amber-700">
            {disabledMessage || "Chat is temporarily disabled for this project."}
          </p>
        )}
        <MessageInput
          onSend={handleSend}
          disabled={disabled || state !== "idle"}
          isThinking={!disabled && state !== "idle"}
        />
      </div>

      <Dialog
        open={selectedSourceDocument !== null}
        onOpenChange={(open) => {
          if (!open) {
            setSelectedSourceDocument(null);
            setSelectedDocumentType(null);
            setSelectedDocumentError(null);
            if (selectedDocumentUrl) {
              URL.revokeObjectURL(selectedDocumentUrl);
            }
            setSelectedDocumentUrl(null);
          }
        }}
      >
        <DialogContent className="h-[94vh] max-h-[94vh] w-[98vw] max-w-[98vw] sm:max-w-none overflow-hidden p-4 sm:p-6">
          <DialogHeader>
            <DialogTitle>
              {selectedSourceDocument?.documentName || "Document preview"}
            </DialogTitle>
            {selectedSourceDocument?.chunkIds &&
              selectedSourceDocument.chunkIds.length > 0 && (
                <div className="mt-1 space-y-1">
                  {selectedSourceDocument.chunkIds.map((chunkId) => (
                    <div
                      key={chunkId}
                      className="flex items-center gap-2 text-xs text-muted-foreground"
                    >
                      <code className="rounded bg-muted px-1.5 py-0.5 font-mono">
                        {chunkId}
                      </code>
                      <button
                        type="button"
                        className="rounded px-1.5 py-0.5 text-xs hover:bg-muted"
                        onClick={() => navigator.clipboard.writeText(chunkId)}
                        title="Copy chunk ID"
                      >
                        Copy
                      </button>
                    </div>
                  ))}
                </div>
              )}
          </DialogHeader>
          <div className="h-full min-h-0 overflow-y-auto rounded-md border bg-muted/20 p-3">
            {isSelectedDocumentLoading && (
              <p className="text-sm text-muted-foreground">Loading document...</p>
            )}
            {!isSelectedDocumentLoading && selectedDocumentError && (
              <p className="text-sm text-destructive">{selectedDocumentError}</p>
            )}
            {!isSelectedDocumentLoading &&
              !selectedDocumentError &&
              selectedDocumentUrl &&
              selectedDocumentType?.startsWith("image/") && (
                <img
                  src={selectedDocumentUrl}
                  alt={selectedSourceDocument?.documentName || "Document"}
                  className="mx-auto max-h-[84vh] object-contain"
                />
              )}
            {!isSelectedDocumentLoading &&
              !selectedDocumentError &&
              selectedDocumentUrl &&
              selectedDocumentType === "application/pdf" && (
                <iframe
                  src={selectedDocumentUrl}
                  title={selectedSourceDocument?.documentName || "Document"}
                  className="h-[84vh] w-full rounded-md border"
                />
              )}
            {!isSelectedDocumentLoading &&
              !selectedDocumentError &&
              selectedDocumentUrl &&
              selectedDocumentType?.startsWith("text/") && (
                <iframe
                  src={selectedDocumentUrl}
                  title={selectedSourceDocument?.documentName || "Document"}
                  className="h-[84vh] w-full rounded-md border bg-background"
                />
              )}
            {!isSelectedDocumentLoading &&
              !selectedDocumentError &&
              selectedDocumentUrl &&
              !selectedDocumentType?.startsWith("image/") &&
              selectedDocumentType !== "application/pdf" &&
              !selectedDocumentType?.startsWith("text/") && (
                <div className="space-y-3">
                  <p className="text-sm text-muted-foreground">
                    Preview is not available for this file type.
                  </p>
                  <a
                    href={selectedDocumentUrl}
                    download={selectedSourceDocument?.documentName}
                    className="inline-flex rounded-md border bg-background px-3 py-2 text-sm"
                  >
                    Download document
                  </a>
                </div>
              )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
