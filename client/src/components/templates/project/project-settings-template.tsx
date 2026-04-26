"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { Skeleton } from "@/components/ui/skeleton";
import { PageTemplate } from "@/components/templates/page-template";
import { ProjectGeneralPanel } from "@/components/organisms/project/settings/project-general-panel";
import { ProjectInstructionsPanel } from "@/components/organisms/project/settings/project-instructions-panel";
import { ProjectKnowledgePanel } from "@/components/organisms/project/settings/project-knowledge-panel";
import { ProjectAdvancedPanel } from "@/components/organisms/project/settings/project-advanced-panel";
import { useProject } from "@/lib/hooks/use-projects";

const SETTINGS_TABS = ["General", "Instructions", "Knowledge", "Advanced"] as const;
type SettingsTab = (typeof SETTINGS_TABS)[number];

interface ProjectSettingsTemplateProps {
  projectId: string;
}

export function ProjectSettingsTemplate({ projectId }: ProjectSettingsTemplateProps) {
  const t = useTranslations("projects.settings");
  const router = useRouter();
  const searchParams = useSearchParams();

  const { data: project, isLoading } = useProject(projectId);

  const tabFromUrl = searchParams.get("tab");
  const [activeTab, setActiveTab] = useState<SettingsTab>(
    SETTINGS_TABS.find((tab) => tab === tabFromUrl) ?? "General",
  );

  const tabLabels: Record<SettingsTab, string> = {
    General: t("tabs.general"),
    Instructions: t("tabs.instructions"),
    Knowledge: t("tabs.knowledge"),
    Advanced: t("tabs.advanced"),
  };

  function handleTabChange(tab: SettingsTab) {
    setActiveTab(tab);
    const next = new URLSearchParams(searchParams.toString());
    next.set("tab", tab);
    router.replace(`?${next.toString()}`, { scroll: false });
  }

  if (isLoading) {
    return (
      <PageTemplate title="">
        <div className="w-full space-y-4">
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-64 w-full" />
        </div>
      </PageTemplate>
    );
  }

  if (!project) {
    return (
      <PageTemplate title="">
        <div className="text-center text-muted-foreground">{t("notFound")}</div>
      </PageTemplate>
    );
  }

  return (
    <PageTemplate title={project.name}>
      <div className="w-full space-y-8">
        <div
          role="tablist"
          aria-label="Project settings sections"
          className="flex flex-wrap items-end gap-4 border-b"
        >
          {SETTINGS_TABS.map((tab) => {
            const isActive = activeTab === tab;
            return (
              <button
                key={tab}
                type="button"
                role="tab"
                aria-selected={isActive}
                className={[
                  "cursor-pointer border-b-2 px-1 py-3 text-sm whitespace-nowrap transition-colors",
                  isActive
                    ? "border-primary text-foreground font-medium"
                    : "border-transparent text-muted-foreground hover:text-foreground",
                ].join(" ")}
                onClick={() => handleTabChange(tab)}
              >
                {tabLabels[tab]}
              </button>
            );
          })}
        </div>

        {activeTab === "General" && <ProjectGeneralPanel projectId={projectId} />}
        {activeTab === "Instructions" && <ProjectInstructionsPanel projectId={projectId} />}
        {activeTab === "Knowledge" && <ProjectKnowledgePanel projectId={projectId} />}
        {activeTab === "Advanced" && <ProjectAdvancedPanel projectId={projectId} />}
      </div>
    </PageTemplate>
  );
}
