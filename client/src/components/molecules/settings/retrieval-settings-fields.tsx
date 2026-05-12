"use client";

import { useTranslations } from "next-intl";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import type { RetrievalStrategy } from "@/lib/types/api";
import { BACKEND_LABELS } from "@/lib/constants/backends";
import { FieldHint } from "@/components/atoms/feedback/field-hint";
import { SettingsFieldRow } from "@/components/atoms/settings/settings-field-row";

type RetrievalValues = {
  retrievalStrategy: string;
  retrievalTopK: number | null;
  retrievalMinScore: number | null;
};

type RetrievalStoredValues = {
  retrieval_strategy?: string | null;
  retrieval_top_k?: number | null;
  retrieval_min_score?: number | null;
};

type RetrievalInheritedValues = {
  retrieval_strategy?: string | null;
  retrieval_top_k?: number | null;
  retrieval_min_score?: number | null;
};

type RetrievalFallbackValues = {
  retrieval_strategy?: string | null;
};

type RetrievalDirty = {
  retrievalStrategy: boolean;
  retrievalTopK: boolean;
  retrievalMinScore: boolean;
};

type RetrievalOnChange = {
  retrievalStrategy: (val: RetrievalStrategy | null) => void;
  retrievalTopK: (val: number | null) => void;
  retrievalMinScore: (val: number | null) => void;
};

export type RetrievalSettingsFieldsProps = {
  idPrefix: string;
  values: RetrievalValues;
  storedValues?: RetrievalStoredValues | null;
  inheritedValues?: RetrievalInheritedValues | null;
  fallbackValues?: RetrievalFallbackValues | null;
  ownerType: "org" | "user" | "system";
  dirty: RetrievalDirty;
  onChange: RetrievalOnChange;
};

export function RetrievalSettingsFields({
  idPrefix,
  values,
  storedValues,
  inheritedValues,
  fallbackValues,
  ownerType,
  dirty,
  onChange,
}: RetrievalSettingsFieldsProps) {
  const t = useTranslations("projects.settings");
  const tInherited = useTranslations("projects.settings.inherited");

  const ownerLabel = ownerType === "org" ? tInherited("organization") : ownerType === "user" ? tInherited("user") : tInherited("default");
  const defaultLabel = tInherited("default");

  const inheritedStrategy = inheritedValues?.retrieval_strategy;
  const fallbackStrategy = fallbackValues?.retrieval_strategy;
  const strategyVal = inheritedStrategy ?? fallbackStrategy;
  const strategyPrefix = inheritedStrategy != null ? ownerLabel : defaultLabel;
  const strategyNoneLabel = strategyVal
    ? `${strategyPrefix} (${BACKEND_LABELS[strategyVal] ?? strategyVal})`
    : "—";

  const id = (field: string) => `${idPrefix}-${field}`;

  return (
    <>
      <p className="text-sm text-muted-foreground">{t("contextRetrieval.description")}</p>
      <SettingsFieldRow
        label={<Label htmlFor={id("retrievalStrategy")}>{t("contextRetrieval.searchTypeLabel")}</Label>}
        dirty={dirty.retrievalStrategy}
        hint={<FieldHint projectValue={storedValues?.retrieval_strategy} inheritedValue={inheritedValues?.retrieval_strategy} ownerType={ownerType} dirty={dirty.retrievalStrategy} />}
      >
        <Select
          value={values.retrievalStrategy}
          onValueChange={(val) => onChange.retrievalStrategy(val === "none" ? null : val as RetrievalStrategy)}
        >
          <SelectTrigger id={id("retrievalStrategy")} className="w-full">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="none">{strategyNoneLabel}</SelectItem>
            <SelectItem value="hybrid">{t("contextRetrieval.hybrid")}</SelectItem>
            <SelectItem value="vector">{t("contextRetrieval.vector")}</SelectItem>
            <SelectItem value="fulltext">{t("contextRetrieval.fulltext")}</SelectItem>
          </SelectContent>
        </Select>
      </SettingsFieldRow>
      <SettingsFieldRow
        label={<Label htmlFor={id("retrievalTopK")}>{t("contextRetrieval.topKLabel")}</Label>}
        description={t("contextRetrieval.topKNote")}
        dirty={dirty.retrievalTopK}
        hint={<FieldHint projectValue={storedValues?.retrieval_top_k} inheritedValue={inheritedValues?.retrieval_top_k} ownerType={ownerType} dirty={dirty.retrievalTopK} />}
      >
        <Input
          id={id("retrievalTopK")}
          type="number"
          min={1}
          max={40}
          className="w-full"
          value={values.retrievalTopK ?? ""}
          onChange={(e) => { const v = Number.parseInt(e.target.value, 10); onChange.retrievalTopK(Number.isNaN(v) ? null : Math.max(1, Math.min(40, v))); }}
        />
      </SettingsFieldRow>
      <SettingsFieldRow
        label={<Label htmlFor={id("retrievalMinScore")}>{t("contextRetrieval.minScoreLabel")}</Label>}
        description={t("contextRetrieval.minScoreNote")}
        dirty={dirty.retrievalMinScore}
        hint={<FieldHint projectValue={storedValues?.retrieval_min_score} inheritedValue={inheritedValues?.retrieval_min_score} ownerType={ownerType} dirty={dirty.retrievalMinScore} />}
      >
        <Input
          id={id("retrievalMinScore")}
          type="number"
          min={0}
          max={1}
          step={0.05}
          className="w-full"
          value={values.retrievalMinScore ?? ""}
          onChange={(e) => { const v = Number.parseFloat(e.target.value); onChange.retrievalMinScore(Number.isNaN(v) ? null : Math.round(Math.max(0, Math.min(1, v)) * 100) / 100); }}
        />
      </SettingsFieldRow>
    </>
  );
}
