"use client";

import { useParams } from "next/navigation";
import { ChatPanel } from "@/components/chat/chat-panel";
import { ConversationSidebar } from "@/components/chat/conversation-sidebar";
import { useProject } from "@/lib/hooks/use-projects";

export default function ChatPage() {
  const params = useParams<{ projectId: string }>();
  const { data: project } = useProject(params.projectId);
  const isProjectReindexing = project?.reindex_status === "in_progress";

  return (
    <div className="-m-6 flex h-[calc(100vh-3.5rem)]">
      <div className="hidden h-full lg:block">
        <ConversationSidebar />
      </div>
      <div className="flex-1">
        <ChatPanel
          projectId={params.projectId}
          conversationId={null}
          disabled={isProjectReindexing}
          disabledMessage={
            isProjectReindexing
              ? `Reindexation en cours (${project?.reindex_progress}/${project?.reindex_total}). Le chat est temporairement desactive.`
              : undefined
          }
        />
      </div>
    </div>
  );
}
