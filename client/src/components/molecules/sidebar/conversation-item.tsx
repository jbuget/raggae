"use client";

import { useState } from "react";
import { MoreVertical, Pencil, Trash2 } from "lucide-react";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ConversationLink, useConversationActive } from "@/components/atoms/sidebar/conversation-link";
import { RenameConversationDialog } from "@/components/atoms/conversation/rename-conversation-dialog";
import { DeleteConversationDialog } from "@/components/atoms/conversation/delete-conversation-dialog";
import { cn } from "@/lib/utils";
import type { ConversationResponse } from "@/lib/types/api";

interface ConversationItemProps {
  conversation: ConversationResponse;
  projectId: string;
  onDelete: (id: string) => void;
  onRename: (id: string, title: string) => void;
}

export function ConversationItem({ conversation, projectId, onDelete, onRename }: ConversationItemProps) {
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [renameDialogOpen, setRenameDialogOpen] = useState(false);
  const isActive = useConversationActive(conversation.id);
  const t = useTranslations("chat.sidebar");

  return (
    <>
      <div
        className={cn(
          "group flex items-center rounded-md transition-colors",
          isActive ? "bg-primary/10" : "hover:bg-muted",
        )}
      >
        <ConversationLink conversation={conversation} projectId={projectId} isActive={isActive} />
        <DropdownMenu modal={false}>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="mr-1 h-5 w-5 shrink-0 opacity-0 transition-opacity group-hover:opacity-100 data-[state=open]:opacity-100 focus:opacity-100"
              aria-label={t("menuLabel")}
            >
              <MoreVertical className="h-3 w-3" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem
              className="cursor-pointer gap-2"
              onSelect={() => setRenameDialogOpen(true)}
            >
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
