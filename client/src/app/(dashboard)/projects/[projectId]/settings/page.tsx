"use client";

import { useParams, useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { ProjectForm } from "@/components/projects/project-form";
import {
  useDeleteProject,
  useProject,
  useUpdateProject,
} from "@/lib/hooks/use-projects";

export default function ProjectSettingsPage() {
  const params = useParams<{ projectId: string }>();
  const router = useRouter();
  const { data: project, isLoading } = useProject(params.projectId);
  const updateProject = useUpdateProject(params.projectId);
  const deleteProject = useDeleteProject();
  const [deleteOpen, setDeleteOpen] = useState(false);

  if (isLoading) {
    return (
      <div className="mx-auto max-w-2xl space-y-4">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (!project) {
    return <div className="text-center text-muted-foreground">Project not found</div>;
  }

  return (
    <div className="mx-auto max-w-2xl space-y-8">
      <ProjectForm
        initialData={project}
        submitLabel="Save Changes"
        isLoading={updateProject.isPending}
        onSubmit={(data) => {
          updateProject.mutate(data, {
            onSuccess: () => toast.success("Project updated"),
            onError: () => toast.error("Failed to update project"),
          });
        }}
      />

      <Separator />

      <div className="space-y-4">
        <h2 className="text-lg font-semibold text-destructive">Danger Zone</h2>
        <Dialog open={deleteOpen} onOpenChange={setDeleteOpen}>
          <DialogTrigger asChild>
            <Button variant="destructive">Delete Project</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Delete Project</DialogTitle>
              <DialogDescription>
                Are you sure you want to delete &quot;{project.name}&quot;? This
                action cannot be undone.
              </DialogDescription>
            </DialogHeader>
            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setDeleteOpen(false)}
              >
                Cancel
              </Button>
              <Button
                variant="destructive"
                disabled={deleteProject.isPending}
                onClick={() => {
                  deleteProject.mutate(project.id, {
                    onSuccess: () => {
                      toast.success("Project deleted");
                      router.push("/projects");
                    },
                    onError: () => toast.error("Failed to delete project"),
                  });
                }}
              >
                {deleteProject.isPending ? "Deleting..." : "Delete"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
}
