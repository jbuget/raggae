"use client";

import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { ProjectForm } from "@/components/projects/project-form";
import { useCreateProject } from "@/lib/hooks/use-projects";

export default function NewProjectPage() {
  const router = useRouter();
  const createProject = useCreateProject();

  return (
    <div className="mx-auto max-w-2xl">
      <ProjectForm
        onSubmit={(data) => {
          createProject.mutate(data, {
            onSuccess: (project) => {
              toast.success("Project created");
              router.push(`/projects/${project.id}`);
            },
            onError: () => {
              toast.error("Failed to create project");
            },
          });
        }}
        isLoading={createProject.isPending}
      />
    </div>
  );
}
