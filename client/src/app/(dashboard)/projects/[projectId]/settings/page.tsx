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
import { Skeleton } from "@/components/ui/skeleton";
import { Textarea } from "@/components/ui/textarea";
import { DocumentRow } from "@/components/documents/document-row";
import { DocumentUpload } from "@/components/documents/document-upload";
import {
  useDeleteDocument,
  useDocuments,
  useReindexDocument,
  useUploadDocument,
} from "@/lib/hooks/use-documents";
import {
  useDeleteProject,
  useProject,
  useReindexProject,
  useUpdateProject,
} from "@/lib/hooks/use-projects";
import { useModelCatalog } from "@/lib/hooks/use-model-catalog";
import { useModelCredentials } from "@/lib/hooks/use-model-credentials";
import type {
  ChunkingStrategy,
  ModelProvider,
  ProjectEmbeddingBackend,
  ProjectLLMBackend,
  UpdateProjectRequest,
} from "@/lib/types/api";

const MAX_SYSTEM_PROMPT_LENGTH = 8000;
const SETTINGS_TABS = [
  "General",
  "Knowledge",
  "Pipeline",
  "Danger zone",
] as const;
type SettingsTab = (typeof SETTINGS_TABS)[number];

const EMBEDDING_MODEL_OPTIONS: Record<ProjectEmbeddingBackend, string[]> = {
  openai: ["text-embedding-3-large", "text-embedding-3-small", "text-embedding-ada-002"],
  gemini: ["text-embedding-004", "gemini-embedding-001", "text-multilingual-embedding-002"],
  ollama: ["nomic-embed-text", "mxbai-embed-large", "all-minilm"],
  inmemory: ["inmemory-embed-accurate", "inmemory-embed-balanced", "inmemory-embed-fast"],
};

const LLM_MODEL_OPTIONS: Record<ProjectLLMBackend, string[]> = {
  openai: ["gpt-4.1", "gpt-4.1-mini", "gpt-4o-mini"],
  gemini: ["gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-1.5-pro"],
  anthropic: [
    "claude-3-7-sonnet-latest",
    "claude-3-5-sonnet-latest",
    "claude-3-5-haiku-latest",
  ],
  ollama: ["llama3.1:8b", "mistral:7b", "qwen2.5:7b"],
  inmemory: ["inmemory-chat-accurate", "inmemory-chat-balanced", "inmemory-chat-fast"],
};

