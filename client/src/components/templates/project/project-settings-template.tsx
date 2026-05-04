"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { History } from "lucide-react";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { PageTemplate } from "@/components/templates/page-template";
import { ProjectGeneralPanel } from "@/components/organisms/project/settings/project-general-panel";
import { ProjectInstructionsPanel } from "@/components/organisms/project/settings/project-instructions-panel";
import { ProjectKnowledgePanel } from "@/components/organisms/project/settings/project-knowledge-panel";
import { ProjectAdvancedPanel } from "@/components/organisms/project/settings/project-advanced-panel";
import { ProjectName } from "@/components/organisms/project/project-name";
import { ProjectSnapshotsSheet } from "@/components/organisms/project/project-snapshots-sheet";

const SETTINGS_TABS = ["General", "Instructions", "Knowledge", "Advanced"] as const;
type SettingsTab = (typeof SETTINGS_TABS)[number];

interface ProjectSettingsTemplateProps {
  projectId: string;
}

export function ProjectSettingsTemplate({ projectId }: ProjectSettingsTemplateProps) {
  const t = useTranslations("projects.settings");
  const router = useRouter();
  const searchParams = useSearchParams();

  const tabFromUrl = searchParams.get("tab");
  const [activeTab, setActiveTab] = useState<SettingsTab>(
    SETTINGS_TABS.find((tab) => tab === tabFromUrl) ?? "General",
  );
  const [versionsOpen, setVersionsOpen] = useState(false);

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

  return (
    <PageTemplate title={<ProjectName projectId={projectId} />}>
      <div className="max-w-3xl space-y-8">
        <div className="flex items-end justify-between border-b">
          <div
            role="tablist"
            aria-label="Project settings sections"
            className="flex flex-wrap items-end gap-4"
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
          <Button
            variant="ghost"
            size="sm"
            className="mb-1 gap-1.5"
            onClick={() => setVersionsOpen(true)}
          >
            <History className="size-4" />
            {t("tabs.history")}
          </Button>
        </div>

        {activeTab === "General" && <ProjectGeneralPanel projectId={projectId} />}
        {activeTab === "Instructions" && <ProjectInstructionsPanel projectId={projectId} />}
        {activeTab === "Knowledge" && <ProjectKnowledgePanel projectId={projectId} />}
        {activeTab === "Advanced" && <ProjectAdvancedPanel projectId={projectId} />}
      </div>

      <ProjectSnapshotsSheet
        projectId={projectId}
        open={versionsOpen}
        onOpenChange={setVersionsOpen}
      />
    </PageTemplate>
  );
}
