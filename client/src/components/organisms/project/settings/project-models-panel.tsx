"use client";

import { useState } from "react";
import { toast } from "sonner";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { useProject, useUpdateProject } from "@/lib/hooks/use-projects";
import { useModelCatalog } from "@/lib/hooks/use-model-catalog";
import { useModelCredentials } from "@/lib/hooks/use-model-credentials";
import { useOrgModelCredentials } from "@/lib/hooks/use-org-model-credentials";
import type {
  ModelProvider,
  ProjectEmbeddingBackend,
  ProjectLLMBackend,
} from "@/lib/types/api";

export function ProjectModelsPanel({ projectId }: { projectId: string }) {
  const t = useTranslations("projects.settings");
  const tCommon = useTranslations("common");

  const { data: project } = useProject(projectId);
  const updateProject = useUpdateProject(projectId);
  const { data: modelCatalog } = useModelCatalog();
  const { data: userCredentials } = useModelCredentials();
  const { data: orgCredentials } = useOrgModelCredentials(project?.organization_id);
  const credentials = project?.organization_id ? orgCredentials : userCredentials;

  const [embeddingBackend, setEmbeddingBackend] = useState<
    ProjectEmbeddingBackend | "" | undefined
  >(undefined);
  const [embeddingModel, setEmbeddingModel] = useState<string | null>(null);
  const [embeddingCredentialId, setEmbeddingCredentialId] = useState<string | null>(null);
  const [llmBackend, setLlmBackend] = useState<ProjectLLMBackend | "" | undefined>(undefined);
  const [llmModel, setLlmModel] = useState<string | null>(null);
  const [llmCredentialId, setLlmCredentialId] = useState<string | null>(null);

  if (!project) return null;

  const effectiveEmbeddingBackend =
    embeddingBackend === undefined ? (project.embedding_backend ?? "") : embeddingBackend;
  const effectiveLlmBackend =
    llmBackend === undefined ? (project.llm_backend ?? "") : llmBackend;
  const effectiveEmbeddingModel =
    effectiveEmbeddingBackend === "" ? "" : (embeddingModel ?? (project.embedding_model ?? ""));
  const effectiveLlmModel =
    effectiveLlmBackend === "" ? "" : (llmModel ?? (project.llm_model ?? ""));

  const storedEmbeddingCredentialId = project.organization_id
    ? (project.org_embedding_api_key_credential_id ?? "")
    : (project.embedding_api_key_credential_id ?? "");
  const storedLlmCredentialId = project.organization_id
    ? (project.org_llm_api_key_credential_id ?? "")
    : (project.llm_api_key_credential_id ?? "");
  const effectiveEmbeddingCredentialId =
    effectiveEmbeddingBackend === ""
      ? ""
      : (embeddingCredentialId ?? storedEmbeddingCredentialId);
  const effectiveLlmCredentialId =
    effectiveLlmBackend === "" ? "" : (llmCredentialId ?? storedLlmCredentialId);

  const hasChanges =
    effectiveEmbeddingBackend !== (project.embedding_backend ?? "") ||
    effectiveEmbeddingModel !== (project.embedding_model ?? "") ||
    effectiveLlmBackend !== (project.llm_backend ?? "") ||
    effectiveLlmModel !== (project.llm_model ?? "") ||
    effectiveEmbeddingCredentialId !== "" ||
    effectiveLlmCredentialId !== "";

  const credentialsByProvider = (credentials ?? [])
    .filter((c) => c.is_active)
    .reduce<Record<ModelProvider, Array<{ id: string; masked_key: string }>>>(
      (acc, credential) => {
        acc[credential.provider].push({ id: credential.id, masked_key: credential.masked_key });
        return acc;
      },
      { openai: [], gemini: [], anthropic: [] },
    );

  const embeddingProviderForHints =
    effectiveEmbeddingBackend === "openai" || effectiveEmbeddingBackend === "gemini"
      ? effectiveEmbeddingBackend
      : null;
  const llmProviderForHints =
    effectiveLlmBackend === "openai" ||
    effectiveLlmBackend === "gemini" ||
    effectiveLlmBackend === "anthropic"
      ? effectiveLlmBackend
      : null;

  const embeddingCredentialOptions = embeddingProviderForHints
    ? credentialsByProvider[embeddingProviderForHints]
    : [];
  const llmCredentialOptions = llmProviderForHints
    ? credentialsByProvider[llmProviderForHints]
    : [];
  const embeddingModelOptions = effectiveEmbeddingBackend
    ? (modelCatalog?.embedding[effectiveEmbeddingBackend as ProjectEmbeddingBackend] ?? [])
    : [];
  const llmModelOptions = effectiveLlmBackend
    ? (modelCatalog?.llm[effectiveLlmBackend as ProjectLLMBackend] ?? [])
    : [];

  function handleSave() {
    updateProject.mutate(
      {
        embedding_backend: effectiveEmbeddingBackend || null,
        embedding_model: effectiveEmbeddingModel || null,
        embedding_api_key: null,
        embedding_api_key_credential_id: effectiveEmbeddingCredentialId || null,
        llm_backend: effectiveLlmBackend || null,
        llm_model: effectiveLlmModel || null,
        llm_api_key: null,
        llm_api_key_credential_id: effectiveLlmCredentialId || null,
      },
      {
        onSuccess: () => toast.success(t("updateSuccess")),
        onError: () => toast.error(t("updateError")),
      },
    );
  }

  return (
    <div className="max-w-3xl space-y-4 rounded-md">
      <p className="text-base font-semibold tracking-tight">{t("models.embeddingTitle")}</p>
      <p className="text-sm text-muted-foreground">{t("models.embeddingDescription")}</p>

      <div className="space-y-2">
        <Label htmlFor="embeddingBackend">{t("models.embeddingBackendLabel")}</Label>
        <select
          id="embeddingBackend"
          value={effectiveEmbeddingBackend}
          onChange={(e) => {
            setEmbeddingBackend((e.target.value || "") as ProjectEmbeddingBackend | "");
            setEmbeddingModel("");
            setEmbeddingCredentialId("");
          }}
          className="border-input bg-background w-full rounded-md border px-3 py-2 text-sm"
        >
          <option value="">Default</option>
          <option value="openai">OpenAI</option>
          <option value="gemini">Gemini</option>
          <option value="ollama">Ollama</option>
          <option value="inmemory">InMemory</option>
        </select>
      </div>

      {effectiveEmbeddingBackend ? (
        <>
          <div className="space-y-2">
            <Label htmlFor="embeddingCredentialId">{t("models.embeddingApiKeyLabel")}</Label>
            {project.embedding_api_key_masked && (
              <p className="text-xs text-muted-foreground">
                {t("models.existingKey", { key: project.embedding_api_key_masked })}
              </p>
            )}
            <select
              id="embeddingCredentialId"
              value={effectiveEmbeddingCredentialId}
              onChange={(e) => setEmbeddingCredentialId(e.target.value)}
              disabled={!embeddingProviderForHints}
              className="border-input bg-background w-full rounded-md border px-3 py-2 text-sm disabled:opacity-60"
            >
              <option value="">
                {embeddingProviderForHints
                  ? t("models.noSelection")
                  : t("models.selectEmbeddingFirst")}
              </option>
              {embeddingCredentialOptions.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.masked_key}
                </option>
              ))}
            </select>
            <p className="text-xs text-muted-foreground">
              {embeddingProviderForHints
                ? t("models.savedKeysFor", {
                    provider: embeddingProviderForHints,
                    keys:
                      embeddingCredentialOptions.length > 0
                        ? embeddingCredentialOptions.map((i) => i.masked_key).join(", ")
                        : t("models.noKeys"),
                  })
                : t("models.embeddingCredentialsNote")}
            </p>
          </div>
          <div className="space-y-2">
            <Label htmlFor="embeddingModel">{t("models.embeddingModelLabel")}</Label>
            <select
              id="embeddingModel"
              value={effectiveEmbeddingModel}
              onChange={(e) => setEmbeddingModel(e.target.value)}
              className="border-input bg-background w-full rounded-md border px-3 py-2 text-sm"
            >
              <option value="">{t("models.selectModel")}</option>
              {embeddingModelOptions.map((model) => (
                <option key={model.id} value={model.id}>
                  {model.label}
                </option>
              ))}
            </select>
          </div>
        </>
      ) : null}

      <hr className="border-border" />

      <p className="text-base font-semibold tracking-tight">{t("models.llmTitle")}</p>
      <p className="text-sm text-muted-foreground">{t("models.llmDescription")}</p>

      <div className="space-y-2">
        <Label htmlFor="llmBackend">{t("models.llmBackendLabel")}</Label>
        <select
          id="llmBackend"
          value={effectiveLlmBackend}
          onChange={(e) => {
            setLlmBackend((e.target.value || "") as ProjectLLMBackend | "");
            setLlmModel("");
            setLlmCredentialId("");
          }}
          className="border-input bg-background w-full rounded-md border px-3 py-2 text-sm"
        >
          <option value="">Default</option>
          <option value="openai">OpenAI</option>
          <option value="gemini">Gemini</option>
          <option value="anthropic">Anthropic</option>
          <option value="ollama">Ollama</option>
          <option value="inmemory">InMemory</option>
        </select>
      </div>

      {effectiveLlmBackend ? (
        <>
          <div className="space-y-2">
            <Label htmlFor="llmCredentialId">{t("models.llmApiKeyLabel")}</Label>
            {project.llm_api_key_masked && (
              <p className="text-xs text-muted-foreground">
                {t("models.existingKey", { key: project.llm_api_key_masked })}
              </p>
            )}
            <select
              id="llmCredentialId"
              value={effectiveLlmCredentialId}
              onChange={(e) => setLlmCredentialId(e.target.value)}
              disabled={!llmProviderForHints}
              className="border-input bg-background w-full rounded-md border px-3 py-2 text-sm disabled:opacity-60"
            >
              <option value="">
                {llmProviderForHints ? t("models.noSelection") : t("models.selectLlmFirst")}
              </option>
              {llmCredentialOptions.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.masked_key}
                </option>
              ))}
            </select>
            <p className="text-xs text-muted-foreground">
              {llmProviderForHints
                ? t("models.savedKeysFor", {
                    provider: llmProviderForHints,
                    keys:
                      llmCredentialOptions.length > 0
                        ? llmCredentialOptions.map((i) => i.masked_key).join(", ")
                        : t("models.noKeys"),
                  })
                : t("models.llmCredentialsNote")}
            </p>
          </div>
          <div className="space-y-2">
            <Label htmlFor="llmModel">{t("models.llmModelLabel")}</Label>
            <select
              id="llmModel"
              value={effectiveLlmModel}
              onChange={(e) => setLlmModel(e.target.value)}
              className="border-input bg-background w-full rounded-md border px-3 py-2 text-sm"
            >
              <option value="">{t("models.selectModel")}</option>
              {llmModelOptions.map((model) => (
                <option key={model.id} value={model.id}>
                  {model.label}
                </option>
              ))}
            </select>
          </div>
        </>
      ) : null}

      <hr className="border-border" />

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
