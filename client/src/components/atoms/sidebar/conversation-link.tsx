"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import type { ConversationResponse } from "@/lib/types/api";

interface ConversationLinkProps {
  conversation: ConversationResponse;
  projectId: string;
}

export function ConversationLink({ conversation, projectId }: ConversationLinkProps) {
  const pathname = usePathname();
  const isActive = pathname.includes(conversation.id);
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
        "block truncate rounded-md px-3 py-1.5 text-sm transition-colors",
        isActive
          ? "bg-primary/10 text-primary"
          : "text-muted-foreground hover:bg-muted hover:text-foreground",
      )}
      title={label}
    >
      {label}
    </Link>
  );
}
