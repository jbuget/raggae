"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { CheckIcon, CopyIcon } from "lucide-react";

interface CopyButtonProps {
  text: string;
}

export function CopyButton({ text }: CopyButtonProps) {
  const t = useTranslations("chat.messageBubble");
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <button
      type="button"
      onClick={handleCopy}
      className="inline-flex cursor-pointer items-center gap-1 self-end rounded px-2 py-1 text-sm text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100 hover:text-foreground"
      title={t("copyMessage")}
    >
      {copied ? (
        <CheckIcon className="size-4" data-testid="copy-button-check-icon" />
      ) : (
        <CopyIcon className="size-4" data-testid="copy-button-copy-icon" />
      )}
    </button>
  );
}
