"use client";

import { useEffect, useRef, useState } from "react";
import { useTranslations } from "next-intl";
import { ArrowUp, Square } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface MessageInputProps {
  onSend: (message: string) => void;
  onStop?: () => void;
  disabled?: boolean;
  isThinking?: boolean;
  hasMessages?: boolean;
}

export function MessageInput({
  onSend,
  onStop,
  disabled = false,
  isThinking = false,
  hasMessages = false,
}: MessageInputProps) {
  const t = useTranslations("chat.input");
  const [message, setMessage] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const canSend = message.trim().length > 0 && !disabled && !isThinking;

  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;
    textarea.style.height = "auto";
    textarea.style.height = `${textarea.scrollHeight}px`;
  }, [message]);

  function handleSubmit() {
    if (!canSend) return;
    onSend(message.trim());
    setMessage("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }

  return (
    <div className="space-y-2">
      <div
        className={cn(
          "rounded-2xl border border-border",
          "transition-[border-color] duration-500",
          "hover:border-foreground/15",
          "focus-within:border-foreground/25",
          "px-4 pt-3",
        )}
        style={{ backgroundColor: "var(--message-input-bg)" }}
      >
        <textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={hasMessages ? t("placeholder") : t("placeholderEmpty")}
          rows={1}
          disabled={disabled}
          className={cn(
            "w-full resize-none bg-transparent pb-2",
            "text-sm leading-relaxed placeholder:text-muted-foreground",
            "outline-none",
            "max-h-40 overflow-y-auto",
            "disabled:cursor-not-allowed disabled:opacity-50",
          )}
          aria-label={t("ariaLabel")}
        />
        <div className="flex items-center justify-end pb-3">
          <Button
            size="icon"
            className={cn(
              "h-8 w-8 rounded-full transition-colors",
              isThinking || canSend
                ? "bg-primary text-primary-foreground hover:bg-primary/90"
                : "bg-muted text-muted-foreground cursor-default",
            )}
            onClick={isThinking ? onStop : handleSubmit}
            disabled={!isThinking && !canSend}
            aria-label={isThinking ? t("stop") : t("send")}
          >
            {isThinking ? (
              <Square className="size-3 fill-current" />
            ) : (
              <ArrowUp className="size-4" />
            )}
          </Button>
        </div>
      </div>
      <p className="text-center text-xs text-muted-foreground">{t("disclaimer")}</p>
    </div>
  );
}
