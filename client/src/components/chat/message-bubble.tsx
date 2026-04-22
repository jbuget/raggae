"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { CheckIcon, CopyIcon } from "lucide-react";
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
  const t = useTranslations("chat.messageBubble");
  const isUser = role === "user";
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div
      className={cn("group flex w-full", isUser ? "justify-end" : "justify-start")}
    >
      <div className={cn("flex max-w-[80%] flex-col gap-1", isUser ? "items-end" : "items-start")}>
        <div
          className={cn(
            "rounded-lg px-4 py-2",
            isUser
              ? "text-foreground"
              : "bg-transparent text-foreground",
          )}
          style={isUser ? { backgroundColor: "hsl(var(--bg-300) / var(--tw-bg-opacity, 1))" } : undefined}
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
        {timestamp && (
          <p
            className={cn(
              "mt-1 text-xs",
              isUser
                ? "text-foreground/50"
                : "text-muted-foreground",
            )}
          >
            {new Date(timestamp).toLocaleTimeString()}
          </p>
        )}
        </div>
        <button
          type="button"
          onClick={handleCopy}
          className="inline-flex cursor-pointer items-center gap-1 self-end rounded px-2 py-1 text-sm text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100 hover:text-foreground"
          title={t("copyMessage")}
        >
          {copied ? (
            <CheckIcon className="size-4" />
          ) : (
            <CopyIcon className="size-4" />
          )}
        </button>
      </div>
    </div>
  );
}
