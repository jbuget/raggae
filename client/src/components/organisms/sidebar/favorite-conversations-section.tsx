"use client";

import Link from "next/link";
import { Star } from "lucide-react";
import { useTranslations } from "next-intl";
import { SidebarSectionHeader } from "@/components/atoms/sidebar/sidebar-section-header";
import { useFavoriteConversations } from "@/lib/hooks/use-chat";

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
          <Link
            key={conversation.id}
            href={`/projects/${conversation.project_id}/chat/${conversation.id}`}
            className="flex items-center gap-2 rounded-md px-3 py-1.5 text-sm hover:bg-muted transition-colors"
          >
            <Star className="h-3 w-3 shrink-0 fill-yellow-400 text-yellow-400" />
            <div className="min-w-0 flex-1">
              <p className="truncate">{conversation.title ?? t("newConversation")}</p>
              <p className="truncate text-xs text-muted-foreground">{conversation.project_name}</p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
