"use client";

import { cn } from "@/lib/utils";
import { renderMarkdown } from "@/lib/markdown/render-markdown";

interface MessageSourceDocument {
  documentId: string;
  documentName: string;
  chunkIds: string[];
}

interface MessageBubbleProps {
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
  reliabilityPercent?: number | null;
  sourceDocuments?: MessageSourceDocument[];
  onSourceClick?: (source: MessageSourceDocument) => void;
}

export function MessageBubble({
  role,
  content,
  timestamp,
  reliabilityPercent,
  sourceDocuments = [],
  onSourceClick,
}: MessageBubbleProps) {
  const isUser = role === "user";

  return (
    <div
      className={cn("flex w-full", isUser ? "justify-end" : "justify-start")}
    >
      <div
        className={cn(
          "max-w-[80%] rounded-lg px-4 py-2",
          isUser
            ? "bg-primary text-primary-foreground"
            : "bg-muted text-foreground",
        )}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap text-sm">{content}</p>
        ) : (
          renderMarkdown(content)
        )}
        {!isUser && sourceDocuments.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1">
            {sourceDocuments.map((documentName) => (
              <button
                key={documentName.documentId}
                type="button"
                onClick={() => onSourceClick?.(documentName)}
                className="inline-flex cursor-pointer items-center rounded-full border border-border bg-background px-2 py-0.5 text-xs text-muted-foreground transition-colors hover:bg-accent"
              >
                {documentName.documentName}
              </button>
            ))}
          </div>
        )}
        {!isUser && reliabilityPercent !== undefined && reliabilityPercent !== null && (
          <p className="mt-1 text-xs text-muted-foreground">
            Fiabilite: {reliabilityPercent}%
          </p>
        )}
        {timestamp && (
          <p
            className={cn(
              "mt-1 text-xs",
              isUser
                ? "text-primary-foreground/70"
                : "text-muted-foreground",
            )}
          >
            {new Date(timestamp).toLocaleTimeString()}
          </p>
        )}
      </div>
    </div>
  );
}
