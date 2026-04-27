"use client";

import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { ConversationPageItem } from "@/components/molecules/project/conversation-page-item";
import { useConversations, useDeleteConversation, useRenameConversation } from "@/lib/hooks/use-chat";

interface ConversationListProps {
  projectId: string;
}

export function ConversationList({ projectId }: ConversationListProps) {
  const t = useTranslations("conversations");
  const router = useRouter();
  const pathname = usePathname();
  const { data: conversations, isLoading } = useConversations(projectId, 100);
  const { mutate: deleteConversation } = useDeleteConversation(projectId);
  const { mutate: renameConversation } = useRenameConversation(projectId);

  const handleDelete = (conversationId: string) => {
    deleteConversation(conversationId);
    if (pathname.includes(conversationId)) {
      router.push(`/projects/${projectId}/chat`);
    }
  };

  const list = conversations ?? [];

  return (
    <div className="mx-auto w-full max-w-190 px-4">
      {isLoading ? (
        <div className="space-y-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-10" />
          ))}
        </div>
      ) : list.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-muted-foreground mb-4">{t("empty")}</p>
          <Button asChild>
            <Link href={`/projects/${projectId}/chat`}>{t("startNew")}</Link>
          </Button>
        </div>
      ) : (
        <div className="flex flex-col gap-2">
          {list.map((conversation) => (
            <ConversationPageItem
              key={conversation.id}
              conversation={conversation}
              projectId={projectId}
              onDelete={handleDelete}
              onRename={(id, title) => renameConversation({ conversationId: id, title })}
            />
          ))}
        </div>
      )}
    </div>
  );
}
