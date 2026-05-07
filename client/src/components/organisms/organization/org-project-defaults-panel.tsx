"use client";

import { useTranslations } from "next-intl";
import { toast } from "sonner";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { ProjectDefaultsForm } from "@/components/molecules/settings/project-defaults-form";
import { useModelCatalog } from "@/lib/hooks/use-model-catalog";
import { useOrgModelCredentials } from "@/lib/hooks/use-org-model-credentials";
import { useSystemDefaults } from "@/lib/hooks/use-system-defaults";
import {
  useOrganizationProjectDefaults,
  useUpsertOrganizationProjectDefaults,
} from "@/lib/hooks/use-org-project-defaults";

type OrgProjectDefaultsPanelProps = {
  organizationId: string;
};

export function OrgProjectDefaultsPanel({ organizationId }: OrgProjectDefaultsPanelProps) {
  const t = useTranslations("organizations.projectDefaults");

  const { data: defaults, isLoading, isError } = useOrganizationProjectDefaults(organizationId);
  const { data: systemDefaults } = useSystemDefaults();
  const upsert = useUpsertOrganizationProjectDefaults(organizationId);
  const { data: modelCatalog } = useModelCatalog();
  const { data: orgCredentials } = useOrgModelCredentials(organizationId);

  if (isLoading) {
    return (
      <Card className="space-y-4 p-5">
        <Skeleton className="h-6 w-48" />
        <Skeleton className="h-40 w-full" />
      </Card>
    );
  }

  if (isError) {
    return <p className="text-sm text-destructive">{t("loadError")}</p>;
  }

  return (
    <ProjectDefaultsForm
      defaults={defaults}
      systemDefaults={systemDefaults}
      showReset
      credentials={orgCredentials ?? []}
      modelCatalog={modelCatalog}
      onSave={(payload, callbacks) => {
        upsert.mutate(payload, {
          onSuccess: () => {
            toast.success(t("saveSuccess"));
            callbacks?.onSuccess?.();
          },
          onError: () => {
            toast.error(t("saveError"));
            callbacks?.onError?.();
          },
        });
      }}
      isPending={upsert.isPending}
      idPrefix="org"
      title={t("title")}
      description={t("description")}
    />
  );
}
