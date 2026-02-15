"use client";

import { useState } from "react";
import { Loader2Icon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

interface MessageInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  isThinking?: boolean;
}

export function MessageInput({
  onSend,
  disabled = false,
  isThinking = false,
}: MessageInputProps) {
  const [message, setMessage] = useState("");

  const isDisabled = !message.trim() || disabled;

  function handleSubmit() {
    if (isDisabled) return;
    onSend(message.trim());
    setMessage("");
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }

  return (
    <div className="flex gap-2">
      <Textarea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type a message..."
        rows={1}
        className="min-h-[40px] resize-none"
        aria-label="Message"
      />
      <Button onClick={handleSubmit} disabled={isDisabled}>
        {isThinking ? (
          <span className="inline-flex items-center gap-2">
            <Loader2Icon className="size-4 animate-spin" />
            Thinking...
          </span>
        ) : (
          "Send"
        )}
      </Button>
    </div>
  );
}
