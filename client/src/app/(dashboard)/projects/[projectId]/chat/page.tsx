"use client";

import { useParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { ChatPanel } from "@/components/chat/chat-panel";
import { ConversationSidebar } from "@/components/chat/conversation-sidebar";
import { useProject } from "@/lib/hooks/use-projects";

export default function ChatPage() {
  const params = useParams<{ projectId: string }>();
  const { data: project } = useProject(params.projectId);
  const isProjectReindexing = project?.reindex_status === "in_progress";
  const t = useTranslations("projects.chatPage");

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
              ? t("reindexingMessage", { progress: project?.reindex_progress, total: project?.reindex_total })
              : undefined
          }
        />
      </div>
    </div>
  );
}
