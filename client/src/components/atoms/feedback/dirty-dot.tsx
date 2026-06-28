"use client";

import { useTranslations } from "next-intl";

export function DirtyDot({ dirty }: { dirty: boolean }) {
  const t = useTranslations("projects.settings");
  if (!dirty) return null;
  return <span title={t("unsavedChange")} className="ml-1.5 inline-block h-1.5 w-1.5 rounded-full bg-blue-500" />;
}
