"use client";

import { useParams } from "next/navigation";
import { ProjectSettingsTemplate } from "@/components/templates/project/project-settings-template";

export default function ProjectSettingsPage() {
  const params = useParams<{ projectId: string }>();
  return <ProjectSettingsTemplate projectId={params.projectId} />;
}
