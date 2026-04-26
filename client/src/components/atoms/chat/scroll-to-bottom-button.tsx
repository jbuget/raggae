"use client";

import { useTranslations } from "next-intl";
import { ArrowDown } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ScrollToBottomButtonProps {
  onClick: () => void;
}

export function ScrollToBottomButton({ onClick }: ScrollToBottomButtonProps) {
  const t = useTranslations("chat.panel");

  return (
    <Button
      variant="outline"
      size="icon"
      className="h-9 w-9 rounded-full border border-border shadow-sm hover:bg-muted"
      style={{ backgroundColor: "var(--message-input-bg)" }}
      onClick={onClick}
      aria-label={t("scrollToBottom")}
    >
      <ArrowDown className="size-4" />
    </Button>
  );
}
