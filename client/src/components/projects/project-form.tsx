"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
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

  const isDisabled = !name.trim() || isLoading;

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    onSubmit({
      name: name.trim(),
      description,
      system_prompt: systemPrompt,
      chunking_strategy: chunkingStrategy,
      parent_child_chunking: parentChildChunking,
    });
  }

  return (
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
            sur des documents longs, au prix d'une indexation plus lourde.
          </p>
          <Button type="submit" className="cursor-pointer" disabled={isDisabled}>
            {isLoading ? "Saving..." : submitLabel}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
