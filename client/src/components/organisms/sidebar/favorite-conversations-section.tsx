"use client";

import { useRouter, usePathname } from "next/navigation";
import { useTranslations } from "next-intl";
import { SidebarSectionHeader } from "@/components/atoms/sidebar/sidebar-section-header";
import { ConversationItem } from "@/components/molecules/sidebar/conversation-item";
import {
  useFavoriteConversations,
  useDeleteConversation,
  useRenameConversation,
  useToggleFavoriteConversation,
} from "@/lib/hooks/use-chat";
import type { FavoriteConversationResponse } from "@/lib/types/api";

interface FavoriteConversationItemProps {
  conversation: FavoriteConversationResponse;
}

function FavoriteConversationItem({ conversation }: FavoriteConversationItemProps) {
  const router = useRouter();
  const pathname = usePathname();
  const { mutate: deleteConversation } = useDeleteConversation(conversation.project_id);
  const { mutate: renameConversation } = useRenameConversation(conversation.project_id);
  const { mutate: toggleFavorite } = useToggleFavoriteConversation(conversation.project_id);

  const handleDelete = (conversationId: string) => {
    deleteConversation(conversationId);
    if (pathname.includes(conversationId)) {
      router.push(`/projects/${conversation.project_id}/chat`);
    }
  };

  return (
    <ConversationItem
      conversation={conversation}
      projectId={conversation.project_id}
      onDelete={handleDelete}
      onRename={(id, title) => renameConversation({ conversationId: id, title })}
      onToggleFavorite={(id) => toggleFavorite(id)}
    />
  );
}

export function FavoriteConversationsSection() {
  const t = useTranslations("chat.sidebar");
  const { data: favorites } = useFavoriteConversations();

  if (!favorites || favorites.length === 0) {
    return null;
  }

  return (
    <div className="mt-2 border-t pt-2">
      <SidebarSectionHeader title={t("favorites")} />
      <div className="space-y-0.5">
        {favorites.map((conversation) => (
          <FavoriteConversationItem key={conversation.id} conversation={conversation} />
        ))}
      </div>
    </div>
  );
}
