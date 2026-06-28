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
import { SettingsFieldRow } from "@/components/atoms/settings/settings-field-row";

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
  parent_child_chunking?: boolean | null;
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

  const effectiveInheritedParentChild = inheritedValues?.parent_child_chunking ?? fallbackValues?.parent_child_chunking;
  const parentChildOwnerType = inheritedValues?.parent_child_chunking != null ? ownerType : "system" as const;

  const id = (field: string) => `${idPrefix}-${field}`;

  return (
    <>
      <SettingsFieldRow
        label={<Label htmlFor={id("chunkingStrategy")}>{t("knowledgeIndexing.chunkingLabel")}</Label>}
        dirty={dirty.chunkingStrategy}
        hint={<FieldHint projectValue={storedValues?.chunking_strategy} inheritedValue={inheritedValues?.chunking_strategy} ownerType={ownerType} dirty={dirty.chunkingStrategy} />}
      >
        <Select
          value={values.chunkingStrategy}
          onValueChange={(val) => onChange.chunkingStrategy(val === "none" ? null : val as ChunkingStrategy)}
        >
          <SelectTrigger id={id("chunkingStrategy")} className="w-full">
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
      </SettingsFieldRow>
      <SettingsFieldRow
        label={<Label htmlFor={id("parentChildChunking")}>{t("knowledgeIndexing.parentChildLabel")}</Label>}
        dirty={dirty.parentChildChunking}
        hint={<FieldHint projectValue={storedValues?.parent_child_chunking} inheritedValue={effectiveInheritedParentChild} ownerType={parentChildOwnerType} dirty={dirty.parentChildChunking} />}
      >
        <Switch
          id={id("parentChildChunking")}
          checked={values.parentChildChunking}
          onCheckedChange={onChange.parentChildChunking}
        />
      </SettingsFieldRow>
    </>
  );
}
