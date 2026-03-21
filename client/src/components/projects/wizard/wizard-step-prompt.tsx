"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { PromptGenerator } from "./prompt-generator";

const MAX_PROMPT_LENGTH = 8000;

interface WizardStepPromptProps {
  projectName: string;
  systemPrompt: string;
  onSystemPromptChange: (value: string) => void;
  onNext: () => void;
  onBack: () => void;
}

export function WizardStepPrompt({
  projectName,
  systemPrompt,
  onSystemPromptChange,
  onNext,
  onBack,
}: WizardStepPromptProps) {
  const t = useTranslations("projects.wizard");
  const [showGenerator, setShowGenerator] = useState(false);
  const isNearLimit = systemPrompt.length > MAX_PROMPT_LENGTH * 0.9;
  const isOverLimit = systemPrompt.length > MAX_PROMPT_LENGTH;

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <Label htmlFor="wizard-prompt">{t("promptLabel")}</Label>
          {!showGenerator && (
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => setShowGenerator(true)}
            >
              ✨ {t("generatePrompt")}
            </Button>
          )}
        </div>

        {showGenerator && (
          <PromptGenerator
            projectName={projectName}
            onGenerated={(prompt) => {
              onSystemPromptChange(prompt);
              setShowGenerator(false);
            }}
            onClose={() => setShowGenerator(false)}
          />
        )}

        <Textarea
          id="wizard-prompt"
          value={systemPrompt}
          onChange={(e) => onSystemPromptChange(e.target.value)}
          placeholder={t("promptPlaceholder")}
          rows={8}
          className={isOverLimit ? "border-destructive" : ""}
        />
        <p className={`text-xs ${isOverLimit ? "text-destructive" : isNearLimit ? "text-orange-500" : "text-muted-foreground"}`}>
          {systemPrompt.length} / {MAX_PROMPT_LENGTH}
          {isNearLimit && !isOverLimit && ` — ${t("promptNearLimit")}`}
          {isOverLimit && ` — ${t("promptOverLimit")}`}
        </p>
      </div>

      <div className="flex justify-between">
        <Button variant="ghost" onClick={onBack}>
          {t("back")}
        </Button>
        <Button onClick={onNext} disabled={isOverLimit}>
          {t("next")}
        </Button>
      </div>
    </div>
  );
}
