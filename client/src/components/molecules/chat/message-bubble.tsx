"use client";

import { cn } from "@/lib/utils";
import { renderMarkdown } from "@/lib/markdown/render-markdown";
import { CopyButton } from "@/components/atoms/chat/copy-button";
import { SourceBadge } from "@/components/atoms/chat/source-badge";

interface MessageSourceDocument {
  documentId: string;
  documentName: string;
  chunkIds: string[];
}

interface MessageBubbleProps {
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
  sourceDocuments?: MessageSourceDocument[];
  onSourceClick?: (source: MessageSourceDocument) => void;
}

export function MessageBubble({
  role,
  content,
  timestamp,
  sourceDocuments = [],
  onSourceClick,
}: MessageBubbleProps) {
  const isUser = role === "user";

  return (
    <div className={cn("group flex w-full", isUser ? "justify-end" : "justify-start")}>
      <div className={cn("flex max-w-[80%] flex-col gap-1", isUser ? "items-end" : "items-start")}>
        <div
          className={cn(
            "rounded-lg px-4 py-2",
            isUser ? "text-foreground" : "bg-transparent text-foreground",
          )}
          style={isUser ? { backgroundColor: "hsl(var(--bg-300) / var(--tw-bg-opacity, 1))" } : undefined}
        >
          {isUser ? (
            <p className="whitespace-pre-wrap text-base">{content}</p>
          ) : (
            renderMarkdown(content)
          )}
          {!isUser && sourceDocuments.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-1">
              {sourceDocuments.map((doc) => (
                <SourceBadge
                  key={doc.documentId}
                  name={doc.documentName}
                  onClick={() => onSourceClick?.(doc)}
                />
              ))}
            </div>
          )}
          {timestamp && (
            <p className={cn("mt-1 text-xs", isUser ? "text-foreground/50" : "text-muted-foreground")}>
              {new Date(timestamp).toLocaleTimeString()}
            </p>
          )}
        </div>
        <CopyButton text={content} />
      </div>
    </div>
  );
}
