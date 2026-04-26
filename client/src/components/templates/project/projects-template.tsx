"use client";

import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { PageTemplate } from "@/components/templates/page-template";
import { ProjectList } from "@/components/organisms/project/project-list";

export function ProjectsTemplate() {
  const t = useTranslations("projects");
  const router = useRouter();
  return (
    <PageTemplate
      title={t("title")}
      description={t("description")}
      actions={
        <Button onClick={() => router.push("/projects?create=1")}>
          {t("new")}
        </Button>
      }
    >
      <ProjectList />
    </PageTemplate>
  );
}
