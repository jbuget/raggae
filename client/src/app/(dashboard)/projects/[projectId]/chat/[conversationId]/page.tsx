"use client";

import { useParams } from "next/navigation";
import { ChatTemplate } from "@/components/templates/project/chat-template";

export default function ConversationPage() {
  const params = useParams<{ projectId: string; conversationId: string }>();
  return <ChatTemplate projectId={params.projectId} conversationId={params.conversationId} />;
}
