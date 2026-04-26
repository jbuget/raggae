"use client";

import { useState } from "react";
import { toast } from "sonner";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useProject, useUpdateProject } from "@/lib/hooks/use-projects";

const MAX_SYSTEM_PROMPT_LENGTH = 8000;

export function ProjectInstructionsPanel({ projectId }: { projectId: string }) {
  const t = useTranslations("projects.settings");
  const tCommon = useTranslations("common");

  const { data: project } = useProject(projectId);
  const updateProject = useUpdateProject(projectId);

  const [systemPrompt, setSystemPrompt] = useState<string | null>(null);

  if (!project) return null;

  const effectiveSystemPrompt = systemPrompt ?? (project.system_prompt ?? "");
  const hasChanges = effectiveSystemPrompt !== (project.system_prompt ?? "");
  const systemPromptLength = effectiveSystemPrompt.length;
  const nearLimit = systemPromptLength >= 7000;

  function handleSave() {
    updateProject.mutate(
      { system_prompt: effectiveSystemPrompt },
      {
        onSuccess: () => toast.success(t("updateSuccess")),
        onError: () => toast.error(t("updateError")),
      },
    );
  }

  return (
    <div className="max-w-3xl space-y-4">
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <Label htmlFor="systemPrompt">{t("answerGeneration.promptLabel")}</Label>
          <span className={`text-xs ${nearLimit ? "text-amber-700" : "text-muted-foreground"}`}>
            {systemPromptLength}/{MAX_SYSTEM_PROMPT_LENGTH}
          </span>
        </div>
        <Textarea
          id="systemPrompt"
          value={effectiveSystemPrompt}
          onChange={(e) => setSystemPrompt(e.target.value)}
          placeholder={t("answerGeneration.promptPlaceholder")}
          rows={16}
          maxLength={MAX_SYSTEM_PROMPT_LENGTH}
        />
        <p className="text-xs text-muted-foreground">{t("answerGeneration.promptLimit")}</p>
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
