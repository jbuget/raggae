"use client";

import { useTranslations } from "next-intl";
import { Label } from "@/components/ui/label";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import type { ModelCatalogResponse, ModelProvider, ProjectEmbeddingBackend, ProjectLLMBackend } from "@/lib/types/api";
import { BACKEND_LABELS } from "@/lib/constants/backends";
import { FieldHint } from "@/components/atoms/feedback/field-hint";
import { SettingsFieldRow } from "@/components/atoms/settings/settings-field-row";

type Credential = { id: string; provider: ModelProvider; masked_key: string; is_active: boolean };

type ModelValues = {
  embeddingBackend: string;
  embeddingModel: string;
  embeddingCredentialId: string;
  llmBackend: string;
  llmModel: string;
  llmCredentialId: string;
};

type ModelStoredValues = {
  embedding_backend?: string | null;
  embedding_model?: string | null;
  llm_backend?: string | null;
  llm_model?: string | null;
};

type ModelInheritedValues = {
  embedding_backend?: string | null;
  embedding_model?: string | null;
  llm_backend?: string | null;
  llm_model?: string | null;
};

type ModelFallbackValues = {
  embedding_backend?: string | null;
  llm_backend?: string | null;
};

type ModelDirty = {
  embeddingBackend: boolean;
  embeddingModel: boolean;
  embeddingCredentialId: boolean;
  llmBackend: boolean;
  llmModel: boolean;
  llmCredentialId: boolean;
};

type ModelOnChange = {
  embeddingBackend: (val: string) => void;
  embeddingModel: (val: string) => void;
  embeddingCredentialId: (val: string) => void;
  llmBackend: (val: string) => void;
  llmModel: (val: string) => void;
  llmCredentialId: (val: string) => void;
};

type ModelSettingsFieldsProps = {
  idPrefix: string;
  values: ModelValues;
  storedValues?: ModelStoredValues | null;
  inheritedValues?: ModelInheritedValues | null;
  fallbackValues?: ModelFallbackValues | null;
  ownerType: "org" | "user" | "system";
  dirty: ModelDirty;
  onChange: ModelOnChange;
  modelCatalog?: ModelCatalogResponse;
  credentials: Credential[];
};

function renderNoneLabel(
  inherited: string | null | undefined,
  fallback: string | null | undefined,
  ownerLabel: string,
  defaultLabel: string,
): string {
  const val = inherited ?? fallback;
  if (!val) return "—";
  const prefix = inherited != null ? ownerLabel : defaultLabel;
  return `${prefix} (${BACKEND_LABELS[val] ?? val})`;
}

