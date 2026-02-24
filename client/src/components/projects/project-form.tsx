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
import { Separator } from "@/components/ui/separator";
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

const MAX_SYSTEM_PROMPT_LENGTH = 8000;

export function ProjectForm({
  initialData,
  onSubmit,
  isLoading = false,
  submitLabel = "Create Project",
}: ProjectFormProps) {
  const isCreateMode = initialData === undefined;
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
  const systemPromptLength = systemPrompt.length;
  const nearSystemPromptLimit = systemPromptLength >= 7000;

  function buildFormData(): ProjectFormData {
    if (isCreateMode) {
      return {
        name: name.trim(),
        description,
      };
    }
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

    if (!isCreateMode && parentChildChanged) {
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
            <div className="space-y-4">
              <h3 className="text-base font-semibold">Presentation</h3>
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
            </div>

            {isCreateMode ? null : (
              <>
                <Separator />

                <div className="space-y-4">
                  <h3 className="text-base font-semibold">Prompt</h3>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <Label htmlFor="systemPrompt">System Prompt</Label>
                      <span
                        className={`text-xs ${
                          nearSystemPromptLimit ? "text-amber-700" : "text-muted-foreground"
                        }`}
                      >
                        {systemPromptLength}/{MAX_SYSTEM_PROMPT_LENGTH}
                      </span>
                    </div>
                    <Textarea
                      id="systemPrompt"
                      value={systemPrompt}
                      onChange={(e) => setSystemPrompt(e.target.value)}
                      placeholder="Instructions for the AI assistant..."
                      rows={5}
                      maxLength={MAX_SYSTEM_PROMPT_LENGTH}
                    />
                    <p className="text-muted-foreground text-xs">
                      Limite: 8000 caracteres. Au-dela, la sauvegarde du projet sera refusee.
                    </p>
                    {nearSystemPromptLimit ? (
                      <p className="text-xs text-amber-700">
                        Tu approches de la limite. Pense a raccourcir si possible.
                      </p>
                    ) : null}
                  </div>
                </div>
                <Separator />

                <div className="space-y-4">
                  <h3 className="text-base font-semibold">Knowledge</h3>
                  <p className="text-muted-foreground text-sm">
                    Les reglages ci-dessous controlent comment les documents sont prepares avant
                    indexation.
                  </p>
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
                      Le chunking definit comment un document est decoupe avant indexation. `Auto`
                      choisit automatiquement selon la structure du texte.
                    </p>
                  </div>
                </div>

                <Separator />

                <div className="space-y-4">
                  <h3 className="text-base font-semibold">Indexing</h3>
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
                    Le mode parent-child construit de gros chunks parents (contexte riche) et des
                    chunks enfants (plus fins pour la recherche). Cela peut ameliorer la pertinence du
                    retrieval sur des documents longs, au prix d&apos;une indexation plus lourde.
                  </p>
                  <p className="text-muted-foreground text-sm">
                    Recommandation: le mode parent-child fonctionne generalement mieux avec la strategie
                    de chunking `Semantic`.
                  </p>
                  {isSemanticRecommended ? (
                    <p className="text-sm text-amber-700">
                      Le mode parent-child est actif avec une strategie non `Semantic`. Cela
                      fonctionne, mais la pertinence est souvent meilleure avec `Semantic`.
                    </p>
                  ) : null}
                </div>

                <Separator />

                <div className="space-y-2">
                  <h3 className="text-base font-semibold">Retrieval</h3>
                  <p className="text-muted-foreground text-sm">
                    Les reglages de retrieval seront centralises ici dans une prochaine iteration.
                  </p>
                </div>

                <Separator />

                <div className="space-y-2">
                  <h3 className="text-base font-semibold">Answer</h3>
                  <p className="text-muted-foreground text-sm">
                    Les reglages de generation de reponse seront centralises ici dans une prochaine
                    iteration.
                  </p>
                </div>
              </>
            )}

            <Button type="submit" className="cursor-pointer" disabled={isDisabled}>
              {isLoading ? "Saving..." : submitLabel}
            </Button>
          </form>
        </CardContent>
      </Card>

      <Dialog open={!isCreateMode && reindexWarningOpen} onOpenChange={setReindexWarningOpen}>
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
