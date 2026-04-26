"use client";

import { useTranslations } from "next-intl";
import { PageTemplate } from "@/components/templates/page-template";
import { OrganizationList } from "@/components/organisms/organization/organization-list";

export function OrganizationsTemplate() {
  const t = useTranslations("organizations");
  return (
    <PageTemplate title={t("title")}>
      <OrganizationList />
    </PageTemplate>
  );
}
