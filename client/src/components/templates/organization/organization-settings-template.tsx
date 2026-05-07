"use client";

import { useTranslations } from "next-intl";
import { PageTemplate } from "@/components/templates/page-template";
import { OrganizationSettings } from "@/components/organisms/organization/organization-settings";
import { Skeleton } from "@/components/ui/skeleton";
import { useOrganization } from "@/lib/hooks/use-organization";

interface OrganizationSettingsTemplateProps {
  organizationId: string;
}

export function OrganizationSettingsTemplate({ organizationId }: OrganizationSettingsTemplateProps) {
  const t = useTranslations("organizations.settings");
  const { data: organization, isLoading } = useOrganization(organizationId);
  const title = isLoading
    ? <Skeleton className="inline-block h-6 w-40" />
    : (organization?.name ?? t("title"));

  return (
    <PageTemplate title={title} description={t("description")}>
      <OrganizationSettings organizationId={organizationId} />
    </PageTemplate>
  );
}
