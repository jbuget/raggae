"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Textarea } from "@/components/ui/textarea";
import type {
  ChunkingStrategy,
  CreateProjectRequest,
  ProjectResponse,
  UpdateProjectRequest,
} from "@/lib/types/api";

type ProjectFormData = CreateProjectRequest | UpdateProjectRequest;

interface ProjectFormProps {
  initialData?: ProjectResponse;
  onSubmit: (data: ProjectFormData) => void;
  isLoading?: boolean;
  submitLabel?: string;
}

const MAX_SYSTEM_PROMPT_LENGTH = 8000;

export function ProjectForm({
  initialData,
  onSubmit,
  isLoading = false,
  submitLabel,
}: ProjectFormProps) {
  const t = useTranslations("projects.form");
  const tCommon = useTranslations("common");
  const isCreateMode = initialData === undefined;
  const [name, setName] = useState(initialData?.name ?? "");
  const [description, setDescription] = useState(initialData?.description ?? "");
  const [systemPrompt, setSystemPrompt] = useState(initialData?.system_prompt ?? "");
  const [chunkingStrategy, setChunkingStrategy] = useState<ChunkingStrategy>(
    initialData?.chunking_strategy ?? "auto"
  );
  const [parentChildChunking, setParentChildChunking] = useState<boolean>(
    initialData?.parent_child_chunking ?? false
  );
  const [reindexWarningOpen, setReindexWarningOpen] = useState(false);
  const [pendingFormData, setPendingFormData] = useState<ProjectFormData | null>(null);

  const isDisabled = !name.trim() || isLoading;

  const parentChildChanged =
    initialData !== undefined &&
    parentChildChunking !== initialData.parent_child_chunking;
  const isSemanticRecommended =
    parentChildChunking && chunkingStrategy !== "semantic";
  const systemPromptLength = systemPrompt.length;
  const nearSystemPromptLimit = systemPromptLength >= 7000;

  function buildFormData(): ProjectFormData {
    if (isCreateMode) {
      return {
        name: name.trim(),
        description,
      };
    }
    return {
      name: name.trim(),
      description,
      system_prompt: systemPrompt,
      chunking_strategy: chunkingStrategy,
      parent_child_chunking: parentChildChunking,
    };
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const data = buildFormData();

    if (!isCreateMode && parentChildChanged) {
      setPendingFormData(data);
      setReindexWarningOpen(true);
    } else {
      onSubmit(data);
    }
  }

  function handleConfirmReindex() {
    setReindexWarningOpen(false);
    if (pendingFormData) {
      onSubmit(pendingFormData);
      setPendingFormData(null);
    }
  }

  function handleCancelReindex() {
    setReindexWarningOpen(false);
    setPendingFormData(null);
  }

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle>
            {initialData ? t("editTitle") : t("newTitle")}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-4">
              <h3 className="text-base font-semibold">{t("presentationSection")}</h3>
              <div className="space-y-2">
                <Label htmlFor="name">{t("nameLabel")}</Label>
                <Input
                  id="name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder={t("namePlaceholder")}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="description">{t("descriptionLabel")}</Label>
                <Textarea
                  id="description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder={t("descriptionPlaceholder")}
                  rows={3}
                />
              </div>
            </div>

            {isCreateMode ? null : (
              <>
                <Separator />

                <div className="space-y-4">
                  <h3 className="text-base font-semibold">{t("promptSection")}</h3>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <Label htmlFor="systemPrompt">{t("systemPromptLabel")}</Label>
                      <span
                        className={`text-xs ${
                          nearSystemPromptLimit ? "text-amber-700" : "text-muted-foreground"
                        }`}
                      >
                        {systemPromptLength}/{MAX_SYSTEM_PROMPT_LENGTH}
                      </span>
                    </div>
                    <Textarea
                      id="systemPrompt"
                      value={systemPrompt}
                      onChange={(e) => setSystemPrompt(e.target.value)}
                      placeholder={t("systemPromptPlaceholder")}
                      rows={5}
                      maxLength={MAX_SYSTEM_PROMPT_LENGTH}
                    />
                    <p className="text-muted-foreground text-xs">
                      {t("systemPromptLimit")}
                    </p>
                    {nearSystemPromptLimit ? (
                      <p className="text-xs text-amber-700">
                        {t("systemPromptNearLimit")}
                      </p>
                    ) : null}
                  </div>
                </div>
                <Separator />

                <div className="space-y-4">
                  <h3 className="text-base font-semibold">{t("knowledgeSection")}</h3>
                  <p className="text-muted-foreground text-sm">
                    {t("knowledgeDescription")}
                  </p>
                  <div className="space-y-2">
                    <Label htmlFor="chunkingStrategy">{t("chunkingStrategyLabel")}</Label>
                    <select
                      id="chunkingStrategy"
                      value={chunkingStrategy}
                      onChange={(e) => setChunkingStrategy(e.target.value as ChunkingStrategy)}
                      className="border-input bg-background w-full rounded-md border px-3 py-2 text-sm"
                    >
                      <option value="auto">{t("chunkingAuto")}</option>
                      <option value="fixed_window">{t("chunkingFixed")}</option>
                      <option value="paragraph">{t("chunkingParagraph")}</option>
                      <option value="heading_section">{t("chunkingHeading")}</option>
                      <option value="semantic">{t("chunkingSemantic")}</option>
                    </select>
                    <p className="text-muted-foreground text-sm">
                      {t("chunkingDescription")}
                    </p>
                  </div>
                </div>

                <Separator />

                <div className="space-y-4">
                  <h3 className="text-base font-semibold">{t("indexingSection")}</h3>
                  <div className="flex items-center gap-2">
                    <input
                      id="parentChildChunking"
                      type="checkbox"
                      checked={parentChildChunking}
                      onChange={(e) => setParentChildChunking(e.target.checked)}
                      className="h-4 w-4"
                    />
                    <Label htmlFor="parentChildChunking">{t("parentChildLabel")}</Label>
                  </div>
                  <p className="text-muted-foreground text-sm">
                    {t("parentChildDescription")}
                  </p>
                  <p className="text-muted-foreground text-sm">
                    {t("parentChildRecommendation")}
                  </p>
                  {isSemanticRecommended ? (
                    <p className="text-sm text-amber-700">
                      {t("parentChildWarning")}
                    </p>
                  ) : null}
                </div>

                <Separator />

                <div className="space-y-2">
                  <h3 className="text-base font-semibold">{t("retrievalSection")}</h3>
                  <p className="text-muted-foreground text-sm">
                    {t("retrievalDescription")}
                  </p>
                </div>

                <Separator />

                <div className="space-y-2">
                  <h3 className="text-base font-semibold">{t("answerSection")}</h3>
                  <p className="text-muted-foreground text-sm">
                    {t("answerDescription")}
                  </p>
                </div>
              </>
            )}

            <Button type="submit" className="cursor-pointer" disabled={isDisabled}>
              {isLoading ? tCommon("saving") : (submitLabel ?? t("newTitle"))}
            </Button>
          </form>
        </CardContent>
      </Card>

      <Dialog open={!isCreateMode && reindexWarningOpen} onOpenChange={setReindexWarningOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t("reindexTitle")}</DialogTitle>
            <DialogDescription>
              {parentChildChunking
                ? t("reindexEnableDescription")
                : t("reindexDisableDescription")}
              {" "}{t("reindexDocumentsWarning")}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              className="cursor-pointer"
              onClick={handleCancelReindex}
            >
              {tCommon("cancel")}
            </Button>
            <Button
              className="cursor-pointer"
              onClick={handleConfirmReindex}
            >
              {t("confirmAndSave")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
