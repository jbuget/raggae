"use client";

import { useParams } from "next/navigation";
import { ProjectDetailTemplate } from "@/components/templates/project/project-detail-template";

export default function ProjectDetailPage() {
  const params = useParams<{ projectId: string }>();
  return <ProjectDetailTemplate projectId={params.projectId} />;
}
