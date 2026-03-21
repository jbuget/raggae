"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { useTranslations } from "next-intl";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useCreateProject } from "@/lib/hooks/use-projects";
import { useAuth } from "@/lib/hooks/use-auth";
import { uploadDocuments } from "@/lib/api/documents";
import { WizardStepIdentity } from "./wizard-step-identity";
import { WizardStepPrompt } from "./wizard-step-prompt";
import { WizardStepDocuments } from "./wizard-step-documents";

type Step = 1 | 2 | 3;

interface ProjectWizardProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  organizationId?: string | null;
}

const STEP_LABELS = ["wizard.step.identity", "wizard.step.prompt", "wizard.step.documents"] as const;

export function ProjectWizard({ open, onOpenChange, organizationId }: ProjectWizardProps) {
  const t = useTranslations("projects");
  const router = useRouter();
  const { token } = useAuth();
  const createProject = useCreateProject();

  const [step, setStep] = useState<Step>(1);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [systemPrompt, setSystemPrompt] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  function reset() {
    setStep(1);
    setName("");
    setDescription("");
    setSystemPrompt("");
    setFiles([]);
    setIsSubmitting(false);
  }

  function handleOpenChange(open: boolean) {
    if (!open) reset();
    onOpenChange(open);
  }

  async function handleSubmit() {
    if (!name.trim()) return;
    setIsSubmitting(true);
    try {
      const project = await createProject.mutateAsync({
        name: name.trim(),
        description,
        system_prompt: systemPrompt,
        organization_id: organizationId ?? null,
      });

      if (files.length > 0 && token) {
        try {
          await uploadDocuments(token, project.id, files);
        } catch {
          toast.warning(t("wizard.uploadWarning"));
        }
      }

      toast.success(t("wizard.createSuccess"));
      handleOpenChange(false);
      router.push(`/projects/${project.id}`);
    } catch {
      toast.error(t("wizard.createError"));
      setIsSubmitting(false);
    }
  }

  const stepTitles: Record<Step, string> = {
    1: t("wizard.step.identity"),
    2: t("wizard.step.prompt"),
    3: t("wizard.step.documents"),
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>{t("wizard.title")}</DialogTitle>
        </DialogHeader>

        <div className="flex items-center gap-2 py-2">
          {([1, 2, 3] as Step[]).map((s) => (
            <div key={s} className="flex items-center gap-2">
              <div
                className={`flex h-6 w-6 items-center justify-center rounded-full text-xs font-medium ${
                  s === step
                    ? "bg-primary text-primary-foreground"
                    : s < step
                      ? "bg-primary/20 text-primary"
                      : "bg-muted text-muted-foreground"
                }`}
              >
                {s}
              </div>
              <span className={`text-xs ${s === step ? "font-medium" : "text-muted-foreground"}`}>
                {stepTitles[s]}
              </span>
              {s < 3 && <div className="h-px w-6 bg-border" />}
            </div>
          ))}
        </div>

        {step === 1 && (
          <WizardStepIdentity
            name={name}
            description={description}
            onNameChange={setName}
            onDescriptionChange={setDescription}
            onNext={() => setStep(2)}
          />
        )}
        {step === 2 && (
          <WizardStepPrompt
            projectName={name}
            systemPrompt={systemPrompt}
            onSystemPromptChange={setSystemPrompt}
            onNext={() => setStep(3)}
            onBack={() => setStep(1)}
          />
        )}
        {step === 3 && (
          <WizardStepDocuments
            files={files}
            onFilesChange={setFiles}
            onSubmit={handleSubmit}
            onBack={() => setStep(2)}
            isSubmitting={isSubmitting}
          />
        )}
      </DialogContent>
    </Dialog>
  );
}
