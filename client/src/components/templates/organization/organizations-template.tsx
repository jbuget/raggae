"use client";

import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { PageTemplate } from "@/components/templates/page-template";
import { OrganizationList } from "@/components/organisms/organization/organization-list";

export function OrganizationsTemplate() {
  const t = useTranslations("organizations");
  const router = useRouter();
  return (
    <PageTemplate
      title={t("title")}
      description={t("description")}
      actions={
        <Button onClick={() => router.push("/organizations?create=1")}>
          {t("new")}
        </Button>
      }
    >
      <OrganizationList />
    </PageTemplate>
  );
}
