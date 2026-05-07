"use client";

import { useTranslations } from "next-intl";
import { toast } from "sonner";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { ProjectDefaultsForm } from "@/components/molecules/settings/project-defaults-form";
import { useModelCatalog } from "@/lib/hooks/use-model-catalog";
import { useModelCredentials } from "@/lib/hooks/use-model-credentials";
import { useSystemDefaults } from "@/lib/hooks/use-system-defaults";
import { useUpsertUserProjectDefaults, useUserProjectDefaults } from "@/lib/hooks/use-user-project-defaults";

export function UserProjectDefaultsPanel() {
  const t = useTranslations("settings.userProjectDefaults");
  const tSettings = useTranslations("projects.settings");

  const { data: defaults, isLoading, isError } = useUserProjectDefaults();
  const { data: systemDefaults } = useSystemDefaults();
  const upsert = useUpsertUserProjectDefaults();
  const { data: modelCatalog } = useModelCatalog();
  const { data: credentials } = useModelCredentials();

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
      credentials={credentials ?? []}
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
      idPrefix="user"
      title={t("title")}
      description={t("description")}
    />
  );
}
