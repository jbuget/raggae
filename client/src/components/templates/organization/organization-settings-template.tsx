"use client";

import { useTranslations } from "next-intl";
import { PageTemplate } from "@/components/templates/page-template";
import { OrganizationSettings } from "@/components/organisms/organization/organization-settings";

interface OrganizationSettingsTemplateProps {
  organizationId: string;
}

export function OrganizationSettingsTemplate({ organizationId }: OrganizationSettingsTemplateProps) {
  const t = useTranslations("organizations.settings");

  return (
    <PageTemplate title={t("title")} description={t("description")}>
      <OrganizationSettings organizationId={organizationId} />
    </PageTemplate>
  );
}