export default function ProjectSettingsPage() {
  const params = useParams<{ projectId: string }>();
  const router = useRouter();
  const { data: project, isLoading } = useProject(params.projectId);
  const { data: documents, isLoading: isDocumentsLoading } = useDocuments(params.projectId);
  const { data: modelCatalog } = useModelCatalog();
  const updateProject = useUpdateProject(params.projectId);
  const { data: credentials } = useModelCredentials();
  const reindexProject = useReindexProject(params.projectId);
  const uploadDocument = useUploadDocument(params.projectId);
  const reindexDocument = useReindexDocument(params.projectId);
  const deleteDocument = useDeleteDocument(params.projectId);
  const deleteProject = useDeleteProject();
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [reindexWarningOpen, setReindexWarningOpen] = useState(false);
  const [pendingData, setPendingData] = useState<UpdateProjectRequest | null>(null);
  const [activeTab, setActiveTab] = useState<SettingsTab>("General");
  const [name, setName] = useState<string | null>(null);
  const [description, setDescription] = useState<string | null>(null);
  const [systemPrompt, setSystemPrompt] = useState<string | null>(null);
  const [chunkingStrategy, setChunkingStrategy] = useState<ChunkingStrategy | null>(null);
  const [parentChildChunking, setParentChildChunking] = useState<boolean | null>(null);
  const [embeddingBackend, setEmbeddingBackend] = useState<
    ProjectEmbeddingBackend | "" | undefined
  >(undefined);
  const [embeddingModel, setEmbeddingModel] = useState<string | null>(null);
  const [embeddingCredentialId, setEmbeddingCredentialId] = useState<string | null>(null);
  const [llmBackend, setLlmBackend] = useState<ProjectLLMBackend | "" | undefined>(undefined);
  const [llmModel, setLlmModel] = useState<string | null>(null);
  const [llmCredentialId, setLlmCredentialId] = useState<string | null>(null);

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
  const effectiveEmbeddingBackend =
    embeddingBackend === undefined ? (project.embedding_backend ?? "") : embeddingBackend;
  const effectiveLlmBackend = llmBackend === undefined ? (project.llm_backend ?? "") : llmBackend;
  const effectiveEmbeddingModel =
    effectiveEmbeddingBackend === "" ? "" : (embeddingModel ?? (project.embedding_model ?? ""));
  const effectiveLlmModel = effectiveLlmBackend === "" ? "" : (llmModel ?? (project.llm_model ?? ""));
  const effectiveEmbeddingCredentialId =
    effectiveEmbeddingBackend === ""
      ? ""
      : (embeddingCredentialId ?? (project.embedding_api_key_credential_id ?? ""));
  const effectiveLlmCredentialId =
    effectiveLlmBackend === "" ? "" : (llmCredentialId ?? (project.llm_api_key_credential_id ?? ""));
  const isProjectReindexing = project.reindex_status === "in_progress";
  const indexedCount = documents?.filter((doc) => doc.status === "indexed").length ?? 0;
  const totalCount = documents?.length ?? 0;
  const hasChanges =
    effectiveName !== project.name ||
    effectiveDescription !== (project.description ?? "") ||
    effectiveSystemPrompt !== (project.system_prompt ?? "") ||
    effectiveChunkingStrategy !== project.chunking_strategy ||
    effectiveParentChildChunking !== project.parent_child_chunking ||
    effectiveEmbeddingBackend !== (project.embedding_backend ?? "") ||
    effectiveEmbeddingModel !== (project.embedding_model ?? "") ||
    effectiveLlmBackend !== (project.llm_backend ?? "") ||
    effectiveLlmModel !== (project.llm_model ?? "") ||
    effectiveEmbeddingCredentialId !== "" ||
    effectiveLlmCredentialId !== "";
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
    embedding_backend: effectiveEmbeddingBackend || null,
    embedding_model: effectiveEmbeddingModel || null,
    embedding_api_key: null,
    embedding_api_key_credential_id: effectiveEmbeddingCredentialId || null,
    llm_backend: effectiveLlmBackend || null,
    llm_model: effectiveLlmModel || null,
    llm_api_key: null,
    llm_api_key_credential_id: effectiveLlmCredentialId || null,
  };

  const credentialsByProvider = (credentials ?? []).reduce<
    Record<ModelProvider, Array<{ id: string; masked_key: string }>>
  >(
    (acc, credential) => {
      acc[credential.provider].push({ id: credential.id, masked_key: credential.masked_key });
      return acc;
    },
    { openai: [], gemini: [], anthropic: [] },
  );

  const embeddingProviderForHints =
    effectiveEmbeddingBackend === "openai" || effectiveEmbeddingBackend === "gemini"
      ? effectiveEmbeddingBackend
      : null;
  const llmProviderForHints =
    effectiveLlmBackend === "openai" ||
    effectiveLlmBackend === "gemini" ||
    effectiveLlmBackend === "anthropic"
      ? effectiveLlmBackend
      : null;
  const embeddingCredentialOptions = embeddingProviderForHints
    ? credentialsByProvider[embeddingProviderForHints]
    : [];
  const llmCredentialOptions = llmProviderForHints ? credentialsByProvider[llmProviderForHints] : [];
  const embeddingModelOptions = effectiveEmbeddingBackend
    ? modelCatalog?.embedding[effectiveEmbeddingBackend as ProjectEmbeddingBackend] ??
      EMBEDDING_MODEL_OPTIONS[effectiveEmbeddingBackend as ProjectEmbeddingBackend] ??
      []
    : [];
  const llmModelOptions = effectiveLlmBackend
    ? modelCatalog?.llm[effectiveLlmBackend as ProjectLLMBackend] ??
      LLM_MODEL_OPTIONS[effectiveLlmBackend as ProjectLLMBackend] ??
      []
    : [];

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
      <div className="flex flex-wrap gap-2">
        {SETTINGS_TABS.map((tab) => (
          <Button
            key={tab}
            type="button"
            variant={activeTab === tab ? "default" : "outline"}
            className="cursor-pointer"
            onClick={() => setActiveTab(tab)}
          >
            {tab}
          </Button>
        ))}
      </div>

      {isProjectReindexing && (
        <div className="rounded-md border border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-900">
          Reindexation en cours ({project.reindex_progress}/{project.reindex_total}).
          Les actions d&apos;upload, chat et reindex sont temporairement bloquees.
        </div>
      )}

      {activeTab === "General" && (
        <div className="space-y-4">
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
            rows={16}
            maxLength={MAX_SYSTEM_PROMPT_LENGTH}
          />
          <p className="text-muted-foreground text-xs">
            Limite: 8000 caracteres. Au-dela, la sauvegarde du projet sera refusee.
          </p>
        </div>
      </div>
      )}

      {activeTab === "Knowledge" && (
        <div className="space-y-4">
        <p className="text-muted-foreground text-sm">
          La base documentaire du projet est configuree via les options d&apos;indexation.
        </p>
        <p className="text-sm text-muted-foreground">
          {indexedCount} indexed / {totalCount} total
        </p>
        <DocumentUpload
          onUpload={(files) => {
            uploadDocument.mutate(files, {
              onSuccess: (result) =>
                toast.success(`${result.succeeded} uploaded, ${result.failed} failed`),
              onError: () => toast.error("Failed to upload document"),
            });
          }}
          isUploading={uploadDocument.isPending}
          disabled={isProjectReindexing}
        />
        {isDocumentsLoading ? (
          <div className="space-y-3">
            {Array.from({ length: 2 }).map((_, i) => (
              <Skeleton key={i} className="h-16" />
            ))}
          </div>
        ) : documents && documents.length > 0 ? (
          <div className="space-y-3">
            {documents.map((doc) => (
              <DocumentRow
                key={doc.id}
                document={doc}
                onReindex={(id) => {
                  if (isProjectReindexing) return;
                  reindexDocument.mutate(id, {
                    onSuccess: () => toast.success("Document reindexed"),
                    onError: () => toast.error("Failed to reindex document"),
                  });
                }}
                reindexingId={reindexDocument.isPending ? (reindexDocument.variables ?? null) : null}
                disableReindex={isProjectReindexing}
                onDelete={(id) => {
                  deleteDocument.mutate(id, {
                    onSuccess: () => toast.success("Document deleted"),
                    onError: () => toast.error("Failed to delete document"),
                  });
                }}
                isDeleting={deleteDocument.isPending}
              />
            ))}
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">
            No documents yet. Upload your first document in this section.
          </p>
        )}
      </div>
      )}

      {activeTab === "Pipeline" && (
        <div className="space-y-4">
        <div className="space-y-2">
          <p className="text-base font-semibold tracking-tight">Knowledge ingestion</p>
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

        <hr className="border-border" />

        <div className="space-y-2">
          <p className="text-base font-semibold tracking-tight">Chunks retrieval</p>
          <div className="space-y-2">
            <Label htmlFor="embeddingBackend">Embedding backend</Label>
            <select
              id="embeddingBackend"
              value={effectiveEmbeddingBackend}
              onChange={(e) => {
                setEmbeddingBackend((e.target.value || "") as ProjectEmbeddingBackend | "");
                setEmbeddingModel("");
                setEmbeddingCredentialId("");
              }}
              className="border-input bg-background w-full rounded-md border px-3 py-2 text-sm"
            >
              <option value="">Default</option>
              <option value="openai">OpenAI</option>
              <option value="gemini">Gemini</option>
              <option value="ollama">Ollama</option>
              <option value="inmemory">InMemory</option>
            </select>
          </div>
          {effectiveEmbeddingBackend ? (
            <>
              <div className="space-y-2">
                <Label htmlFor="embeddingModel">Embedding model</Label>
                <select
                  id="embeddingModel"
                  value={effectiveEmbeddingModel}
                  onChange={(e) => setEmbeddingModel(e.target.value)}
                  className="border-input bg-background w-full rounded-md border px-3 py-2 text-sm"
                >
                  <option value="">Select a model</option>
                  {embeddingModelOptions.map((model) => (
                    <option key={model} value={model}>
                      {model}
                    </option>
                  ))}
                </select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="embeddingCredentialId">Embedding API key</Label>
                {project.embedding_api_key_masked ? (
                  <p className="text-xs text-muted-foreground">
                    Existing key: {project.embedding_api_key_masked}
                  </p>
                ) : null}
                <select
                  id="embeddingCredentialId"
                  value={effectiveEmbeddingCredentialId}
                  onChange={(e) => {
                    setEmbeddingCredentialId(e.target.value);
                  }}
                  disabled={!embeddingProviderForHints}
                  className="border-input bg-background w-full rounded-md border px-3 py-2 text-sm disabled:opacity-60"
                >
                  <option value="">
                    {embeddingProviderForHints
                      ? "No selection"
                      : "Select OpenAI or Gemini backend first"}
                  </option>
                  {embeddingCredentialOptions.map((item) => (
                    <option key={item.id} value={item.id}>
                      {item.masked_key}
                    </option>
                  ))}
                </select>
                {embeddingProviderForHints ? (
                  <p className="text-xs text-muted-foreground">
                    Your saved keys for {embeddingProviderForHints}:{" "}
                    {embeddingCredentialOptions.length > 0
                      ? embeddingCredentialOptions.map((item) => item.masked_key).join(", ")
                      : "none"}
                  </p>
                ) : (
                  <p className="text-xs text-muted-foreground">
                    Credentials are available only for OpenAI/Gemini user keys.
                  </p>
                )}
              </div>
            </>
          ) : null}
        </div>

        <hr className="border-border" />

        <div className="space-y-2">
          <p className="text-base font-semibold tracking-tight">Answer generation</p>
          <div className="space-y-2">
            <Label htmlFor="llmBackend">LLM backend</Label>
            <select
              id="llmBackend"
              value={effectiveLlmBackend}
              onChange={(e) => {
                setLlmBackend((e.target.value || "") as ProjectLLMBackend | "");
                setLlmModel("");
                setLlmCredentialId("");
              }}
              className="border-input bg-background w-full rounded-md border px-3 py-2 text-sm"
            >
              <option value="">Default</option>
              <option value="openai">OpenAI</option>
              <option value="gemini">Gemini</option>
              <option value="anthropic">Anthropic</option>
              <option value="ollama">Ollama</option>
              <option value="inmemory">InMemory</option>
            </select>
          </div>
          {effectiveLlmBackend ? (
            <>
              <div className="space-y-2">
                <Label htmlFor="llmModel">LLM model</Label>
                <select
                  id="llmModel"
                  value={effectiveLlmModel}
                  onChange={(e) => setLlmModel(e.target.value)}
                  className="border-input bg-background w-full rounded-md border px-3 py-2 text-sm"
                >
                  <option value="">Select a model</option>
                  {llmModelOptions.map((model) => (
                    <option key={model} value={model}>
                      {model}
                    </option>
                  ))}
                </select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="llmCredentialId">LLM API key</Label>
                {project.llm_api_key_masked ? (
                  <p className="text-xs text-muted-foreground">
                    Existing key: {project.llm_api_key_masked}
                  </p>
                ) : null}
                <select
                  id="llmCredentialId"
                  value={effectiveLlmCredentialId}
                  onChange={(e) => {
                    setLlmCredentialId(e.target.value);
                  }}
                  disabled={!llmProviderForHints}
                  className="border-input bg-background w-full rounded-md border px-3 py-2 text-sm disabled:opacity-60"
                >
                  <option value="">
                    {llmProviderForHints
                      ? "No selection"
                      : "Select OpenAI, Gemini or Anthropic backend first"}
                  </option>
                  {llmCredentialOptions.map((item) => (
                    <option key={item.id} value={item.id}>
                      {item.masked_key}
                    </option>
                  ))}
                </select>
                {llmProviderForHints ? (
                  <p className="text-xs text-muted-foreground">
                    Your saved keys for {llmProviderForHints}:{" "}
                    {llmCredentialOptions.length > 0
                      ? llmCredentialOptions.map((item) => item.masked_key).join(", ")
                      : "none"}
                  </p>
                ) : (
                  <p className="text-xs text-muted-foreground">
                    Credentials are available only for OpenAI/Gemini/Anthropic user keys.
                  </p>
                )}
              </div>
            </>
          ) : null}
        </div>
      </div>
      )}

      {activeTab !== "Knowledge" && activeTab !== "Danger zone" ? (
        <Button className="cursor-pointer" disabled={isDisabled} onClick={handleSave}>
          {updateProject.isPending ? "Saving..." : "Save changes"}
        </Button>
      ) : null}

      {activeTab === "Pipeline" ? (
        <>
          <hr className="border-border" />
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
        </>
      ) : null}

      {activeTab === "Danger zone" && (
        <div className="space-y-4">
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
      )}

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
