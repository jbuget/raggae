"use client";

import { Star } from "lucide-react";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { useConversation, useToggleFavoriteConversation } from "@/lib/hooks/use-chat";
import { cn } from "@/lib/utils";

interface FavoriteConversationButtonProps {
  projectId: string;
  conversationId: string;
}

export function FavoriteConversationButton({
  projectId,
  conversationId,
}: FavoriteConversationButtonProps) {
  const t = useTranslations("chat.sidebar");
  const { data: conversation } = useConversation(projectId, conversationId);
  const { mutate: toggleFavorite } = useToggleFavoriteConversation(projectId);

  return (
    <Button
      variant="ghost"
      size="icon"
      className="h-8 w-8"
      aria-label={conversation?.is_favorite ? t("removeFromFavorites") : t("addToFavorites")}
      title={conversation?.is_favorite ? t("removeFromFavorites") : t("addToFavorites")}
      onClick={() => toggleFavorite(conversationId)}
    >
      <Star
        className={cn("h-4 w-4", conversation?.is_favorite && "fill-current")}
      />
    </Button>
  );
}
