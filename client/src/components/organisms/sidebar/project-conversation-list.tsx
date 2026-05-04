"use client";

import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";
import { useTranslations } from "next-intl";
import { ConversationItem } from "@/components/molecules/sidebar/conversation-item";
import {
  useConversations,
  useDeleteConversation,
  useRenameConversation,
  useToggleFavoriteConversation,
} from "@/lib/hooks/use-chat";

interface ProjectConversationListProps {
  projectId: string;
}

export function ProjectConversationList({ projectId }: ProjectConversationListProps) {
  const t = useTranslations("chat.sidebar");
  const router = useRouter();
  const pathname = usePathname();
  const { data: conversations, isLoading } = useConversations(projectId, 10);
  const { mutate: deleteConversation } = useDeleteConversation(projectId);
  const { mutate: renameConversation } = useRenameConversation(projectId);
  const { mutate: toggleFavorite } = useToggleFavoriteConversation(projectId);

  const recent = conversations ?? [];

  const handleDelete = (conversationId: string) => {
    deleteConversation(conversationId);
    if (pathname.includes(conversationId)) {
      router.push(`/projects/${projectId}/chat`);
    }
  };

  if (isLoading) {
    return (
      <p className="px-3 py-1 text-xs text-muted-foreground">{t("loading")}</p>
    );
  }

  if (recent.length === 0) {
    return (
      <Link
        href={`/projects/${projectId}/chat`}
        className="block px-3 py-1 text-xs text-muted-foreground hover:text-foreground"
      >
        {t("noConversations")}
      </Link>
    );
  }

  return (
    <div className="space-y-0.5">
      {recent.map((conversation) => (
        <ConversationItem
          key={conversation.id}
          conversation={conversation}
          projectId={projectId}
          onDelete={handleDelete}
          onRename={(id, title) => renameConversation({ conversationId: id, title })}
          onToggleFavorite={(id) => toggleFavorite(id)}
        />
      ))}
    </div>
  );
}
