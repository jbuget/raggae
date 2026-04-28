"use client";

import { useConversation } from "@/lib/hooks/use-chat";

interface ConversationTitleProps {
  projectId: string;
  conversationId: string;
}

export function ConversationTitle({ projectId, conversationId }: ConversationTitleProps) {
  const { data: conversation } = useConversation(projectId, conversationId);
  return <>{conversation?.title ?? ""}</>;
}
