"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Skeleton } from "@/components/ui/skeleton";
import { SnapshotAccordionItem } from "@/components/atoms/project/snapshot-accordion-item";
import {
  useProjectSnapshots,
  useRestoreProjectSnapshot,
} from "@/lib/hooks/use-project-snapshots";
import type { ProjectSnapshotResponse } from "@/lib/types/api";

const DEFAULT_LIMIT = 20;

interface ProjectSnapshotsListProps {
  projectId: string;
}

function SnapshotsSkeleton() {
  return (
    <div className="divide-y">
      {[1, 2, 3].map((i) => (
        <div key={i} className="flex items-center gap-3 px-4 py-3">
          <div className="flex flex-col items-center gap-1 shrink-0 w-10">
            <Skeleton className="h-4 w-8" />
          </div>
          <div className="flex-1 space-y-1.5">
            <Skeleton className="h-3.5 w-36" />
            <Skeleton className="h-4 w-48" />
          </div>
          <Skeleton className="h-8 w-20 shrink-0" />
        </div>
      ))}
    </div>
  );
}

export function ProjectSnapshotsList({ projectId }: ProjectSnapshotsListProps) {
  const t = useTranslations("projects.snapshots");
  const tCommon = useTranslations("common");

  const [offset, setOffset] = useState(0);
  const [confirmSnapshot, setConfirmSnapshot] =
    useState<ProjectSnapshotResponse | null>(null);

  const { data, isLoading, isError } = useProjectSnapshots(
    projectId,
    DEFAULT_LIMIT,
    offset,
  );
  const restoreMutation = useRestoreProjectSnapshot(projectId);

  const snapshots = data?.snapshots ?? [];
  const total = data?.total ?? 0;
  const currentPage = Math.floor(offset / DEFAULT_LIMIT) + 1;
  const totalPages = Math.ceil(total / DEFAULT_LIMIT);

  const maxVersion =
    snapshots.length > 0
      ? Math.max(...snapshots.map((s) => s.version_number))
      : -1;

  function handleRestoreRequest(snapshot: ProjectSnapshotResponse) {
    setConfirmSnapshot(snapshot);
  }

  function handleConfirmRestore() {
    if (!confirmSnapshot) return;

    const version = confirmSnapshot.version_number;
    restoreMutation.mutate(version, {
      onSuccess: () => {
        toast.success(t("restoreSuccess", { version }));
        setConfirmSnapshot(null);
      },
      onError: () => {
        toast.error(t("restoreError", { version }));
        setConfirmSnapshot(null);
      },
    });
  }

  function handleCancelRestore() {
    setConfirmSnapshot(null);
  }

  if (isLoading) {
    return <SnapshotsSkeleton />;
  }

  if (isError) {
    return (
      <p className="text-sm text-destructive">{t("loadError")}</p>
    );
  }

  if (snapshots.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">{t("empty")}</p>
    );
  }

  return (
    <>
    <div>
        {snapshots.map((snapshot) => (
          <SnapshotAccordionItem
            key={snapshot.id}
            snapshot={snapshot}
            isCurrentVersion={snapshot.version_number === maxVersion}
            onRestoreRequest={handleRestoreRequest}
          />
        ))}
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-between pt-2">
          <Button
            variant="outline"
            size="sm"
            disabled={offset === 0}
            onClick={() => setOffset(Math.max(0, offset - DEFAULT_LIMIT))}
          >
            {t("previous")}
          </Button>
          <span className="text-sm text-muted-foreground">
            {t("pageInfo", { current: currentPage, total: totalPages })}
          </span>
          <Button
            variant="outline"
            size="sm"
            disabled={offset + DEFAULT_LIMIT >= total}
            onClick={() => setOffset(offset + DEFAULT_LIMIT)}
          >
            {t("next")}
          </Button>
        </div>
      )}

      <Dialog
        open={confirmSnapshot !== null}
        onOpenChange={(open) => {
          if (!open) handleCancelRestore();
        }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {confirmSnapshot
                ? t("restoreDialogTitle", {
                    version: confirmSnapshot.version_number,
                  })
                : ""}
            </DialogTitle>
            <DialogDescription>
              {confirmSnapshot
                ? t("restoreDialogDescription", {
                    version: confirmSnapshot.version_number,
                  })
                : ""}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={handleCancelRestore}
              disabled={restoreMutation.isPending}
            >
              {tCommon("cancel")}
            </Button>
            <Button
              onClick={handleConfirmRestore}
              disabled={restoreMutation.isPending}
            >
              {restoreMutation.isPending ? t("restoring") : t("restore")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
