"use client";

import { useTranslations } from "next-intl";
import { PageTemplate } from "@/components/templates/page-template";
import { UserSettings } from "@/components/organisms/settings/user-settings";

export function UserSettingsTemplate() {
  const t = useTranslations("settings");
  return (
    <PageTemplate title={t("title")} description={t("description")}>
      <UserSettings />
    </PageTemplate>
  );
}
