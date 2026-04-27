"use client";

import { useState } from "react";
import Link from "next/link";
import { Trash2 } from "lucide-react";
import { useRouter, usePathname } from "next/navigation";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { ConversationPageItem } from "@/components/molecules/project/conversation-page-item";
import { useConversations, useDeleteConversation, useRenameConversation } from "@/lib/hooks/use-chat";

interface ConversationListProps {
  projectId: string;
}

export function ConversationList({ projectId }: ConversationListProps) {
  const t = useTranslations("conversations");
  const tCommon = useTranslations("common");
  const router = useRouter();
  const pathname = usePathname();
  const { data: conversations, isLoading } = useConversations(projectId, 100);
  const { mutate: deleteConversation } = useDeleteConversation(projectId);
  const { mutate: renameConversation } = useRenameConversation(projectId);

  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [bulkDeleteOpen, setBulkDeleteOpen] = useState(false);

  const list = conversations ?? [];

  const handleDelete = (conversationId: string) => {
    deleteConversation(conversationId);
    setSelected((prev) => { const next = new Set(prev); next.delete(conversationId); return next; });
    if (pathname.includes(conversationId)) {
      router.push(`/projects/${projectId}/chat`);
    }
  };

  const handleToggleSelect = (id: string) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const allSelected = list.length > 0 && selected.size === list.length;
  const someSelected = selected.size > 0 && !allSelected;

  const handleToggleAll = () => {
    if (allSelected || someSelected) {
      setSelected(new Set());
    } else {
      setSelected(new Set(list.map((c) => c.id)));
    }
  };

  const handleBulkDelete = () => {
    const ids = Array.from(selected);
    const currentInPath = ids.find((id) => pathname.includes(id));
    for (const id of ids) {
      deleteConversation(id);
    }
    setSelected(new Set());
    setBulkDeleteOpen(false);
    if (currentInPath) {
      router.push(`/projects/${projectId}/chat`);
    }
  };

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
        <>
          <div className="mb-3 flex items-center gap-3 border-b pb-3 px-4">
            <Checkbox
              checked={allSelected ? true : someSelected ? "indeterminate" : false}
              onCheckedChange={handleToggleAll}
              aria-label={t("selectAll")}
            />
            <span className="text-sm text-muted-foreground">
              {selected.size > 0 ? t("selectedCount", { count: selected.size }) : t("selectAll")}
            </span>
            {selected.size > 0 && (
              <Button
                variant="destructive"
                size="sm"
                className="ml-auto gap-1.5"
                onClick={() => setBulkDeleteOpen(true)}
              >
                <Trash2 className="h-3.5 w-3.5" />
                {t("deleteSelected", { count: selected.size })}
              </Button>
            )}
          </div>

          <div className="flex flex-col gap-2">
            {list.map((conversation) => (
              <ConversationPageItem
                key={conversation.id}
                conversation={conversation}
                projectId={projectId}
                onDelete={handleDelete}
                onRename={(id, title) => renameConversation({ conversationId: id, title })}
                isSelected={selected.has(conversation.id)}
                anySelected={selected.size > 0}
                onToggleSelect={handleToggleSelect}
              />
            ))}
          </div>
        </>
      )}

      <Dialog open={bulkDeleteOpen} onOpenChange={setBulkDeleteOpen}>
        <DialogContent showCloseButton={false}>
          <DialogHeader>
            <DialogTitle>{t("bulkDeleteTitle", { count: selected.size })}</DialogTitle>
            <DialogDescription>{t("bulkDeleteConfirm", { count: selected.size })}</DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setBulkDeleteOpen(false)}>
              {tCommon("cancel")}
            </Button>
            <Button variant="destructive" onClick={handleBulkDelete}>
              {tCommon("delete")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
