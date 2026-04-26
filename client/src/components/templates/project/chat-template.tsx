"use client";

import { useParams } from "next/navigation";
import { WorkspaceTemplate } from "@/components/templates/workspace-template";
import { ChatPanel } from "@/components/organisms/chat/chat-panel";
import { useConversation } from "@/lib/hooks/use-chat";
import { useProject } from "@/lib/hooks/use-projects";
import { useTranslations } from "next-intl";

type ChatTemplateProps = {
  projectId: string;
  conversationId: string | null;
};

export function ChatTemplate({ projectId, conversationId }: ChatTemplateProps) {
  const { data: project } = useProject(projectId);
  const { data: conversation } = useConversation(
    conversationId ? projectId : undefined,
    conversationId ?? undefined,
  );
  const isProjectReindexing = project?.reindex_status === "in_progress";
  const t = useTranslations("projects.chatPage");

  const breadcrumb = [
    { label: project?.name ?? "" },
    ...(conversation?.title ? [{ label: conversation.title }] : []),
  ];

  return (
    <WorkspaceTemplate breadcrumb={breadcrumb}>
      <ChatPanel
        projectId={projectId}
        conversationId={conversationId}
        disabled={isProjectReindexing}
        disabledMessage={
          isProjectReindexing
            ? t("reindexingMessage", {
                progress: project?.reindex_progress,
                total: project?.reindex_total,
              })
            : undefined
        }
      />
    </WorkspaceTemplate>
  );
}
