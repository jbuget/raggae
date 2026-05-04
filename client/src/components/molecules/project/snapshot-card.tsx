"use client";

import { useTranslations } from "next-intl";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import type { ProjectSnapshotResponse } from "@/lib/types/api";
import { formatDateTime } from "@/lib/utils/format";

interface SnapshotCardProps {
  snapshot: ProjectSnapshotResponse;
  isCurrentVersion: boolean;
  onRestoreRequest: (snapshot: ProjectSnapshotResponse) => void;
}

export function SnapshotCard({
  snapshot,
  isCurrentVersion,
  onRestoreRequest,
}: SnapshotCardProps) {
  const t = useTranslations("projects.snapshots");

  return (
    <Card className="gap-2 transition-colors hover:bg-muted/30 dark:hover:bg-muted/20">
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
