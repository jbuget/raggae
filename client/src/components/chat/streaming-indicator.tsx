"use client";

import { useTranslations } from "next-intl";

export function StreamingIndicator() {
  const t = useTranslations("chat.streamingIndicator");

  return (
    <div className="flex items-center gap-2 px-4 py-2">
      <div className="flex gap-1">
        <span className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground [animation-delay:0ms]" />
        <span className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground [animation-delay:150ms]" />
        <span className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground [animation-delay:300ms]" />
      </div>
      <span className="text-sm text-muted-foreground">{t("thinking")}</span>
    </div>
  );
}
