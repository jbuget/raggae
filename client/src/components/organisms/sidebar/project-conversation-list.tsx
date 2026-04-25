"use client";

import { useRouter, usePathname } from "next/navigation";
import { useTranslations } from "next-intl";
import { ConversationItem } from "@/components/molecules/sidebar/conversation-item";
import { useConversations, useDeleteConversation } from "@/lib/hooks/use-chat";

interface ProjectConversationListProps {
  projectId: string;
}

export function ProjectConversationList({ projectId }: ProjectConversationListProps) {
  const t = useTranslations("chat.sidebar");
  const router = useRouter();
  const pathname = usePathname();
  const { data: conversations, isLoading } = useConversations(projectId);
  const { mutate: deleteConversation } = useDeleteConversation(projectId);

  const sorted = [...(conversations ?? [])].sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
  );
  const recent = sorted.slice(0, 10);

  const handleDelete = (conversationId: string) => {
    deleteConversation(conversationId);
    if (pathname.includes(conversationId)) {
      router.push(`/projects/${projectId}/chat`);
    }
  };

  if (isLoading || recent.length === 0) {
    return (
      <p className="px-3 py-1 text-xs text-muted-foreground">{t("noConversations")}</p>
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
        />
      ))}
    </div>
  );
}
