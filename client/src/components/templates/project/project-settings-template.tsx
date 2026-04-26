"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { Skeleton } from "@/components/ui/skeleton";
import { PageTemplate } from "@/components/templates/page-template";
import { ProjectGeneralPanel } from "@/components/organisms/project/settings/project-general-panel";
import { ProjectPublicationPanel } from "@/components/organisms/project/settings/project-publication-panel";
import { ProjectModelsPanel } from "@/components/organisms/project/settings/project-models-panel";
import { ProjectKnowledgeIndexingPanel } from "@/components/organisms/project/settings/project-knowledge-indexing-panel";
import { ProjectDocumentIngestionPanel } from "@/components/organisms/project/settings/project-document-ingestion-panel";
import { ProjectContextRetrievalPanel } from "@/components/organisms/project/settings/project-context-retrieval-panel";
import { ProjectContextAugmentationPanel } from "@/components/organisms/project/settings/project-context-augmentation-panel";
import { ProjectAnswerGenerationPanel } from "@/components/organisms/project/settings/project-answer-generation-panel";
import { ProjectSnapshotsList } from "@/components/organisms/project/project-snapshots-list";
import { useProject } from "@/lib/hooks/use-projects";

const SETTINGS_TABS = [
  "General",
  "Publication",
  "Models",
  "Knowledge indexing",
  "Document ingestion",
  "Context retrieval",
  "Context augmentation",
  "Answer generation",
  "History",
] as const;
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
    Publication: t("tabs.publication"),
    Models: t("tabs.models"),
    "Knowledge indexing": t("tabs.knowledgeIndexing"),
    "Document ingestion": t("tabs.documentIngestion"),
    "Context retrieval": t("tabs.contextRetrieval"),
    "Context augmentation": t("tabs.contextAugmentation"),
    "Answer generation": t("tabs.answerGeneration"),
    History: t("tabs.history"),
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

  const isProjectReindexing = project.reindex_status === "in_progress";

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

        {isProjectReindexing && (
          <div className="rounded-md border border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-900">
            {t("reindexingWarning", {
              progress: project.reindex_progress,
              total: project.reindex_total,
            })}
          </div>
        )}

        {activeTab === "General" && <ProjectGeneralPanel projectId={projectId} />}
        {activeTab === "Publication" && <ProjectPublicationPanel projectId={projectId} />}
        {activeTab === "Models" && <ProjectModelsPanel projectId={projectId} />}
        {activeTab === "Knowledge indexing" && (
          <ProjectKnowledgeIndexingPanel projectId={projectId} />
        )}
        {activeTab === "Document ingestion" && (
          <ProjectDocumentIngestionPanel projectId={projectId} />
        )}
        {activeTab === "Context retrieval" && (
          <ProjectContextRetrievalPanel projectId={projectId} />
        )}
        {activeTab === "Context augmentation" && (
          <ProjectContextAugmentationPanel projectId={projectId} />
        )}
        {activeTab === "Answer generation" && (
          <ProjectAnswerGenerationPanel projectId={projectId} />
        )}
        {activeTab === "History" && (
          <div className="max-w-3xl space-y-6">
            <ProjectSnapshotsList projectId={projectId} />
          </div>
        )}
      </div>
    </PageTemplate>
  );
}
