"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import type { ConversationResponse } from "@/lib/types/api";

interface ConversationLinkProps {
  conversation: ConversationResponse;
  projectId: string;
  isActive: boolean;
}

export function ConversationLink({ conversation, projectId, isActive }: ConversationLinkProps) {
  const href = `/projects/${projectId}/chat/${conversation.id}`;

  const label =
    conversation.title ||
    new Date(conversation.created_at).toLocaleDateString(undefined, {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });

  return (
    <Link
      href={href}
      className={cn(
        "block min-w-0 flex-1 truncate px-3 py-1 text-sm",
        isActive ? "text-primary" : "text-muted-foreground",
      )}
      title={label}
    >
      {label}
    </Link>
  );
}

export function useConversationActive(conversationId: string) {
  const pathname = usePathname();
  return pathname.includes(conversationId);
}
