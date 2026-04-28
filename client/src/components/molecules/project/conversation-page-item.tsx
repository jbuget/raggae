"use client";

import { useState } from "react";
import Link from "next/link";
import { MoreVertical, Pencil, Trash2 } from "lucide-react";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { RenameConversationDialog } from "@/components/atoms/conversation/rename-conversation-dialog";
import { DeleteConversationDialog } from "@/components/atoms/conversation/delete-conversation-dialog";
import { cn } from "@/lib/utils";
import { formatDateTime } from "@/lib/utils/format";
import type { ConversationResponse } from "@/lib/types/api";

interface ConversationPageItemProps {
  conversation: ConversationResponse;
  projectId: string;
  onDelete: (id: string) => void;
  onRename: (id: string, title: string) => void;
  isSelected?: boolean;
  anySelected?: boolean;
  onToggleSelect?: (id: string) => void;
}

export function ConversationPageItem({
  conversation,
  projectId,
  onDelete,
  onRename,
  isSelected = false,
  anySelected = false,
  onToggleSelect,
}: ConversationPageItemProps) {
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [renameDialogOpen, setRenameDialogOpen] = useState(false);
  const t = useTranslations("chat.sidebar");

  const title = conversation.title ?? formatDateTime(conversation.created_at);

  return (
    <>
      <div className={cn("group flex items-center gap-3 rounded-lg border px-4 py-3 transition-colors hover:bg-muted/50", isSelected && "bg-muted/50 border-primary/40")}>
        {onToggleSelect && (
          <Checkbox
            checked={isSelected}
            onCheckedChange={() => onToggleSelect(conversation.id)}
            onClick={(e) => e.stopPropagation()}
            aria-label={`Sélectionner ${title}`}
            className={cn(!anySelected && !isSelected && "opacity-0 group-hover:opacity-100 transition-opacity")}
          />
        )}
        <Link
          href={`/projects/${projectId}/chat/${conversation.id}`}
          className="flex flex-1 items-center gap-4 min-w-0 -my-3 py-3"
        >
          <span className="flex-1 truncate font-medium">{title}</span>
          <span className="shrink-0 text-xs text-muted-foreground">
            {formatDateTime(conversation.created_at)}
          </span>
        </Link>

        <DropdownMenu modal={false}>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7 shrink-0 opacity-0 transition-opacity group-hover:opacity-100 data-[state=open]:opacity-100 focus:opacity-100"
              aria-label={t("menuLabel")}
              onClick={(e) => e.preventDefault()}
            >
              <MoreVertical className="size-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem className="cursor-pointer gap-2" onSelect={() => setRenameDialogOpen(true)}>
              <Pencil className="h-4 w-4" />
              {t("renameTitle")}
            </DropdownMenuItem>
            <DropdownMenuItem
              className="cursor-pointer gap-2 text-destructive focus:text-destructive"
              onSelect={() => setDeleteDialogOpen(true)}
            >
              <Trash2 className="h-4 w-4" />
              {t("deleteTitle")}
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      <RenameConversationDialog
        open={renameDialogOpen}
        onOpenChange={setRenameDialogOpen}
        initialTitle={conversation.title ?? ""}
        onConfirm={(title) => onRename(conversation.id, title)}
      />

      <DeleteConversationDialog
        open={deleteDialogOpen}
        onOpenChange={setDeleteDialogOpen}
        onConfirm={() => onDelete(conversation.id)}
      />
    </>
  );
}
