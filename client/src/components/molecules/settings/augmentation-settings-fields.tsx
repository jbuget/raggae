"use client";

import { useTranslations } from "next-intl";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import type { ModelCatalogResponse, ProjectRerankerBackend } from "@/lib/types/api";
import { FieldHint } from "@/components/atoms/feedback/field-hint";
import { SettingsFieldRow } from "@/components/atoms/settings/settings-field-row";

type AugmentationValues = {
  rerankingEnabled: boolean;
  rerankerBackend: string;
  rerankerModel: string;
  rerankerCandidateMultiplier: number | null;
};

type AugmentationStoredValues = {
  reranking_enabled?: boolean | null;
  reranker_backend?: string | null;
  reranker_candidate_multiplier?: number | null;
};

type AugmentationInheritedValues = {
  reranking_enabled?: boolean | null;
  reranker_backend?: string | null;
  reranker_candidate_multiplier?: number | null;
};

type AugmentationFallbackValues = {
  reranking_enabled?: boolean | null;
  reranker_candidate_multiplier?: number | null;
};

type AugmentationDirty = {
  rerankingEnabled: boolean;
  rerankerBackend: boolean;
  rerankerModel: boolean;
  rerankerCandidateMultiplier: boolean;
};

type AugmentationOnChange = {
  rerankingEnabled: (val: boolean) => void;
  rerankerBackend: (val: ProjectRerankerBackend | null) => void;
  rerankerModel: (val: string) => void;
  rerankerCandidateMultiplier: (val: number | null) => void;
};

export type AugmentationSettingsFieldsProps = {
  idPrefix: string;
  values: AugmentationValues;
  storedValues?: AugmentationStoredValues | null;
  inheritedValues?: AugmentationInheritedValues | null;
  fallbackValues?: AugmentationFallbackValues | null;
  ownerType: "org" | "user" | "system";
  dirty: AugmentationDirty;
  onChange: AugmentationOnChange;
  modelCatalog?: ModelCatalogResponse;
};

export function AugmentationSettingsFields({
  idPrefix,
  values,
  storedValues,
  inheritedValues,
  fallbackValues,
  ownerType,
  dirty,
  onChange,
  modelCatalog,
}: AugmentationSettingsFieldsProps) {
  const t = useTranslations("projects.settings");

  const rerankerModelOptions = (values.rerankerBackend && values.rerankerBackend !== "none")
    ? (modelCatalog?.reranker[values.rerankerBackend as ProjectRerankerBackend] ?? []) : [];

  const effectiveInheritedRerankingEnabled = inheritedValues?.reranking_enabled ?? fallbackValues?.reranking_enabled;
  const rerankingEnabledOwnerType = inheritedValues?.reranking_enabled != null ? ownerType : "system" as const;
  const effectiveInheritedCandidateMultiplier = inheritedValues?.reranker_candidate_multiplier ?? fallbackValues?.reranker_candidate_multiplier;
  const candidateMultiplierOwnerType = inheritedValues?.reranker_candidate_multiplier != null ? ownerType : "system" as const;

  const id = (field: string) => `${idPrefix}-${field}`;

  return (
    <>
      <SettingsFieldRow
        label={<Label htmlFor={id("rerankingEnabled")}>{t("contextAugmentation.rerankingLabel")}</Label>}
        description={t("contextAugmentation.rerankingNote")}
        dirty={dirty.rerankingEnabled}
        hint={<FieldHint projectValue={storedValues?.reranking_enabled} inheritedValue={effectiveInheritedRerankingEnabled} ownerType={rerankingEnabledOwnerType} dirty={dirty.rerankingEnabled} />}
      >
        <Switch
          id={id("rerankingEnabled")}
          checked={values.rerankingEnabled}
          onCheckedChange={onChange.rerankingEnabled}
        />
      </SettingsFieldRow>
      {values.rerankingEnabled && (
        <>
          <SettingsFieldRow
            label={<Label htmlFor={id("rerankerBackend")}>{t("contextAugmentation.rerankerBackendLabel")}</Label>}
            description={t("contextAugmentation.rerankerBackendNote")}
            dirty={dirty.rerankerBackend}
            hint={<FieldHint projectValue={storedValues?.reranker_backend} inheritedValue={inheritedValues?.reranker_backend} ownerType={ownerType} dirty={dirty.rerankerBackend} />}
          >
            <Select
              value={values.rerankerBackend}
              onValueChange={(val) => {
                onChange.rerankerBackend(val === "none" ? null : val as ProjectRerankerBackend);
                onChange.rerankerModel("");
              }}
            >
              <SelectTrigger id={id("rerankerBackend")} className="w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="none">{t("contextAugmentation.rerankerNone")}</SelectItem>
                <SelectItem value="cross_encoder">{t("contextAugmentation.rerankerCrossEncoder")}</SelectItem>
                <SelectItem value="inmemory">{t("contextAugmentation.rerankerInMemory")}</SelectItem>
                <SelectItem value="mmr">{t("contextAugmentation.rerankerMmr")}</SelectItem>
              </SelectContent>
            </Select>
          </SettingsFieldRow>
          <SettingsFieldRow
            label={<Label htmlFor={id("rerankerModel")}>{t("contextAugmentation.rerankerModelLabel")}</Label>}
            description={t("contextAugmentation.rerankerModelNote")}
            dirty={dirty.rerankerModel}
          >
            <Select
              value={rerankerModelOptions.some(m => m.id === values.rerankerModel) ? values.rerankerModel : "none"}
              onValueChange={(val) => onChange.rerankerModel(val === "none" ? "" : val)}
              disabled={values.rerankerBackend === "none"}
            >
              <SelectTrigger id={id("rerankerModel")} className="w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="none">
                  {values.rerankerBackend === "none" ? t("contextAugmentation.selectRerankerBackend") : t("contextAugmentation.selectModel")}
                </SelectItem>
                {rerankerModelOptions.map((m) => (
                  <SelectItem key={m.id} value={m.id}>{m.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </SettingsFieldRow>
          <SettingsFieldRow
            label={<Label htmlFor={id("rerankerCandidateMultiplier")}>{t("contextAugmentation.candidateMultiplierLabel")}</Label>}
            description={t("contextAugmentation.candidateMultiplierNote")}
            dirty={dirty.rerankerCandidateMultiplier}
            hint={<FieldHint projectValue={storedValues?.reranker_candidate_multiplier} inheritedValue={effectiveInheritedCandidateMultiplier} ownerType={candidateMultiplierOwnerType} dirty={dirty.rerankerCandidateMultiplier} />}
          >
            <Input
              id={id("rerankerCandidateMultiplier")}
              type="number"
              min={1}
              max={10}
              className="w-full"
              value={values.rerankerCandidateMultiplier ?? ""}
              onChange={(e) => { const v = Number.parseInt(e.target.value, 10); onChange.rerankerCandidateMultiplier(Number.isNaN(v) ? null : Math.max(1, Math.min(10, v))); }}
            />
          </SettingsFieldRow>
        </>
      )}
    </>
  );
}
