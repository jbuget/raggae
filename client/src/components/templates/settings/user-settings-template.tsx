"use client";

import { useTranslations } from "next-intl";
import { PageTemplate } from "@/components/templates/page-template";
import { UserProfilePanel } from "@/components/organisms/settings/user-profile-panel";
import { UserLocalePanel } from "@/components/organisms/settings/user-locale-panel";
import { UserApiKeysPanel } from "@/components/organisms/settings/user-api-keys-panel";

export function UserSettingsTemplate() {
  const t = useTranslations("settings");
  return (
    <PageTemplate title={t("title")} description={t("description")}>
      <div className="mx-auto w-full max-w-4xl space-y-6">
        <UserProfilePanel />
        <UserLocalePanel />
        <UserApiKeysPanel />
      </div>
    </PageTemplate>
  );
}
