"use client";

import { useEffect, useRef, useState } from "react";
import { useConversation, useRenameConversation } from "@/lib/hooks/use-chat";

interface ConversationTitleProps {
  projectId: string;
  conversationId: string;
}

export function ConversationTitle({ projectId, conversationId }: ConversationTitleProps) {
  const { data: conversation } = useConversation(projectId, conversationId);
  const rename = useRenameConversation(projectId);
  const [editing, setEditing] = useState(false);
  const [value, setValue] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (editing) {
      setValue(conversation?.title ?? "");
      inputRef.current?.focus();
      inputRef.current?.select();
    }
  }, [editing, conversation?.title]);

  function handleSave() {
    const trimmed = value.trim();
    if (trimmed && trimmed !== conversation?.title) {
      rename.mutate({ conversationId, title: trimmed });
    }
    setEditing(false);
  }

  if (editing) {
    return (
      <input
        ref={inputRef}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onBlur={handleSave}
        onKeyDown={(e) => {
          if (e.key === "Enter") handleSave();
          if (e.key === "Escape") setEditing(false);
        }}
        className="w-40 border-b border-current bg-transparent text-sm outline-none"
      />
    );
  }

  return (
    <span
      className="cursor-text hover:opacity-70"
      title="Cliquer pour renommer"
      onClick={() => setEditing(true)}
    >
      {conversation?.title ?? ""}
    </span>
  );
}
