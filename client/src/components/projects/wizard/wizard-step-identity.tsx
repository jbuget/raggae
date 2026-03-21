"use client";

import { useTranslations } from "next-intl";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";

interface WizardStepIdentityProps {
  name: string;
  description: string;
  onNameChange: (value: string) => void;
  onDescriptionChange: (value: string) => void;
  onNext: () => void;
}

export function WizardStepIdentity({
  name,
  description,
  onNameChange,
  onDescriptionChange,
  onNext,
}: WizardStepIdentityProps) {
  const t = useTranslations("projects.wizard");

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="wizard-name">{t("nameLabel")}</Label>
        <Input
          id="wizard-name"
          value={name}
          onChange={(e) => onNameChange(e.target.value)}
          placeholder={t("namePlaceholder")}
          autoFocus
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="wizard-description">{t("descriptionLabel")}</Label>
        <Textarea
          id="wizard-description"
          value={description}
          onChange={(e) => onDescriptionChange(e.target.value)}
          placeholder={t("descriptionPlaceholder")}
          rows={3}
        />
        <p className="text-xs text-muted-foreground">{t("descriptionHint")}</p>
      </div>
      <div className="flex justify-end">
        <Button onClick={onNext} disabled={!name.trim()}>
          {t("next")}
        </Button>
      </div>
    </div>
  );
}
