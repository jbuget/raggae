"use client";

import { useState } from "react";
import { MoreVertical } from "lucide-react";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ConversationLink } from "@/components/atoms/sidebar/conversation-link";
import type { ConversationResponse } from "@/lib/types/api";

interface ConversationItemProps {
  conversation: ConversationResponse;
  projectId: string;
  onDelete: (id: string) => void;
}

export function ConversationItem({ conversation, projectId, onDelete }: ConversationItemProps) {
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const t = useTranslations("chat.sidebar");

  return (
    <>
      <div className="group flex items-center gap-1">
        <div className="min-w-0 flex-1">
          <ConversationLink conversation={conversation} projectId={projectId} />
        </div>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="h-6 w-6 opacity-0 transition-opacity group-hover:opacity-100 data-[state=open]:opacity-100 focus:opacity-100"
              aria-label={t("deleteTitle")}
            >
              <MoreVertical className="h-3 w-3" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem
              className="cursor-pointer text-destructive focus:text-destructive"
              onSelect={() => setDeleteDialogOpen(true)}
            >
              {t("deleteTitle")}
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent showCloseButton={false}>
          <DialogHeader>
            <DialogTitle>{t("deleteTitle")}</DialogTitle>
            <DialogDescription>{t("deleteConfirm")}</DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteDialogOpen(false)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={() => {
                onDelete(conversation.id);
                setDeleteDialogOpen(false);
              }}
            >
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
