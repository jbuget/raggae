"use client";

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
import type { DocumentResponse } from "@/lib/types/api";
import { formatDate, formatFileSize } from "@/lib/utils/format";

interface DocumentRowProps {
  document: DocumentResponse;
  onDelete: (id: string) => void;
  isDeleting: boolean;
  onReindex: (id: string) => void;
  reindexingId: string | null;
}

export function DocumentRow({ document, onDelete, isDeleting, onReindex, reindexingId }: DocumentRowProps) {
  const isReindexing = reindexingId === document.id;
  const [deleteOpen, setDeleteOpen] = useState(false);

  return (
    <div className="flex items-center justify-between rounded-md border p-4">
      <div className="space-y-1">
        <p className="text-sm font-medium">{document.file_name}</p>
        <div className="flex gap-3 text-xs text-muted-foreground">
          <span>{document.content_type}</span>
          <span>{formatFileSize(document.file_size)}</span>
          <span>{formatDate(document.created_at)}</span>
        </div>
      </div>

      <div className="flex gap-2">
        <Button
          variant="ghost"
          size="sm"
          disabled={isReindexing}
          onClick={() => onReindex(document.id)}
        >
          {isReindexing ? "Reindexing..." : "Reindex"}
        </Button>

      <Dialog open={deleteOpen} onOpenChange={setDeleteOpen}>
        <DialogTrigger asChild>
          <Button variant="ghost" size="sm" className="text-destructive">
            Delete
          </Button>
        </DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Document</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete &quot;{document.file_name}&quot;?
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteOpen(false)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              disabled={isDeleting}
              onClick={() => {
                onDelete(document.id);
                setDeleteOpen(false);
              }}
            >
              {isDeleting ? "Deleting..." : "Delete"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      </div>
    </div>
  );
}
