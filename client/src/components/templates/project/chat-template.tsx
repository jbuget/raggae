"use client";

import { WorkspaceTemplate } from "@/components/templates/workspace-template";
import { ChatPanel } from "@/components/organisms/chat/chat-panel";
import { ConversationTitle } from "@/components/organisms/chat/conversation-title";
import { FavoriteConversationButton } from "@/components/organisms/chat/favorite-conversation-button";
import { ProjectName } from "@/components/organisms/project/project-name";

type ChatTemplateProps = {
  projectId: string;
  conversationId: string | null;
};

export function ChatTemplate({ projectId, conversationId }: ChatTemplateProps) {
  const breadcrumb = [
    { label: <ProjectName projectId={projectId} /> },
    ...(conversationId
      ? [{ label: <ConversationTitle projectId={projectId} conversationId={conversationId} /> }]
      : []),
  ];

  const actions = conversationId ? (
    <FavoriteConversationButton projectId={projectId} conversationId={conversationId} />
  ) : undefined;

  return (
    <WorkspaceTemplate breadcrumb={breadcrumb} actions={actions}>
      <ChatPanel projectId={projectId} conversationId={conversationId} />
    </WorkspaceTemplate>
  );
}
