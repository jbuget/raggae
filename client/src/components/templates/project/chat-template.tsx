"use client";

import { Star } from "lucide-react";
import { useTranslations } from "next-intl";
import { WorkspaceTemplate } from "@/components/templates/workspace-template";
import { ChatPanel } from "@/components/organisms/chat/chat-panel";
import { Button } from "@/components/ui/button";
import { useConversation, useToggleFavoriteConversation } from "@/lib/hooks/use-chat";
import { useProject } from "@/lib/hooks/use-projects";
import { cn } from "@/lib/utils";

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
  const { mutate: toggleFavorite } = useToggleFavoriteConversation(projectId);
  const isProjectReindexing = project?.reindex_status === "in_progress";
  const t = useTranslations("chat.sidebar");
  const tChat = useTranslations("projects.chatPage");

  const breadcrumb = [
    { label: project?.name ?? "" },
    ...(conversation?.title ? [{ label: conversation.title }] : []),
  ];

  const actions = conversationId ? (
    <Button
      variant="ghost"
      size="icon"
      className="h-8 w-8"
      aria-label={conversation?.is_favorite ? t("removeFromFavorites") : t("addToFavorites")}
      title={conversation?.is_favorite ? t("removeFromFavorites") : t("addToFavorites")}
      onClick={() => toggleFavorite(conversationId)}
    >
      <Star
        className={cn(
          "h-4 w-4",
          conversation?.is_favorite && "fill-current",
        )}
      />
    </Button>
  ) : undefined;

  return (
    <WorkspaceTemplate breadcrumb={breadcrumb} actions={actions}>
      <ChatPanel
        projectId={projectId}
        conversationId={conversationId}
        disabled={isProjectReindexing}
        disabledMessage={
          isProjectReindexing
            ? tChat("reindexingMessage", {
                progress: project?.reindex_progress,
                total: project?.reindex_total,
              })
            : undefined
        }
      />
    </WorkspaceTemplate>
  );
}
