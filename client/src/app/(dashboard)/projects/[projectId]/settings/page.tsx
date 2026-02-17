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
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { Textarea } from "@/components/ui/textarea";
import {
  useDeleteProject,
  useProject,
  useReindexProject,
  useUpdateProject,
} from "@/lib/hooks/use-projects";
import type { ChunkingStrategy, UpdateProjectRequest } from "@/lib/types/api";

const MAX_SYSTEM_PROMPT_LENGTH = 8000;

export default function ProjectSettingsPage() {
  const params = useParams<{ projectId: string }>();
  const router = useRouter();
  const { data: project, isLoading } = useProject(params.projectId);
  const updateProject = useUpdateProject(params.projectId);
  const reindexProject = useReindexProject(params.projectId);
  const deleteProject = useDeleteProject();
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [reindexWarningOpen, setReindexWarningOpen] = useState(false);
  const [pendingData, setPendingData] = useState<UpdateProjectRequest | null>(null);
  const [name, setName] = useState<string | null>(null);
  const [description, setDescription] = useState<string | null>(null);
  const [systemPrompt, setSystemPrompt] = useState<string | null>(null);
  const [chunkingStrategy, setChunkingStrategy] = useState<ChunkingStrategy | null>(null);
  const [parentChildChunking, setParentChildChunking] = useState<boolean | null>(null);

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

  const effectiveName = name ?? project.name;
  const effectiveDescription = description ?? (project.description ?? "");
  const effectiveSystemPrompt = systemPrompt ?? (project.system_prompt ?? "");
  const effectiveChunkingStrategy = chunkingStrategy ?? project.chunking_strategy;
  const effectiveParentChildChunking = parentChildChunking ?? project.parent_child_chunking;
  const isProjectReindexing = project.reindex_status === "in_progress";
  const hasChanges =
    effectiveName !== project.name ||
    effectiveDescription !== (project.description ?? "") ||
    effectiveSystemPrompt !== (project.system_prompt ?? "") ||
    effectiveChunkingStrategy !== project.chunking_strategy ||
    effectiveParentChildChunking !== project.parent_child_chunking;
  const isDisabled = !effectiveName.trim() || updateProject.isPending || !hasChanges;
  const systemPromptLength = effectiveSystemPrompt.length;
  const nearSystemPromptLimit = systemPromptLength >= 7000;
  const isSemanticRecommended =
    effectiveParentChildChunking && effectiveChunkingStrategy !== "semantic";

  const payload: UpdateProjectRequest = {
    name: effectiveName.trim(),
    description: effectiveDescription,
    system_prompt: effectiveSystemPrompt,
    chunking_strategy: effectiveChunkingStrategy,
    parent_child_chunking: effectiveParentChildChunking,
  };

  function handleSave() {
    const parentChildChanged =
      effectiveParentChildChunking !== project.parent_child_chunking;
    if (parentChildChanged) {
      setPendingData(payload);
      setReindexWarningOpen(true);
      return;
    }
    updateProject.mutate(payload, {
      onSuccess: () => toast.success("Project updated"),
      onError: () => toast.error("Failed to update project"),
    });
  }

  return (
    <div className="mx-auto max-w-2xl space-y-8">
      {isProjectReindexing && (
        <div className="rounded-md border border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-900">
          Reindexation en cours ({project.reindex_progress}/{project.reindex_total}).
          Les actions d&apos;upload, chat et reindex sont temporairement bloquees.
        </div>
      )}
      <div className="space-y-4">
        <h2 className="text-lg font-semibold">Presentation</h2>
        <div className="space-y-2">
          <Label htmlFor="name">Name *</Label>
          <Input
            id="name"
            value={effectiveName}
            onChange={(e) => setName(e.target.value)}
            placeholder="My project"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="description">Description</Label>
          <Textarea
            id="description"
            value={effectiveDescription}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="What is this project about?"
            rows={3}
          />
        </div>
      </div>

      <Separator />

      <div className="space-y-4">
        <h2 className="text-lg font-semibold">Prompt</h2>
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label htmlFor="systemPrompt">System Prompt</Label>
            <span className={`text-xs ${nearSystemPromptLimit ? "text-amber-700" : "text-muted-foreground"}`}>
              {systemPromptLength}/{MAX_SYSTEM_PROMPT_LENGTH}
            </span>
          </div>
          <Textarea
            id="systemPrompt"
            value={effectiveSystemPrompt}
            onChange={(e) => setSystemPrompt(e.target.value)}
            placeholder="Instructions for the AI assistant..."
            rows={10}
            maxLength={MAX_SYSTEM_PROMPT_LENGTH}
          />
          <p className="text-muted-foreground text-xs">
            Limite: 8000 caracteres. Au-dela, la sauvegarde du projet sera refusee.
          </p>
        </div>
      </div>

      <Separator />

      <div className="space-y-4">
        <h2 className="text-lg font-semibold">Knowledge</h2>
        <p className="text-muted-foreground text-sm">
          La base documentaire du projet est configuree via les options d&apos;indexation.
        </p>
      </div>

      <Separator />

      <div className="space-y-4">
        <h2 className="text-lg font-semibold">Indexing</h2>
        <div className="space-y-2">
          <Label htmlFor="chunkingStrategy">Chunking strategy</Label>
          <select
            id="chunkingStrategy"
            value={effectiveChunkingStrategy}
            onChange={(e) => setChunkingStrategy(e.target.value as ChunkingStrategy)}
            className="border-input bg-background w-full rounded-md border px-3 py-2 text-sm"
          >
            <option value="auto">Auto</option>
            <option value="fixed_window">Fixed window</option>
            <option value="paragraph">Paragraph</option>
            <option value="heading_section">Heading section</option>
            <option value="semantic">Semantic</option>
          </select>
        </div>
        <div className="flex items-center gap-2">
          <input
            id="parentChildChunking"
            type="checkbox"
            checked={effectiveParentChildChunking}
            onChange={(e) => setParentChildChunking(e.target.checked)}
            className="h-4 w-4"
          />
          <Label htmlFor="parentChildChunking">Enable parent-child chunking</Label>
        </div>
        <p className="text-muted-foreground text-sm">
          Recommandation: le mode parent-child fonctionne generalement mieux avec la strategie
          `Semantic`.
        </p>
        {isSemanticRecommended ? (
          <p className="text-sm text-amber-700">
            Le mode parent-child est actif avec une strategie non `Semantic`. Cela fonctionne,
            mais la pertinence est souvent meilleure avec `Semantic`.
          </p>
        ) : null}
      </div>

      <Separator />

      <div className="space-y-2">
        <h2 className="text-lg font-semibold">Retrieval</h2>
        <p className="text-muted-foreground text-sm">
          Les reglages de retrieval seront centralises ici dans une prochaine iteration.
        </p>
      </div>

      <Separator />

      <div className="space-y-2">
        <h2 className="text-lg font-semibold">Answer</h2>
        <p className="text-muted-foreground text-sm">
          Les reglages de generation de reponse seront centralises ici dans une prochaine
          iteration.
        </p>
      </div>

      <Button className="cursor-pointer" disabled={isDisabled} onClick={handleSave}>
        {updateProject.isPending ? "Saving..." : "Save changes"}
      </Button>

      <div className="space-y-2">
        <h2 className="text-lg font-semibold">Reindexation</h2>
        <Button
          className="cursor-pointer"
          disabled={reindexProject.isPending || isProjectReindexing}
          onClick={() => {
            reindexProject.mutate(undefined, {
              onSuccess: (result) =>
                toast.success(
                  `Reindexation terminee: ${result.indexed_documents}/${result.total_documents} indexes, ${result.failed_documents} en erreur`,
                ),
              onError: () => toast.error("Failed to reindex project"),
            });
          }}
        >
          {reindexProject.isPending ? "Reindexing..." : "Reindex all documents"}
        </Button>
      </div>

      <Separator />

      <div className="space-y-4">
        <h2 className="text-lg font-semibold text-destructive">Danger zone</h2>
        <Dialog open={deleteOpen} onOpenChange={setDeleteOpen}>
          <DialogTrigger asChild>
            <Button variant="destructive" className="cursor-pointer">Delete Project</Button>
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
                className="cursor-pointer"
                onClick={() => setDeleteOpen(false)}
              >
                Cancel
              </Button>
              <Button
                variant="destructive"
                className="cursor-pointer"
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

      <Dialog open={reindexWarningOpen} onOpenChange={setReindexWarningOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Reindexation requise</DialogTitle>
            <DialogDescription>
              {effectiveParentChildChunking
                ? "Activer le mode parent-child necessite de reindexer tous les documents du projet pour creer la hierarchie parent/enfant."
                : "Desactiver le mode parent-child necessite de reindexer tous les documents du projet pour revenir au chunking standard."}
              {" "}Les documents existants ne seront pas utilisables correctement tant qu&apos;ils
              n&apos;auront pas ete reindexes.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              className="cursor-pointer"
              onClick={() => {
                setReindexWarningOpen(false);
                setPendingData(null);
              }}
            >
              Cancel
            </Button>
            <Button
              className="cursor-pointer"
              onClick={() => {
                if (!pendingData) return;
                updateProject.mutate(pendingData, {
                  onSuccess: () => toast.success("Project updated"),
                  onError: () => toast.error("Failed to update project"),
                });
                setReindexWarningOpen(false);
                setPendingData(null);
              }}
            >
              Confirm and save
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
