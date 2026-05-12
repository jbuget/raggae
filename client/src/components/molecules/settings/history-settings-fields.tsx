"use client";

import { useTranslations } from "next-intl";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { FieldHint } from "@/components/atoms/feedback/field-hint";

type HistoryValues = {
  chatHistoryWindowSize: number | null;
  chatHistoryMaxChars: number | null;
};

type HistoryStoredValues = {
  chat_history_window_size?: number | null;
  chat_history_max_chars?: number | null;
};

type HistoryInheritedValues = {
  chat_history_window_size?: number | null;
  chat_history_max_chars?: number | null;
};

type HistoryDirty = {
  chatHistoryWindowSize: boolean;
  chatHistoryMaxChars: boolean;
};

type HistoryOnChange = {
  chatHistoryWindowSize: (val: number | null) => void;
  chatHistoryMaxChars: (val: number | null) => void;
};

export type HistorySettingsFieldsProps = {
  idPrefix: string;
  values: HistoryValues;
  storedValues?: HistoryStoredValues | null;
  inheritedValues?: HistoryInheritedValues | null;
  ownerType: "org" | "user" | "system";
  dirty: HistoryDirty;
  onChange: HistoryOnChange;
};

export function HistorySettingsFields({
  idPrefix,
  values,
  storedValues,
  inheritedValues,
  ownerType,
  dirty,
  onChange,
}: HistorySettingsFieldsProps) {
  const t = useTranslations("projects.settings");

  const id = (field: string) => `${idPrefix}-${field}`;

  return (
    <>
      <div className="space-y-2">
        <Label htmlFor={id("chatHistoryWindowSize")}>{t("answerGeneration.chatHistoryWindowLabel")}</Label>
        <Input
          id={id("chatHistoryWindowSize")}
          type="number"
          min={1}
          max={40}
          value={values.chatHistoryWindowSize ?? ""}
          onChange={(e) => { const v = Number.parseInt(e.target.value, 10); onChange.chatHistoryWindowSize(Number.isNaN(v) ? null : Math.max(1, Math.min(40, v))); }}
        />
        <FieldHint projectValue={storedValues?.chat_history_window_size} inheritedValue={inheritedValues?.chat_history_window_size} ownerType={ownerType} dirty={dirty.chatHistoryWindowSize} />
        <p className="text-xs text-muted-foreground">{t("answerGeneration.chatHistoryWindowNote")}</p>
      </div>
      <div className="space-y-2">
        <Label htmlFor={id("chatHistoryMaxChars")}>{t("answerGeneration.chatHistoryMaxCharsLabel")}</Label>
        <Input
          id={id("chatHistoryMaxChars")}
          type="number"
          min={128}
          max={16000}
          value={values.chatHistoryMaxChars ?? ""}
          onChange={(e) => { const v = Number.parseInt(e.target.value, 10); onChange.chatHistoryMaxChars(Number.isNaN(v) ? null : Math.max(128, Math.min(16000, v))); }}
        />
        <FieldHint projectValue={storedValues?.chat_history_max_chars} inheritedValue={inheritedValues?.chat_history_max_chars} ownerType={ownerType} dirty={dirty.chatHistoryMaxChars} />
        <p className="text-xs text-muted-foreground">{t("answerGeneration.chatHistoryMaxCharsNote")}</p>
      </div>
    </>
  );
}
