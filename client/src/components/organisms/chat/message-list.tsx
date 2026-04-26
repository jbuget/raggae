"use client";

import { useEffect, useRef, useState } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { MessageBubble } from "@/components/molecules/chat/message-bubble";
import { StreamingIndicator } from "@/components/molecules/chat/streaming-indicator";
import { ScrollToBottomButton } from "@/components/atoms/chat/scroll-to-bottom-button";
import type { MessageResponse } from "@/lib/types/api";

interface MessageSourceDocument {
  documentId: string;
  documentName: string;
  chunkIds: string[];
}

interface MessageListProps {
  messages: MessageResponse[];
  streamedContent: string;
  isStreaming: boolean;
  isSending: boolean;
  streamError: string | null;
  streamedSourceDocuments: MessageSourceDocument[];
  onSourceClick: (source: MessageSourceDocument) => void;
}

function getMessageSourceDocuments(message: MessageResponse): MessageSourceDocument[] {
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

export function MessageList({
  messages,
  streamedContent,
  isStreaming,
  isSending,
  streamError,
  streamedSourceDocuments,
  onSourceClick,
}: MessageListProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [isAtBottom, setIsAtBottom] = useState(true);
  const isAtBottomRef = useRef(true);

  const lastMessage = messages.at(-1);
  const shouldRenderTransientAssistant =
    streamedContent.length > 0 &&
    (isStreaming || lastMessage?.role !== "assistant");

  function scrollToBottom() {
    const viewport = scrollRef.current?.querySelector<HTMLElement>(
      "[data-slot='scroll-area-viewport']",
    );
    if (viewport) {
      viewport.scrollTop = viewport.scrollHeight;
    }
  }

  useEffect(() => {
    if (isAtBottomRef.current) scrollToBottom();
  }, [messages, streamedContent]);

  useEffect(() => {
    const viewport = scrollRef.current?.querySelector<HTMLElement>(
      "[data-slot='scroll-area-viewport']",
    );
    if (!viewport) return;
    function handleScroll() {
      const { scrollTop, scrollHeight, clientHeight } = viewport!;
      const atBottom = scrollHeight - scrollTop - clientHeight < 50;
      isAtBottomRef.current = atBottom;
      setIsAtBottom(atBottom);
    }
    viewport.addEventListener("scroll", handleScroll);
    return () => viewport.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <div className="relative h-full min-h-0">
      <ScrollArea className="h-full" ref={scrollRef}>
        <div className="space-y-4 px-8 pt-4 pb-36">
          {messages.map((msg) => (
            <div key={msg.id} className="space-y-2">
              <MessageBubble
                role={msg.role as "user" | "assistant"}
                content={msg.content}
                sourceDocuments={msg.role === "assistant" ? getMessageSourceDocuments(msg) : []}
                onSourceClick={onSourceClick}
                timestamp={msg.created_at}
              />
            </div>
          ))}

          {(isSending || (isStreaming && streamedContent.length === 0)) && (
            <StreamingIndicator />
          )}

          {streamError && !isStreaming && !isSending && (
            <p className="text-sm text-destructive">{streamError}</p>
          )}

          {shouldRenderTransientAssistant && (
            <div className="space-y-2">
              <MessageBubble
                role="assistant"
                content={streamedContent}
                sourceDocuments={streamedSourceDocuments}
                onSourceClick={onSourceClick}
              />
            </div>
          )}
        </div>
      </ScrollArea>

      {!isAtBottom && (
        <div className="absolute bottom-34 left-1/2 z-20 -translate-x-1/2">
          <ScrollToBottomButton onClick={scrollToBottom} />
        </div>
      )}
    </div>
  );
}
