"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useMessages, useSendMessage } from "@/lib/hooks/use-chat";
import { useAuth } from "@/lib/hooks/use-auth";
import { getDocumentFileBlob } from "@/lib/api/documents";
import { MessageList } from "@/components/organisms/chat/message-list";
import { DocumentPreviewDialog } from "@/components/organisms/chat/document-preview-dialog";
import { SourcesBar } from "@/components/organisms/chat/sources-bar";
import { MessageInput } from "@/components/molecules/chat/message-input";
import type { MessageResponse } from "@/lib/types/api";

interface MessageSourceDocument {
  documentId: string;
  documentName: string;
  chunkIds: string[];
}

interface ChatPanelProps {
  projectId: string;
  conversationId: string | null;
  disabled?: boolean;
  disabledMessage?: string;
}

export function ChatPanel({
  projectId,
  conversationId,
  disabled = false,
  disabledMessage,
}: ChatPanelProps) {
  const t = useTranslations("chat.panel");
  const router = useRouter();
  const { token } = useAuth();

  const [currentConversationId, setCurrentConversationId] = useState<string | null>(conversationId);
  const { data: existingMessages } = useMessages(projectId, currentConversationId);
  const { send, cancel, state, streamedContent, chunks, error: streamError } = useSendMessage(projectId);
  const [optimisticMessages, setOptimisticMessages] = useState<MessageResponse[]>([]);

  const [selectedSource, setSelectedSource] = useState<MessageSourceDocument | null>(null);
  const [selectedDocumentUrl, setSelectedDocumentUrl] = useState<string | null>(null);
  const [selectedDocumentType, setSelectedDocumentType] = useState<string | null>(null);
  const [isDocumentLoading, setIsDocumentLoading] = useState(false);
  const [documentError, setDocumentError] = useState<string | null>(null);

  useEffect(() => {
    setCurrentConversationId(conversationId);
  }, [conversationId]);

  useEffect(() => {
    return () => {
      if (selectedDocumentUrl) URL.revokeObjectURL(selectedDocumentUrl);
    };
  }, [selectedDocumentUrl]);

  const messages = useMemo(() => {
    if (existingMessages) return [...existingMessages, ...optimisticMessages];
    return optimisticMessages;
  }, [existingMessages, optimisticMessages]);

  const streamedSourceDocuments = useMemo<MessageSourceDocument[]>(() => {
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
          router.push(`/projects/${projectId}/chat/${newConversationId}`);
        }
      },
    );
  }

  async function handleSourceClick(source: MessageSourceDocument) {
    if (!token) return;
    if (selectedDocumentUrl) URL.revokeObjectURL(selectedDocumentUrl);
    setSelectedSource(source);
    setSelectedDocumentUrl(null);
    setSelectedDocumentType(null);
    setDocumentError(null);
    setIsDocumentLoading(true);
    try {
      const blob = await getDocumentFileBlob(token, projectId, source.documentId);
      setSelectedDocumentUrl(URL.createObjectURL(blob));
      setSelectedDocumentType(blob.type || "application/octet-stream");
    } catch {
      setDocumentError(t("unableToLoadDocument"));
    } finally {
      setIsDocumentLoading(false);
    }
  }

  function handleDialogClose() {
    setSelectedSource(null);
    setSelectedDocumentType(null);
    setDocumentError(null);
    if (selectedDocumentUrl) URL.revokeObjectURL(selectedDocumentUrl);
    setSelectedDocumentUrl(null);
  }

  return (
    <div className="flex h-full min-h-0 flex-col">
      <div className="relative min-h-0 flex-1">
        <MessageList
          messages={messages}
          streamedContent={streamedContent}
          isStreaming={state === "streaming"}
          isSending={state === "sending"}
          streamError={streamError}
          streamedSourceDocuments={streamedSourceDocuments}
          onSourceClick={handleSourceClick}
        />

        <div className="absolute bottom-0 left-0 right-0 z-10 bg-background">
          <div className="mx-auto w-full max-w-[800px] px-4">
          <SourcesBar sources={streamedSourceDocuments} onSourceClick={handleSourceClick} />
          {disabled && (
            <p className="mb-2 text-xs text-amber-700">
              {disabledMessage || t("disabledDefault")}
            </p>
          )}
          <MessageInput
            onSend={handleSend}
            onStop={cancel}
            disabled={disabled || state !== "idle"}
            isThinking={!disabled && state !== "idle"}
            hasMessages={messages.length > 0}
          />
          </div>
        </div>
      </div>

      <DocumentPreviewDialog
        source={selectedSource}
        documentUrl={selectedDocumentUrl}
        documentType={selectedDocumentType}
        isLoading={isDocumentLoading}
        error={documentError}
        onClose={handleDialogClose}
      />
    </div>
  );
}
