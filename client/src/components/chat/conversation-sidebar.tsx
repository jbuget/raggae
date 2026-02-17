"use client";

import Link from "next/link";
import { useParams, usePathname, useRouter } from "next/navigation";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import { formatDate } from "@/lib/utils/format";
import {
  useConversations,
  useDeleteConversation,
} from "@/lib/hooks/use-chat";
import type { ConversationResponse } from "@/lib/types/api";

export function ConversationSidebar() {
  const router = useRouter();
  const params = useParams<{ projectId: string; conversationId?: string }>();
  const pathname = usePathname();
  const { data: conversations, isLoading } = useConversations(params.projectId);
  const deleteConversation = useDeleteConversation(params.projectId);

  const sorted = conversations
    ? [...conversations].sort(
        (a, b) =>
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
      )
    : [];

  return (
    <div className="flex h-full min-h-0 w-64 flex-col border-r">
      <div className="border-b p-3">
        <Button asChild className="w-full" size="sm">
          <Link href={`/projects/${params.projectId}/chat`}>
            New Conversation
          </Link>
        </Button>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto">
        {isLoading ? (
          <div className="space-y-2 p-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="h-12" />
            ))}
          </div>
        ) : sorted.length === 0 ? (
          <p className="p-3 text-sm text-muted-foreground">
            No conversations yet
          </p>
        ) : (
          <div className="space-y-1 p-2">
            {sorted.map((conv) => (
              <ConversationItem
                key={conv.id}
                conversation={conv}
                projectId={params.projectId}
                isActive={pathname.includes(conv.id)}
                onDelete={(id) =>
                  deleteConversation.mutate(id, {
                    onSuccess: () => {
                      if (pathname.includes(id)) {
                        router.push(`/projects/${params.projectId}/chat`);
                      }
                    },
                  })
                }
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function ConversationItem({
  conversation,
  projectId,
  isActive,
  onDelete,
}: {
  conversation: ConversationResponse;
  projectId: string;
  isActive: boolean;
  onDelete: (id: string) => void;
}) {
  const [deleteOpen, setDeleteOpen] = useState(false);
  const conversationLabel = conversation.title || formatDate(conversation.created_at);

  return (
    <div className="group relative">
      <Link
        href={`/projects/${projectId}/chat/${conversation.id}`}
        className={cn(
          "block w-full min-w-0 truncate rounded-md px-2 py-2 pr-10 text-left text-sm",
          isActive ? "bg-muted" : "hover:bg-muted/50",
        )}
        title={conversationLabel}
      >
        {conversationLabel}
      </Link>

      <div className="absolute right-1 top-1/2 -translate-y-1/2 rounded bg-background/95 p-0.5 opacity-0 backdrop-blur-sm transition-opacity group-hover:opacity-100">
        <Dialog open={deleteOpen} onOpenChange={setDeleteOpen}>
          <DialogTrigger asChild>
            <Button
              variant="ghost"
              size="sm"
              className="h-6 w-6 cursor-pointer p-0 opacity-0 group-hover:opacity-100"
            >
              x
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Delete Conversation</DialogTitle>
              <DialogDescription>
                Are you sure you want to delete this conversation?
              </DialogDescription>
            </DialogHeader>
            <DialogFooter>
              <Button variant="outline" onClick={() => setDeleteOpen(false)}>
                Cancel
              </Button>
              <Button
                variant="destructive"
                onClick={() => {
                  onDelete(conversation.id);
                  setDeleteOpen(false);
                }}
              >
                Delete
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
}
