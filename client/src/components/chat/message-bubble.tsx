"use client";

import { cn } from "@/lib/utils";
import { renderMarkdown } from "@/lib/markdown/render-markdown";

interface MessageBubbleProps {
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
  reliabilityPercent?: number | null;
}

export function MessageBubble({
  role,
  content,
  timestamp,
  reliabilityPercent,
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
