"use client";

import { useParams } from "next/navigation";
import { ChatPanel } from "@/components/chat/chat-panel";
import { ConversationSidebar } from "@/components/chat/conversation-sidebar";

export default function ChatPage() {
  const params = useParams<{ projectId: string }>();

  return (
    <div className="-m-6 flex h-[calc(100vh-3.5rem)]">
      <div className="hidden lg:block">
        <ConversationSidebar />
      </div>
      <div className="flex-1">
        <ChatPanel projectId={params.projectId} conversationId={null} />
      </div>
    </div>
  );
}
