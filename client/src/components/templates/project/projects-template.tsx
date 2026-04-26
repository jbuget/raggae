"use client";

import { useTranslations } from "next-intl";
import { PageTemplate } from "@/components/templates/page-template";
import { ProjectList } from "@/components/organisms/project/project-list";

export function ProjectsTemplate() {
  const t = useTranslations("projects");
  return (
    <PageTemplate title={t("title")}>
      <ProjectList />
    </PageTemplate>
  );
}
