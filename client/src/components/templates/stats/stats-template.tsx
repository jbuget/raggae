"use client";

import { useTranslations } from "next-intl";
import { PageTemplate } from "@/components/templates/page-template";
import { StatsPage } from "@/components/organisms/stats/stats-page";

export function StatsTemplate() {
  const t = useTranslations("stats");
  return (
    <PageTemplate title={t("pageTitle")} description={t("pageDescription")}>
      <StatsPage />
    </PageTemplate>
  );
}