export function ModelSettingsFields({
  idPrefix,
  values,
  storedValues,
  inheritedValues,
  fallbackValues,
  ownerType,
  dirty,
  onChange,
  modelCatalog,
  credentials,
}: ModelSettingsFieldsProps) {
  const tSettings = useTranslations("projects.settings");
  const tInherited = useTranslations("projects.settings.inherited");

  const ownerLabel = ownerType === "org" ? tInherited("organization") : ownerType === "user" ? tInherited("user") : tInherited("default");
  const defaultLabel = tInherited("default");

  const activeCredentials = credentials.filter((c) => c.is_active);
  const credentialsByProvider = activeCredentials.reduce<Record<string, Array<{ id: string; masked_key: string }>>>(
    (acc, c) => { (acc[c.provider] ??= []).push({ id: c.id, masked_key: c.masked_key }); return acc; },
    {},
  );

  const embeddingProviderForHints = values.embeddingBackend === "openai" || values.embeddingBackend === "gemini"
    ? values.embeddingBackend : null;
  const llmProviderForHints = values.llmBackend === "openai" || values.llmBackend === "gemini" || values.llmBackend === "anthropic"
    ? values.llmBackend : null;
  const embeddingCredentialOptions = embeddingProviderForHints ? (credentialsByProvider[embeddingProviderForHints] ?? []) : [];
  const llmCredentialOptions = llmProviderForHints ? (credentialsByProvider[llmProviderForHints] ?? []) : [];
  const embeddingModelOptions = values.embeddingBackend !== "none"
    ? (modelCatalog?.embedding[values.embeddingBackend as ProjectEmbeddingBackend] ?? []) : [];
  const llmModelOptions = values.llmBackend !== "none"
    ? (modelCatalog?.llm[values.llmBackend as ProjectLLMBackend] ?? []) : [];

  const id = (field: string) => `${idPrefix}-${field}`;

  return (
    <>
      <div className="space-y-1">
        <p className="text-sm font-medium">{tSettings("models.embeddingTitle")}</p>
        <p className="text-sm text-muted-foreground">{tSettings("models.embeddingDescription")}</p>
      </div>
      <SettingsFieldRow
        label={<Label htmlFor={id("embeddingBackend")}>{tSettings("models.embeddingBackendLabel")}</Label>}
        dirty={dirty.embeddingBackend}
        hint={<FieldHint projectValue={storedValues?.embedding_backend} inheritedValue={inheritedValues?.embedding_backend} ownerType={ownerType} dirty={dirty.embeddingBackend} />}
      >
        <Select
          value={values.embeddingBackend}
          onValueChange={(val) => {
            onChange.embeddingBackend(val);
            onChange.embeddingModel("none");
            onChange.embeddingCredentialId("none");
          }}
        >
          <SelectTrigger id={id("embeddingBackend")} className="w-full">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="none">
              {renderNoneLabel(inheritedValues?.embedding_backend, fallbackValues?.embedding_backend, ownerLabel, defaultLabel)}
            </SelectItem>
            <SelectItem value="openai">{BACKEND_LABELS.openai}</SelectItem>
            <SelectItem value="gemini">{BACKEND_LABELS.gemini}</SelectItem>
            <SelectItem value="ollama">{BACKEND_LABELS.ollama}</SelectItem>
            <SelectItem value="inmemory">{BACKEND_LABELS.inmemory}</SelectItem>
          </SelectContent>
        </Select>
      </SettingsFieldRow>
      {values.embeddingBackend !== "none" && (
        <>
          <SettingsFieldRow
            label={<Label htmlFor={id("embeddingCredentialId")}>{tSettings("models.embeddingApiKeyLabel")}</Label>}
            dirty={dirty.embeddingCredentialId}
          >
            <Select
              value={values.embeddingCredentialId || "none"}
              onValueChange={(val) => onChange.embeddingCredentialId(val === "none" ? "" : val)}
              disabled={!embeddingProviderForHints}
            >
              <SelectTrigger id={id("embeddingCredentialId")} className="w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="none">
                  {embeddingProviderForHints ? tSettings("models.noSelection") : tSettings("models.selectEmbeddingFirst")}
                </SelectItem>
                {embeddingCredentialOptions.map((item) => (
                  <SelectItem key={item.id} value={item.id}>{item.masked_key}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </SettingsFieldRow>
          <SettingsFieldRow
            label={<Label htmlFor={id("embeddingModel")}>{tSettings("models.embeddingModelLabel")}</Label>}
            dirty={dirty.embeddingModel}
            hint={<FieldHint projectValue={storedValues?.embedding_model} inheritedValue={inheritedValues?.embedding_model} ownerType={ownerType} dirty={dirty.embeddingModel} />}
          >
            <Select
              value={embeddingModelOptions.some(m => m.id === values.embeddingModel) ? values.embeddingModel : "none"}
              onValueChange={(val) => onChange.embeddingModel(val === "none" ? "" : val)}
            >
              <SelectTrigger id={id("embeddingModel")} className="w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="none">{tSettings("models.selectModel")}</SelectItem>
                {embeddingModelOptions.map((m) => (
                  <SelectItem key={m.id} value={m.id}>{m.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </SettingsFieldRow>
        </>
      )}
      <hr className="border-border" />
      <div className="space-y-1">
        <p className="text-sm font-medium">{tSettings("models.llmTitle")}</p>
        <p className="text-sm text-muted-foreground">{tSettings("models.llmDescription")}</p>
      </div>
      <SettingsFieldRow
        label={<Label htmlFor={id("llmBackend")}>{tSettings("models.llmBackendLabel")}</Label>}
        dirty={dirty.llmBackend}
        hint={<FieldHint projectValue={storedValues?.llm_backend} inheritedValue={inheritedValues?.llm_backend} ownerType={ownerType} dirty={dirty.llmBackend} />}
      >
        <Select
          value={values.llmBackend}
          onValueChange={(val) => {
            onChange.llmBackend(val);
            onChange.llmModel("none");
            onChange.llmCredentialId("none");
          }}
        >
          <SelectTrigger id={id("llmBackend")} className="w-full">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="none">
              {renderNoneLabel(inheritedValues?.llm_backend, fallbackValues?.llm_backend, ownerLabel, defaultLabel)}
            </SelectItem>
            <SelectItem value="openai">{BACKEND_LABELS.openai}</SelectItem>
            <SelectItem value="gemini">{BACKEND_LABELS.gemini}</SelectItem>
            <SelectItem value="anthropic">{BACKEND_LABELS.anthropic}</SelectItem>
            <SelectItem value="ollama">{BACKEND_LABELS.ollama}</SelectItem>
            <SelectItem value="inmemory">{BACKEND_LABELS.inmemory}</SelectItem>
          </SelectContent>
        </Select>
      </SettingsFieldRow>
      {values.llmBackend !== "none" && (
        <>
          <SettingsFieldRow
            label={<Label htmlFor={id("llmCredentialId")}>{tSettings("models.llmApiKeyLabel")}</Label>}
            dirty={dirty.llmCredentialId}
          >
            <Select
              value={values.llmCredentialId || "none"}
              onValueChange={(val) => onChange.llmCredentialId(val === "none" ? "" : val)}
              disabled={!llmProviderForHints}
            >
              <SelectTrigger id={id("llmCredentialId")} className="w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="none">
                  {llmProviderForHints ? tSettings("models.noSelection") : tSettings("models.selectLlmFirst")}
                </SelectItem>
                {llmCredentialOptions.map((item) => (
                  <SelectItem key={item.id} value={item.id}>{item.masked_key}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </SettingsFieldRow>
          <SettingsFieldRow
            label={<Label htmlFor={id("llmModel")}>{tSettings("models.llmModelLabel")}</Label>}
            dirty={dirty.llmModel}
            hint={<FieldHint projectValue={storedValues?.llm_model} inheritedValue={inheritedValues?.llm_model} ownerType={ownerType} dirty={dirty.llmModel} />}
          >
            <Select
              value={llmModelOptions.some(m => m.id === values.llmModel) ? values.llmModel : "none"}
              onValueChange={(val) => onChange.llmModel(val === "none" ? "" : val)}
            >
              <SelectTrigger id={id("llmModel")} className="w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="none">{tSettings("models.selectModel")}</SelectItem>
                {llmModelOptions.map((m) => (
                  <SelectItem key={m.id} value={m.id}>{m.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </SettingsFieldRow>
        </>
      )}
    </>
  );
}
