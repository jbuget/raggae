"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { Textarea } from "@/components/ui/textarea";
import { ProjectCard } from "./project-card";
import { useCreateProject, useProjects } from "@/lib/hooks/use-projects";

export function ProjectList() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { data: projects, isLoading, error } = useProjects();
  const createProject = useCreateProject();
  const shouldOpenFromQuery = searchParams.get("create") === "1";
  const organizationIdFromQuery = searchParams.get("organizationId");
  const [createOpen, setCreateOpen] = useState(shouldOpenFromQuery);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");

  if (isLoading) {
    return (
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <Skeleton key={i} className="h-32" />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center text-destructive">
        Failed to load projects
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold">Projects</h1>
        <Dialog open={createOpen} onOpenChange={setCreateOpen}>
          <DialogTrigger asChild>
            <Button>New Project</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create project</DialogTitle>
            </DialogHeader>
            <div className="space-y-3">
              <div className="space-y-2">
                <Label htmlFor="new-project-name">Name *</Label>
                <Input
                  id="new-project-name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="My project"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="new-project-description">Description</Label>
                <Textarea
                  id="new-project-description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="What is this project about?"
                  rows={3}
                />
              </div>
            </div>
            <DialogFooter>
              <Button
                onClick={() => {
                  if (!name.trim()) return;
                  createProject.mutate(
                    {
                      name: name.trim(),
                      description,
                      organization_id: organizationIdFromQuery || null,
                    },
                    {
                      onSuccess: (project) => {
                        toast.success("Project created");
                        setCreateOpen(false);
                        setName("");
                        setDescription("");
                        router.push(`/projects/${project.id}/settings`);
                      },
                      onError: () => toast.error("Failed to create project"),
                    },
                  );
                }}
                disabled={!name.trim() || createProject.isPending}
              >
                {createProject.isPending ? "Creating..." : "Create"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {projects && projects.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-muted-foreground mb-4">No projects yet</p>
          <Button onClick={() => setCreateOpen(true)}>Create your first project</Button>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {projects?.map((project) => (
            <ProjectCard key={project.id} project={project} />
          ))}
        </div>
      )}
    </div>
  );
}
