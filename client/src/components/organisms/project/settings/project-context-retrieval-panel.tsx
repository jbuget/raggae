"use client";

import { useState } from "react";
import { toast } from "sonner";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useProject, useUpdateProject } from "@/lib/hooks/use-projects";
import type { RetrievalStrategy } from "@/lib/types/api";

export function ProjectContextRetrievalPanel({ projectId }: { projectId: string }) {
  const t = useTranslations("projects.settings");
  const tCommon = useTranslations("common");

  const { data: project } = useProject(projectId);
  const updateProject = useUpdateProject(projectId);

  const [retrievalStrategy, setRetrievalStrategy] = useState<RetrievalStrategy | null>(null);
  const [retrievalTopK, setRetrievalTopK] = useState<number | null>(null);
  const [retrievalMinScore, setRetrievalMinScore] = useState<number | null>(null);

  if (!project) return null;

  const effectiveRetrievalStrategy =
    retrievalStrategy ?? (project.retrieval_strategy ?? "hybrid");
  const effectiveRetrievalTopK = retrievalTopK ?? project.retrieval_top_k ?? 8;
  const effectiveRetrievalMinScore = retrievalMinScore ?? project.retrieval_min_score ?? 0.3;

  const hasChanges =
    effectiveRetrievalStrategy !== (project.retrieval_strategy ?? "hybrid") ||
    effectiveRetrievalTopK !== (project.retrieval_top_k ?? 8) ||
    effectiveRetrievalMinScore !== (project.retrieval_min_score ?? 0.3);

  function handleSave() {
    updateProject.mutate(
      {
        retrieval_strategy: effectiveRetrievalStrategy,
        retrieval_top_k: effectiveRetrievalTopK,
        retrieval_min_score: effectiveRetrievalMinScore,
      },
      {
        onSuccess: () => toast.success(t("updateSuccess")),
        onError: () => toast.error(t("updateError")),
      },
    );
  }

  return (
    <div className="max-w-3xl space-y-4 rounded-md">
      <p className="text-base font-semibold tracking-tight">{t("contextRetrieval.title")}</p>
      <p className="text-sm text-muted-foreground">{t("contextRetrieval.description")}</p>

      <div className="space-y-2">
        <Label htmlFor="retrievalStrategy">{t("contextRetrieval.searchTypeLabel")}</Label>
        <select
          id="retrievalStrategy"
          value={effectiveRetrievalStrategy}
          onChange={(e) => setRetrievalStrategy(e.target.value as RetrievalStrategy)}
          className="border-input bg-background w-full rounded-md border px-3 py-2 text-sm"
        >
          <option value="hybrid">{t("contextRetrieval.hybrid")}</option>
          <option value="vector">{t("contextRetrieval.vector")}</option>
          <option value="fulltext">{t("contextRetrieval.fulltext")}</option>
        </select>
      </div>

      <div className="space-y-2">
        <Label htmlFor="retrievalTopK">{t("contextRetrieval.topKLabel")}</Label>
        <Input
          id="retrievalTopK"
          type="number"
          min={1}
          max={40}
          value={effectiveRetrievalTopK}
          onChange={(e) => {
            const parsed = Number.parseInt(e.target.value, 10);
            if (Number.isNaN(parsed)) return;
            setRetrievalTopK(Math.max(1, Math.min(40, parsed)));
          }}
        />
        <p className="text-xs text-muted-foreground">{t("contextRetrieval.topKNote")}</p>
      </div>

      <div className="space-y-2">
        <Label htmlFor="retrievalMinScore">{t("contextRetrieval.minScoreLabel")}</Label>
        <Input
          id="retrievalMinScore"
          type="number"
          min={0}
          max={1}
          step={0.05}
          value={effectiveRetrievalMinScore}
          onChange={(e) => {
            const parsed = Number.parseFloat(e.target.value);
            if (Number.isNaN(parsed)) return;
            const bounded = Math.max(0, Math.min(1, parsed));
            setRetrievalMinScore(Math.round(bounded * 100) / 100);
          }}
        />
        <p className="text-xs text-muted-foreground">{t("contextRetrieval.minScoreNote")}</p>
      </div>

      <Button
        className="cursor-pointer"
        disabled={!hasChanges || updateProject.isPending}
        onClick={handleSave}
      >
        {updateProject.isPending ? tCommon("saving") : t("saveChanges")}
      </Button>
    </div>
  );
}
