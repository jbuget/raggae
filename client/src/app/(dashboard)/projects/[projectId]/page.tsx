"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useProject } from "@/lib/hooks/use-projects";

export default function ProjectDetailPage() {
  const params = useParams<{ projectId: string }>();
  const { data: project, isLoading } = useProject(params.projectId);

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-32 w-full" />
      </div>
    );
  }

  if (!project) {
    return <div className="text-center text-muted-foreground">Project not found</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">{project.name}</h1>
        <Button asChild variant="outline" size="sm">
          <Link href={`/projects/${project.id}/settings`}>Settings</Link>
        </Button>
      </div>

      {project.description && (
        <p className="text-muted-foreground">{project.description}</p>
      )}

      <div className="grid gap-4 sm:grid-cols-3">
        <Link href={`/projects/${project.id}/chat`}>
          <Card className="transition-colors hover:bg-muted/50">
            <CardHeader>
              <CardTitle className="text-base">Chat</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Start a conversation with your documents
              </p>
            </CardContent>
          </Card>
        </Link>

        <Link href={`/projects/${project.id}/documents`}>
          <Card className="transition-colors hover:bg-muted/50">
            <CardHeader>
              <CardTitle className="text-base">Documents</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Upload and manage documents
              </p>
            </CardContent>
          </Card>
        </Link>

        <Link href={`/projects/${project.id}/settings`}>
          <Card className="transition-colors hover:bg-muted/50">
            <CardHeader>
              <CardTitle className="text-base">Settings</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Configure project settings
              </p>
            </CardContent>
          </Card>
        </Link>
      </div>
    </div>
  );
}
