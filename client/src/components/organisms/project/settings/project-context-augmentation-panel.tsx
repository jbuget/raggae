"use client";

import { useState } from "react";
import { toast } from "sonner";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Input } from "@/components/ui/input";
import { useProject, useUpdateProject } from "@/lib/hooks/use-projects";
import { useModelCatalog } from "@/lib/hooks/use-model-catalog";
import type { ProjectRerankerBackend } from "@/lib/types/api";

export function ProjectContextAugmentationPanel({ projectId }: { projectId: string }) {
  const t = useTranslations("projects.settings");
  const tCommon = useTranslations("common");

  const { data: project } = useProject(projectId);
  const updateProject = useUpdateProject(projectId);
  const { data: modelCatalog } = useModelCatalog();

  const [rerankingEnabled, setRerankingEnabled] = useState<boolean | null>(null);
  const [rerankerBackend, setRerankerBackend] = useState<ProjectRerankerBackend | null>(null);
  const [rerankerModel, setRerankerModel] = useState<string | null>(null);
  const [rerankerCandidateMultiplier, setRerankerCandidateMultiplier] = useState<number | null>(
    null,
  );

  if (!project) return null;

  const effectiveRerankingEnabled = rerankingEnabled ?? project.reranking_enabled ?? false;
  const effectiveRerankerBackend = rerankerBackend ?? project.reranker_backend ?? "none";
  const effectiveRerankerModel = rerankerModel ?? project.reranker_model ?? "";
  const effectiveRerankerCandidateMultiplier =
    rerankerCandidateMultiplier ?? project.reranker_candidate_multiplier ?? 3;

  const hasChanges =
    effectiveRerankingEnabled !== (project.reranking_enabled ?? false) ||
    effectiveRerankerBackend !== (project.reranker_backend ?? "none") ||
    effectiveRerankerModel !== (project.reranker_model ?? "") ||
    effectiveRerankerCandidateMultiplier !== (project.reranker_candidate_multiplier ?? 3);

  const rerankerModelOptions =
    modelCatalog?.reranker[effectiveRerankerBackend as ProjectRerankerBackend] ?? [];

  function handleSave() {
    updateProject.mutate(
      {
        reranking_enabled: effectiveRerankingEnabled,
        reranker_backend: effectiveRerankerBackend,
        reranker_model: effectiveRerankerModel || null,
        reranker_candidate_multiplier: effectiveRerankerCandidateMultiplier,
      },
      {
        onSuccess: () => toast.success(t("updateSuccess")),
        onError: () => toast.error(t("updateError")),
      },
    );
  }

  return (
    <div className="max-w-3xl space-y-4 rounded-md">
      <p className="text-base font-semibold tracking-tight">{t("contextAugmentation.title")}</p>

      <div className="flex items-center gap-2">
        <Switch
          id="rerankingEnabled"
          checked={effectiveRerankingEnabled}
          onCheckedChange={setRerankingEnabled}
        />
        <Label htmlFor="rerankingEnabled">{t("contextAugmentation.rerankingLabel")}</Label>
      </div>

      {effectiveRerankingEnabled && (
        <>
          <div className="space-y-2">
            <Label htmlFor="rerankerBackend">
              {t("contextAugmentation.rerankerBackendLabel")}
            </Label>
            <select
              id="rerankerBackend"
              value={effectiveRerankerBackend}
              onChange={(e) => {
                setRerankerBackend(e.target.value as ProjectRerankerBackend);
                setRerankerModel("");
              }}
              className="border-input bg-background w-full rounded-md border px-3 py-2 text-sm"
            >
              <option value="none">{t("contextAugmentation.rerankerNone")}</option>
              <option value="cross_encoder">
                {t("contextAugmentation.rerankerCrossEncoder")}
              </option>
              <option value="inmemory">{t("contextAugmentation.rerankerInMemory")}</option>
              <option value="mmr">{t("contextAugmentation.rerankerMmr")}</option>
            </select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="rerankerModel">{t("contextAugmentation.rerankerModelLabel")}</Label>
            <select
              id="rerankerModel"
              value={effectiveRerankerModel}
              onChange={(e) => setRerankerModel(e.target.value)}
              disabled={effectiveRerankerBackend === "none"}
              className="border-input bg-background w-full rounded-md border px-3 py-2 text-sm disabled:opacity-60"
            >
              <option value="">
                {effectiveRerankerBackend === "none"
                  ? t("contextAugmentation.selectRerankerBackend")
                  : t("contextAugmentation.selectModel")}
              </option>
              {rerankerModelOptions.map((model) => (
                <option key={model.id} value={model.id}>
                  {model.label}
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="rerankerCandidateMultiplier">
              {t("contextAugmentation.candidateMultiplierLabel")}
            </Label>
            <Input
              id="rerankerCandidateMultiplier"
              type="number"
              min={1}
              max={10}
              value={effectiveRerankerCandidateMultiplier}
              onChange={(e) => {
                const parsed = Number.parseInt(e.target.value, 10);
                if (Number.isNaN(parsed)) return;
                setRerankerCandidateMultiplier(Math.max(1, Math.min(10, parsed)));
              }}
            />
            <p className="text-xs text-muted-foreground">
              {t("contextAugmentation.candidateMultiplierNote")}
            </p>
          </div>
        </>
      )}

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
