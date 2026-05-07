"use client";

import { useState } from "react";
import { ChevronDown } from "lucide-react";
import { useTranslations } from "next-intl";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { ProjectSnapshotResponse } from "@/lib/types/api";
import { formatDateTime } from "@/lib/utils/format";

const CHUNKING_KEY: Record<string, "chunkingAuto" | "chunkingFixed" | "chunkingParagraph" | "chunkingHeading" | "chunkingSemantic" | "chunkingTabular"> = {
  auto: "chunkingAuto",
  fixed_window: "chunkingFixed",
  paragraph: "chunkingParagraph",
  heading_section: "chunkingHeading",
  semantic: "chunkingSemantic",
  tabular: "chunkingTabular",
};

interface SnapshotAccordionItemProps {
  snapshot: ProjectSnapshotResponse;
  isCurrentVersion: boolean;
  onRestoreRequest: (snapshot: ProjectSnapshotResponse) => void;
}

export function SnapshotAccordionItem({ snapshot, isCurrentVersion, onRestoreRequest }: SnapshotAccordionItemProps) {
  const t = useTranslations("projects.snapshots");
  const [expanded, setExpanded] = useState(false);

  const configTags = [
    snapshot.embedding_model,
    snapshot.llm_model,
    snapshot.chunking_strategy ? (CHUNKING_KEY[snapshot.chunking_strategy] ? t(CHUNKING_KEY[snapshot.chunking_strategy]) : snapshot.chunking_strategy) : null,
    snapshot.retrieval_strategy,
  ].filter(Boolean);

  return (
    <div className="border-b last:border-b-0">
      <div className="flex w-full items-center gap-3 px-4 py-3">
        <div className="flex flex-col items-center gap-1 shrink-0 w-10">
          <span className={`font-mono text-xs font-semibold ${isCurrentVersion ? "text-foreground" : "text-muted-foreground"}`}>
            v{snapshot.version_number}
          </span>
          {snapshot.restored_from_version !== null && (
            <Badge variant="outline" className="px-1 py-0 text-xs leading-3 text-muted-foreground whitespace-nowrap">
              ↩ v{snapshot.restored_from_version}
            </Badge>
          )}
        </div>

        <button
          type="button"
          aria-expanded={expanded}
          className="flex flex-1 items-start gap-3 text-left"
          onClick={() => setExpanded((prev) => !prev)}
        >
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              {isCurrentVersion && (
                <Badge variant="secondary" className="px-1.5 py-0.5 text-xs leading-none whitespace-nowrap bg-secondary text-secondary-foreground font-medium">
                  {t("currentVersion")}
                </Badge>
              )}
              {formatDateTime(snapshot.created_at)}
            </div>
            {snapshot.label && (
              <div className="text-xs italic text-muted-foreground">{snapshot.label}</div>
            )}
            {configTags.length > 0 && (
              <div className="mt-1 flex flex-wrap gap-1">
                {configTags.map((tag) => (
                  <Badge key={tag} variant="outline" className="px-1.5 py-0 text-xs font-normal">
                    {tag}
                  </Badge>
                ))}
              </div>
            )}
          </div>
          <ChevronDown
            className={`mt-0.5 shrink-0 size-4 text-muted-foreground transition-transform duration-200 ${expanded ? "rotate-180" : ""}`}
          />
        </button>

        <Button
          size="sm"
          variant="outline"
          className="shrink-0"
          disabled={isCurrentVersion}
          onClick={() => onRestoreRequest(snapshot)}
        >
          {t("restore")}
        </Button>
      </div>

      {expanded && (
        <div className="px-4 pb-3 pt-1 grid grid-cols-2 gap-x-6 gap-y-1 text-xs text-muted-foreground bg-muted/30 sm:grid-cols-3">
          {snapshot.embedding_model && (
            <span className="py-1"><span className="font-medium">{t("embeddingModel")}:</span> {snapshot.embedding_model}</span>
          )}
          {snapshot.llm_model && (
            <span className="py-1"><span className="font-medium">{t("llmModel")}:</span> {snapshot.llm_model}</span>
          )}
          {snapshot.chunking_strategy && CHUNKING_KEY[snapshot.chunking_strategy] && (
            <span className="py-1"><span className="font-medium">{t("chunking")}:</span> {t(CHUNKING_KEY[snapshot.chunking_strategy])}</span>
          )}
          {snapshot.parent_child_chunking && (
            <span className="py-1 font-medium">{t("parentChild")}</span>
          )}
          {snapshot.retrieval_strategy && (
            <span className="py-1"><span className="font-medium">{t("retrievalStrategy")}:</span> {snapshot.retrieval_strategy}</span>
          )}
          {snapshot.retrieval_top_k != null && (
            <span className="py-1"><span className="font-medium">Top-K:</span> {snapshot.retrieval_top_k}</span>
          )}
          {snapshot.reranking_enabled && (
            <span className="py-1"><span className="font-medium">{snapshot.reranker_backend}</span></span>
          )}
          {snapshot.chat_history_window_size != null && (
            <span className="py-1"><span className="font-medium">Historique:</span> {snapshot.chat_history_window_size}</span>
          )}
        </div>
      )}
    </div>
  );
}
