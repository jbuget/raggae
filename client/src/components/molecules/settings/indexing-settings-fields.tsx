"use client";

import { useTranslations } from "next-intl";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import type { ChunkingStrategy } from "@/lib/types/api";
import { BACKEND_LABELS } from "@/lib/constants/backends";
import { FieldHint } from "@/components/atoms/feedback/field-hint";

type IndexingValues = {
  chunkingStrategy: string;
  parentChildChunking: boolean;
};

type IndexingStoredValues = {
  chunking_strategy?: string | null;
  parent_child_chunking?: boolean | null;
};

type IndexingInheritedValues = {
  chunking_strategy?: string | null;
  parent_child_chunking?: boolean | null;
};

type IndexingFallbackValues = {
  chunking_strategy?: string | null;
};

type IndexingDirty = {
  chunkingStrategy: boolean;
  parentChildChunking: boolean;
};

type IndexingOnChange = {
  chunkingStrategy: (val: ChunkingStrategy | null) => void;
  parentChildChunking: (val: boolean) => void;
};

export type IndexingSettingsFieldsProps = {
  idPrefix: string;
  values: IndexingValues;
  storedValues?: IndexingStoredValues | null;
  inheritedValues?: IndexingInheritedValues | null;
  fallbackValues?: IndexingFallbackValues | null;
  ownerType: "org" | "user" | "system";
  dirty: IndexingDirty;
  onChange: IndexingOnChange;
};

export function IndexingSettingsFields({
  idPrefix,
  values,
  storedValues,
  inheritedValues,
  fallbackValues,
  ownerType,
  dirty,
  onChange,
}: IndexingSettingsFieldsProps) {
  const t = useTranslations("projects.settings");
  const tForm = useTranslations("projects.form");
  const tInherited = useTranslations("projects.settings.inherited");

  const ownerLabel = ownerType === "org" ? tInherited("organization") : ownerType === "user" ? tInherited("user") : tInherited("default");
  const defaultLabel = tInherited("default");

  const inheritedChunking = inheritedValues?.chunking_strategy;
  const fallbackChunking = fallbackValues?.chunking_strategy;
  const chunkingVal = inheritedChunking ?? fallbackChunking;
  const chunkingPrefix = inheritedChunking != null ? ownerLabel : defaultLabel;
  const chunkingNoneLabel = chunkingVal
    ? `${chunkingPrefix} (${BACKEND_LABELS[chunkingVal] ?? chunkingVal})`
    : "—";

  const id = (field: string) => `${idPrefix}-${field}`;

  return (
    <>
      <div className="space-y-2">
        <Label htmlFor={id("chunkingStrategy")}>{t("knowledgeIndexing.chunkingLabel")}</Label>
        <Select
          value={values.chunkingStrategy}
          onValueChange={(val) => onChange.chunkingStrategy(val === "none" ? null : val as ChunkingStrategy)}
        >
          <SelectTrigger id={id("chunkingStrategy")}>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="none">{chunkingNoneLabel}</SelectItem>
            <SelectItem value="auto">{tForm("chunkingAuto")}</SelectItem>
            <SelectItem value="fixed_window">{tForm("chunkingFixed")}</SelectItem>
            <SelectItem value="paragraph">{tForm("chunkingParagraph")}</SelectItem>
            <SelectItem value="heading_section">{tForm("chunkingHeading")}</SelectItem>
            <SelectItem value="semantic">{tForm("chunkingSemantic")}</SelectItem>
          </SelectContent>
        </Select>
        <FieldHint projectValue={storedValues?.chunking_strategy} inheritedValue={inheritedValues?.chunking_strategy} ownerType={ownerType} dirty={dirty.chunkingStrategy} />
      </div>
      <div className="flex items-center gap-2">
        <Switch
          id={id("parentChildChunking")}
          checked={values.parentChildChunking}
          onCheckedChange={onChange.parentChildChunking}
        />
        <Label htmlFor={id("parentChildChunking")}>{t("knowledgeIndexing.parentChildLabel")}</Label>
      </div>
      <FieldHint projectValue={storedValues?.parent_child_chunking} inheritedValue={inheritedValues?.parent_child_chunking} ownerType={ownerType} dirty={dirty.parentChildChunking} />
    </>
  );
}
