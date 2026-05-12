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
  ownerType,
  dirty,
  onChange,
  modelCatalog,
}: AugmentationSettingsFieldsProps) {
  const t = useTranslations("projects.settings");

  const rerankerModelOptions = (values.rerankerBackend && values.rerankerBackend !== "none")
    ? (modelCatalog?.reranker[values.rerankerBackend as ProjectRerankerBackend] ?? []) : [];

  const id = (field: string) => `${idPrefix}-${field}`;

  return (
    <>
      <div className="flex items-center gap-2">
        <Switch
          id={id("rerankingEnabled")}
          checked={values.rerankingEnabled}
          onCheckedChange={onChange.rerankingEnabled}
        />
        <Label htmlFor={id("rerankingEnabled")}>{t("contextAugmentation.rerankingLabel")}</Label>
      </div>
      <FieldHint projectValue={storedValues?.reranking_enabled} inheritedValue={inheritedValues?.reranking_enabled} ownerType={ownerType} dirty={dirty.rerankingEnabled} />
      {values.rerankingEnabled && (
        <>
          <div className="space-y-2">
            <Label htmlFor={id("rerankerBackend")}>{t("contextAugmentation.rerankerBackendLabel")}</Label>
            <Select
              value={values.rerankerBackend}
              onValueChange={(val) => {
                onChange.rerankerBackend(val === "none" ? null : val as ProjectRerankerBackend);
                onChange.rerankerModel("");
              }}
            >
              <SelectTrigger id={id("rerankerBackend")}>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="none">{t("contextAugmentation.rerankerNone")}</SelectItem>
                <SelectItem value="cross_encoder">{t("contextAugmentation.rerankerCrossEncoder")}</SelectItem>
                <SelectItem value="inmemory">{t("contextAugmentation.rerankerInMemory")}</SelectItem>
                <SelectItem value="mmr">{t("contextAugmentation.rerankerMmr")}</SelectItem>
              </SelectContent>
            </Select>
            <FieldHint projectValue={storedValues?.reranker_backend} inheritedValue={inheritedValues?.reranker_backend} ownerType={ownerType} dirty={dirty.rerankerBackend} />
          </div>
          <div className="space-y-2">
            <Label htmlFor={id("rerankerModel")}>{t("contextAugmentation.rerankerModelLabel")}</Label>
            <Select
              value={rerankerModelOptions.some(m => m.id === values.rerankerModel) ? values.rerankerModel : "none"}
              onValueChange={(val) => onChange.rerankerModel(val === "none" ? "" : val)}
              disabled={values.rerankerBackend === "none"}
            >
              <SelectTrigger id={id("rerankerModel")}>
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
          </div>
          <div className="space-y-2">
            <Label htmlFor={id("rerankerCandidateMultiplier")}>{t("contextAugmentation.candidateMultiplierLabel")}</Label>
            <Input
              id={id("rerankerCandidateMultiplier")}
              type="number"
              min={1}
              max={10}
              value={values.rerankerCandidateMultiplier ?? ""}
              onChange={(e) => { const v = Number.parseInt(e.target.value, 10); onChange.rerankerCandidateMultiplier(Number.isNaN(v) ? null : Math.max(1, Math.min(10, v))); }}
            />
            <FieldHint projectValue={storedValues?.reranker_candidate_multiplier} inheritedValue={inheritedValues?.reranker_candidate_multiplier} ownerType={ownerType} dirty={dirty.rerankerCandidateMultiplier} />
            <p className="text-xs text-muted-foreground">{t("contextAugmentation.candidateMultiplierNote")}</p>
          </div>
        </>
      )}
    </>
  );
}
