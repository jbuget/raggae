"use client";

import { useParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { ChatPanel } from "@/components/chat/chat-panel";
import { useConversation } from "@/lib/hooks/use-chat";
import { useProject } from "@/lib/hooks/use-projects";

export default function ConversationPage() {
  const params = useParams<{ projectId: string; conversationId: string }>();
  const { data: project } = useProject(params.projectId);
  const { data: conversation } = useConversation(params.projectId, params.conversationId);
  const isProjectReindexing = project?.reindex_status === "in_progress";
  const t = useTranslations("projects.chatPage");

  return (
    <div className="-m-6 flex h-[calc(100vh-3.5rem)]">
<div className="flex flex-1 flex-col">
        <div className="flex h-14 shrink-0 items-center gap-2 border-b px-6 text-sm">
          <span className="font-bold">{project?.name}</span>
          {conversation?.title && (
            <>
              <span className="text-muted-foreground">›</span>
              <span className="text-muted-foreground">{conversation.title}</span>
            </>
          )}
        </div>
        <div className="min-h-0 flex-1">
        <ChatPanel
          projectId={params.projectId}
          conversationId={params.conversationId}
          disabled={isProjectReindexing}
          disabledMessage={
            isProjectReindexing
              ? t("reindexingMessage", { progress: project?.reindex_progress, total: project?.reindex_total })
              : undefined
          }
        />
        </div>
      </div>
    </div>
  );
}
