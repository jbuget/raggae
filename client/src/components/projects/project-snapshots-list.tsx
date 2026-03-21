"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Skeleton } from "@/components/ui/skeleton";
import {
  useProjectSnapshots,
  useRestoreProjectSnapshot,
} from "@/lib/hooks/use-project-snapshots";
import type { ProjectSnapshotResponse } from "@/lib/types/api";
import { formatDateTime } from "@/lib/utils/format";

const DEFAULT_LIMIT = 20;

interface ProjectSnapshotsListProps {
  projectId: string;
}

interface SnapshotCardProps {
  snapshot: ProjectSnapshotResponse;
  isCurrentVersion: boolean;
  onRestoreRequest: (snapshot: ProjectSnapshotResponse) => void;
}

function SnapshotCard({
  snapshot,
  isCurrentVersion,
  onRestoreRequest,
}: SnapshotCardProps) {
  const t = useTranslations("projects.snapshots");

  return (
    <Card className="transition-colors hover:bg-muted/30 dark:hover:bg-muted/20">
      <CardHeader className="pb-2">
        <div className="flex flex-wrap items-start justify-between gap-2">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="outline" className="font-mono text-xs">
              v{snapshot.version_number}
            </Badge>
            {isCurrentVersion && (
              <Badge variant="secondary" className="text-xs">
                {t("currentVersion")}
              </Badge>
            )}
            {snapshot.restored_from_version !== null && (
              <Badge variant="outline" className="text-xs text-muted-foreground">
                {t("restoredFrom", { version: snapshot.restored_from_version })}
              </Badge>
            )}
          </div>
          <Button
            size="sm"
            variant="outline"
            disabled={isCurrentVersion}
            onClick={() => onRestoreRequest(snapshot)}
          >
            {t("restore")}
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-2">
        <div className="text-sm text-muted-foreground">
          {formatDateTime(snapshot.created_at)}
        </div>
        {snapshot.label && (
          <p className="text-sm italic text-muted-foreground">{snapshot.label}</p>
        )}
        <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
          {snapshot.embedding_model && (
            <span>
              <span className="font-medium">{t("embeddingModel")}:</span>{" "}
              {snapshot.embedding_model}
            </span>
          )}
          {snapshot.llm_model && (
            <span>
              <span className="font-medium">{t("llmModel")}:</span>{" "}
              {snapshot.llm_model}
            </span>
          )}
          <span>
            <span className="font-medium">{t("retrievalStrategy")}:</span>{" "}
            {snapshot.retrieval_strategy}
          </span>
        </div>
      </CardContent>
    </Card>
  );
}

function SnapshotsSkeleton() {
  return (
    <div className="space-y-4">
      {[1, 2, 3].map((i) => (
        <Card key={i}>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <div className="flex gap-2">
                <Skeleton className="h-5 w-10" />
                <Skeleton className="h-5 w-24" />
              </div>
              <Skeleton className="h-8 w-20" />
            </div>
          </CardHeader>
          <CardContent className="space-y-2">
            <Skeleton className="h-4 w-40" />
            <Skeleton className="h-4 w-64" />
          </CardContent>
        </Card>
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
      <div className="space-y-4">
        {snapshots.map((snapshot) => (
          <SnapshotCard
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
