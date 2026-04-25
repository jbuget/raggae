"use client";

import { useState } from "react";
import { MoreVertical, Pencil, Trash2 } from "lucide-react";
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
import { Input } from "@/components/ui/input";
import { ConversationLink, useConversationActive } from "@/components/atoms/sidebar/conversation-link";
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
  const [renameValue, setRenameValue] = useState("");
  const isActive = useConversationActive(conversation.id);
  const t = useTranslations("chat.sidebar");
  const tCommon = useTranslations("common");

  function handleRenameOpen() {
    setRenameValue(conversation.title ?? "");
    setRenameDialogOpen(true);
  }

  function handleRenameConfirm() {
    const trimmed = renameValue.trim();
    if (trimmed) {
      onRename(conversation.id, trimmed);
    }
    setRenameDialogOpen(false);
  }

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
              onSelect={handleRenameOpen}
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

      <Dialog open={renameDialogOpen} onOpenChange={setRenameDialogOpen}>
        <DialogContent showCloseButton={false}>
          <DialogHeader>
            <DialogTitle>{t("renameTitle")}</DialogTitle>
            <DialogDescription>{t("renameDescription")}</DialogDescription>
          </DialogHeader>
          <Input
            value={renameValue}
            onChange={(e) => setRenameValue(e.target.value)}
            placeholder={t("renamePlaceholder")}
            onKeyDown={(e) => {
              if (e.key === "Enter") handleRenameConfirm();
            }}
            autoFocus
          />
          <DialogFooter>
            <Button variant="outline" onClick={() => setRenameDialogOpen(false)}>
              {tCommon("cancel")}
            </Button>
            <Button onClick={handleRenameConfirm} disabled={!renameValue.trim()}>
              {tCommon("save")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent showCloseButton={false}>
          <DialogHeader>
            <DialogTitle>{t("deleteTitle")}</DialogTitle>
            <DialogDescription>{t("deleteConfirm")}</DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteDialogOpen(false)}>
              {tCommon("cancel")}
            </Button>
            <Button
              variant="destructive"
              onClick={() => {
                onDelete(conversation.id);
                setDeleteDialogOpen(false);
              }}
            >
              {tCommon("delete")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
