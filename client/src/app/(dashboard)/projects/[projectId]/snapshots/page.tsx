"use client";

import { useParams } from "next/navigation";
import { ProjectSnapshotsTemplate } from "@/components/templates/project/project-snapshots-template";

export default function ProjectSnapshotsPage() {
  const params = useParams<{ projectId: string }>();
  return <ProjectSnapshotsTemplate projectId={params.projectId} />;
}
