"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import type {
  ChunkingStrategy,
  CreateProjectRequest,
  ProjectResponse,
  UpdateProjectRequest,
} from "@/lib/types/api";

type ProjectFormData = CreateProjectRequest | UpdateProjectRequest;

interface ProjectFormProps {
  initialData?: ProjectResponse;
  onSubmit: (data: ProjectFormData) => void;
  isLoading?: boolean;
  submitLabel?: string;
}

export function ProjectForm({
  initialData,
  onSubmit,
  isLoading = false,
  submitLabel = "Create Project",
}: ProjectFormProps) {
  const [name, setName] = useState(initialData?.name ?? "");
  const [description, setDescription] = useState(initialData?.description ?? "");
  const [systemPrompt, setSystemPrompt] = useState(initialData?.system_prompt ?? "");
  const [chunkingStrategy, setChunkingStrategy] = useState<ChunkingStrategy>(
    initialData?.chunking_strategy ?? "auto"
  );
  const [parentChildChunking, setParentChildChunking] = useState<boolean>(
    initialData?.parent_child_chunking ?? false
  );
  const [reindexWarningOpen, setReindexWarningOpen] = useState(false);
  const [pendingFormData, setPendingFormData] = useState<ProjectFormData | null>(null);

  const isDisabled = !name.trim() || isLoading;

  const parentChildChanged =
    initialData !== undefined &&
    parentChildChunking !== initialData.parent_child_chunking;
  const isSemanticRecommended =
    parentChildChunking && chunkingStrategy !== "semantic";

  function buildFormData(): ProjectFormData {
    return {
      name: name.trim(),
      description,
      system_prompt: systemPrompt,
      chunking_strategy: chunkingStrategy,
      parent_child_chunking: parentChildChunking,
    };
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const data = buildFormData();

    if (parentChildChanged) {
      setPendingFormData(data);
      setReindexWarningOpen(true);
    } else {
      onSubmit(data);
    }
  }

  function handleConfirmReindex() {
    setReindexWarningOpen(false);
    if (pendingFormData) {
      onSubmit(pendingFormData);
      setPendingFormData(null);
    }
  }

  function handleCancelReindex() {
    setReindexWarningOpen(false);
    setPendingFormData(null);
  }

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle>
            {initialData ? "Edit Project" : "New Project"}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">Name *</Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="My project"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="What is this project about?"
                rows={3}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="systemPrompt">System Prompt</Label>
              <Textarea
                id="systemPrompt"
                value={systemPrompt}
                onChange={(e) => setSystemPrompt(e.target.value)}
                placeholder="Instructions for the AI assistant..."
                rows={5}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="chunkingStrategy">Chunking Strategy</Label>
              <select
                id="chunkingStrategy"
                value={chunkingStrategy}
                onChange={(e) => setChunkingStrategy(e.target.value as ChunkingStrategy)}
                className="border-input bg-background w-full rounded-md border px-3 py-2 text-sm"
              >
                <option value="auto">Auto</option>
                <option value="fixed_window">Fixed window</option>
                <option value="paragraph">Paragraph</option>
                <option value="heading_section">Heading section</option>
                <option value="semantic">Semantic</option>
              </select>
              <p className="text-muted-foreground text-sm">
                Le chunking definit comment un document est decoupe avant indexation. `Auto` choisit
                automatiquement selon la structure du texte, `Fixed window` coupe par taille fixe,
                `Paragraph` suit les paragraphes, `Heading section` suit les sections/titres, et
                `Semantic` essaie de couper sur des ruptures de sens pour produire des chunks plus
                coherents.
              </p>
            </div>
            <div className="flex items-center gap-2">
              <input
                id="parentChildChunking"
                type="checkbox"
                checked={parentChildChunking}
                onChange={(e) => setParentChildChunking(e.target.checked)}
                className="h-4 w-4"
              />
              <Label htmlFor="parentChildChunking">Enable parent-child chunking</Label>
            </div>
            <p className="text-muted-foreground text-sm">
              Le mode parent-child construit de gros chunks parents (contexte riche) et des chunks
              enfants (plus fins pour la recherche). Cela peut ameliorer la pertinence du retrieval
              sur des documents longs, au prix d&apos;une indexation plus lourde.
            </p>
            <p className="text-muted-foreground text-sm">
              Recommandation: le mode parent-child fonctionne generalement mieux avec la strategie
              de chunking `Semantic`.
            </p>
            {isSemanticRecommended ? (
              <p className="text-sm text-amber-700">
                Le mode parent-child est actif avec une strategie non `Semantic`. Cela fonctionne,
                mais la pertinence est souvent meilleure avec `Semantic`.
              </p>
            ) : null}
            <Button type="submit" className="cursor-pointer" disabled={isDisabled}>
              {isLoading ? "Saving..." : submitLabel}
            </Button>
          </form>
        </CardContent>
      </Card>

      <Dialog open={reindexWarningOpen} onOpenChange={setReindexWarningOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Reindexation requise</DialogTitle>
            <DialogDescription>
              {parentChildChunking
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
              onClick={handleCancelReindex}
            >
              Annuler
            </Button>
            <Button
              className="cursor-pointer"
              onClick={handleConfirmReindex}
            >
              Confirmer et sauvegarder
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
