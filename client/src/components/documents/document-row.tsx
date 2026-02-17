"use client";

import { useState } from "react";
import { Badge } from "@/components/ui/badge";
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
  const statusLabel = document.status.charAt(0).toUpperCase() + document.status.slice(1);
  const statusClassName =
    document.status === "indexed"
      ? "border-emerald-200 bg-emerald-100 text-emerald-800"
      : document.status === "processing"
        ? "border-sky-200 bg-sky-100 text-sky-800"
        : document.status === "uploaded"
          ? "border-amber-200 bg-amber-100 text-amber-800"
          : "border-red-200 bg-red-100 text-red-800";

  return (
    <div className="flex items-center justify-between rounded-md border p-4">
      <div className="space-y-1">
        <div className="flex items-center gap-2">
          <p className="text-sm font-medium">{document.file_name}</p>
          <Badge variant="outline" className={statusClassName}>
            {statusLabel}
          </Badge>
        </div>
        <div className="flex gap-3 text-xs text-muted-foreground">
          <span
            className="font-mono cursor-pointer hover:text-foreground"
            onClick={() => navigator.clipboard.writeText(document.id)}
            title="Copy ID"
          >
            {document.id}
          </span>
          <span>{document.content_type}</span>
          <span>{formatFileSize(document.file_size)}</span>
          <span>{formatDate(document.created_at)}</span>
          {document.status === "error" && document.error_message && (
            <span className="text-destructive">{document.error_message}</span>
          )}
        </div>
      </div>

      <div className="flex gap-2">
        <Button
          variant="ghost"
          size="sm"
          className="cursor-pointer"
          disabled={isReindexing}
          onClick={() => onReindex(document.id)}
        >
          {isReindexing ? "Reindexing..." : "Reindex"}
        </Button>

      <Dialog open={deleteOpen} onOpenChange={setDeleteOpen}>
        <DialogTrigger asChild>
          <Button variant="ghost" size="sm" className="cursor-pointer text-destructive">
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
            <Button variant="outline" className="cursor-pointer" onClick={() => setDeleteOpen(false)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              className="cursor-pointer"
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
