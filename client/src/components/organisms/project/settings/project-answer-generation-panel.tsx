"use client";

import { useState } from "react";
import { toast } from "sonner";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useProject, useUpdateProject } from "@/lib/hooks/use-projects";

const MAX_SYSTEM_PROMPT_LENGTH = 8000;

export function ProjectAnswerGenerationPanel({ projectId }: { projectId: string }) {
  const t = useTranslations("projects.settings");
  const tCommon = useTranslations("common");

  const { data: project } = useProject(projectId);
  const updateProject = useUpdateProject(projectId);

  const [systemPrompt, setSystemPrompt] = useState<string | null>(null);
  const [chatHistoryWindowSize, setChatHistoryWindowSize] = useState<number | null>(null);
  const [chatHistoryMaxChars, setChatHistoryMaxChars] = useState<number | null>(null);

  if (!project) return null;

  const effectiveSystemPrompt = systemPrompt ?? (project.system_prompt ?? "");
  const effectiveChatHistoryWindowSize =
    chatHistoryWindowSize ?? project.chat_history_window_size ?? 8;
  const effectiveChatHistoryMaxChars =
    chatHistoryMaxChars ?? project.chat_history_max_chars ?? 4000;

  const hasChanges =
    effectiveSystemPrompt !== (project.system_prompt ?? "") ||
    effectiveChatHistoryWindowSize !== (project.chat_history_window_size ?? 8) ||
    effectiveChatHistoryMaxChars !== (project.chat_history_max_chars ?? 4000);

  const systemPromptLength = effectiveSystemPrompt.length;
  const nearSystemPromptLimit = systemPromptLength >= 7000;

  function handleSave() {
    updateProject.mutate(
      {
        system_prompt: effectiveSystemPrompt,
        chat_history_window_size: effectiveChatHistoryWindowSize,
        chat_history_max_chars: effectiveChatHistoryMaxChars,
      },
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
          <span
            className={`text-xs ${nearSystemPromptLimit ? "text-amber-700" : "text-muted-foreground"}`}
          >
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

      <div className="space-y-2">
        <Label htmlFor="chatHistoryWindowSize">
          {t("answerGeneration.chatHistoryWindowLabel")}
        </Label>
        <Input
          id="chatHistoryWindowSize"
          type="number"
          min={1}
          max={40}
          value={effectiveChatHistoryWindowSize}
          onChange={(e) => {
            const parsed = Number.parseInt(e.target.value, 10);
            if (Number.isNaN(parsed)) return;
            setChatHistoryWindowSize(Math.max(1, Math.min(40, parsed)));
          }}
        />
        <p className="text-xs text-muted-foreground">
          {t("answerGeneration.chatHistoryWindowNote")}
        </p>
      </div>

      <div className="space-y-2">
        <Label htmlFor="chatHistoryMaxChars">
          {t("answerGeneration.chatHistoryMaxCharsLabel")}
        </Label>
        <Input
          id="chatHistoryMaxChars"
          type="number"
          min={128}
          max={16000}
          value={effectiveChatHistoryMaxChars}
          onChange={(e) => {
            const parsed = Number.parseInt(e.target.value, 10);
            if (Number.isNaN(parsed)) return;
            setChatHistoryMaxChars(Math.max(128, Math.min(16000, parsed)));
          }}
        />
        <p className="text-xs text-muted-foreground">
          {t("answerGeneration.chatHistoryMaxCharsNote")}
        </p>
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
