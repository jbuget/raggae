"use client";

import { useTranslations } from "next-intl";
import { StreamingDot } from "@/components/atoms/chat/streaming-dot";

export function StreamingIndicator() {
  const t = useTranslations("chat.streamingIndicator");

  return (
    <div className="flex items-center gap-2 px-4 py-2">
      <div className="flex gap-1">
        <StreamingDot delay={0} />
        <StreamingDot delay={150} />
        <StreamingDot delay={300} />
      </div>
      <span className="text-sm text-muted-foreground">{t("thinking")}</span>
    </div>
  );
}
