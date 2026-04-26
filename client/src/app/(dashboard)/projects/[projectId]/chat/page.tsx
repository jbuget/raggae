"use client";

import { useParams } from "next/navigation";
import { ChatTemplate } from "@/components/templates/project/chat-template";

export default function ChatPage() {
  const params = useParams<{ projectId: string }>();
  return <ChatTemplate projectId={params.projectId} conversationId={null} />;
}
