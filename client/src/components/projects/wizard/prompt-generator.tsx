"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { useGeneratePrompt } from "@/lib/hooks/use-generate-prompt";

interface PromptGeneratorProps {
  projectName: string;
  onGenerated: (prompt: string) => void;
  onClose: () => void;
}

export function PromptGenerator({ projectName, onGenerated, onClose }: PromptGeneratorProps) {
  const t = useTranslations("projects.wizard.promptGenerator");
  const [description, setDescription] = useState("");
  const generatePrompt = useGeneratePrompt();

  async function handleGenerate() {
    if (!description.trim()) return;
    const result = await generatePrompt.mutateAsync({
      description: description.trim(),
      name: projectName,
    });
    onGenerated(result.system_prompt);
    onClose();
  }

  return (
    <div className="rounded-lg border bg-muted/50 p-4 space-y-3">
      <p className="text-sm font-medium">{t("title")}</p>
      <div className="space-y-2">
        <Label htmlFor="generator-description">{t("descriptionLabel")}</Label>
        <Textarea
          id="generator-description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder={t("descriptionPlaceholder")}
          rows={3}
          autoFocus
        />
      </div>
      <div className="flex justify-end gap-2">
        <Button variant="ghost" size="sm" onClick={onClose} disabled={generatePrompt.isPending}>
          {t("cancel")}
        </Button>
        <Button
          size="sm"
          onClick={handleGenerate}
          disabled={!description.trim() || generatePrompt.isPending}
        >
          {generatePrompt.isPending ? t("generating") : t("generate")}
        </Button>
      </div>
    </div>
  );
}
