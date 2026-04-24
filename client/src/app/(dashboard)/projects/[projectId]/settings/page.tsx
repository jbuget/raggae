"use client";

import { useParams, useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";
import { useTranslations } from "next-intl";
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
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";
import { DocumentRow } from "@/components/documents/document-row";
import { DocumentUpload } from "@/components/documents/document-upload";
import { ProjectSnapshotsList } from "@/components/projects/project-snapshots-list";
import {
  useDeleteDocument,
  useDocuments,
  useReindexDocument,
  useUploadDocument,
} from "@/lib/hooks/use-documents";
import {
  useDeleteProject,
  useProject,
  usePublishProject,
  useReindexProject,
  useUnpublishProject,
  useUpdateProject,
} from "@/lib/hooks/use-projects";
import { useModelCatalog } from "@/lib/hooks/use-model-catalog";
import { useModelCredentials } from "@/lib/hooks/use-model-credentials";
import { useOrgModelCredentials } from "@/lib/hooks/use-org-model-credentials";
import type {
  ChunkingStrategy,
  ModelProvider,
  ProjectEmbeddingBackend,
  ProjectLLMBackend,
  ProjectRerankerBackend,
  RetrievalStrategy,
  UpdateProjectRequest,
} from "@/lib/types/api";

const MAX_SYSTEM_PROMPT_LENGTH = 8000;
const SETTINGS_TABS = [
  "General",
  "Publication",
  "Models",
  "Knowledge indexing",
  "Document ingestion",
  "Context retrieval",
  "Context augmentation",
  "Answer generation",
  "History",
] as const;
type SettingsTab = (typeof SETTINGS_TABS)[number];

export default function ProjectSettingsPage() {
  const params = useParams<{ projectId: string }>();
  const router = useRouter();
  const searchParams = useSearchParams();
  const { data: project, isLoading } = useProject(params.projectId);
  const { data: documents, isLoading: isDocumentsLoading } = useDocuments(params.projectId);
  const { data: modelCatalog } = useModelCatalog();
  const updateProject = useUpdateProject(params.projectId);
  const { data: userCredentials } = useModelCredentials();
  const { data: orgCredentials } = useOrgModelCredentials(project?.organization_id);
  const credentials = project?.organization_id ? orgCredentials : userCredentials;
  const reindexProject = useReindexProject(params.projectId);
  const publishProject = usePublishProject(params.projectId);
  const unpublishProject = useUnpublishProject(params.projectId);
  const uploadDocument = useUploadDocument(params.projectId);
  const reindexDocument = useReindexDocument(params.projectId);
  const deleteDocument = useDeleteDocument(params.projectId);
  const deleteProject = useDeleteProject();
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [publishOpen, setPublishOpen] = useState(false);
  const [unpublishOpen, setUnpublishOpen] = useState(false);
  const [reindexWarningOpen, setReindexWarningOpen] = useState(false);
  const [pendingData, setPendingData] = useState<UpdateProjectRequest | null>(null);
  const tabFromUrl = searchParams.get("tab");
  const [activeTab, setActiveTab] = useState<SettingsTab>(
    SETTINGS_TABS.find((t) => t === tabFromUrl) ?? "General",
  );

  function handleTabChange(tab: SettingsTab) {
    setActiveTab(tab);
    const next = new URLSearchParams(searchParams.toString());
    next.set("tab", tab);
    router.replace(`?${next.toString()}`, { scroll: false });
  }
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
  const [retrievalStrategy, setRetrievalStrategy] = useState<RetrievalStrategy | null>(null);
  const [retrievalTopK, setRetrievalTopK] = useState<number | null>(null);
  const [retrievalMinScore, setRetrievalMinScore] = useState<number | null>(null);
  const [chatHistoryWindowSize, setChatHistoryWindowSize] = useState<number | null>(null);
  const [chatHistoryMaxChars, setChatHistoryMaxChars] = useState<number | null>(null);
  const [rerankingEnabled, setRerankingEnabled] = useState<boolean | null>(null);
  const [rerankerBackend, setRerankerBackend] = useState<ProjectRerankerBackend | null>(null);
  const [rerankerModel, setRerankerModel] = useState<string | null>(null);
  const [rerankerCandidateMultiplier, setRerankerCandidateMultiplier] = useState<number | null>(
    null,
  );

  const t = useTranslations("projects.settings");
  const tCommon = useTranslations("common");
  const tForm = useTranslations("projects.form");

  const tabLabels: Record<SettingsTab, string> = {
    "General": t("tabs.general"),
    "Publication": t("tabs.publication"),
    "Models": t("tabs.models"),
    "Knowledge indexing": t("tabs.knowledgeIndexing"),
    "Document ingestion": t("tabs.documentIngestion"),
    "Context retrieval": t("tabs.contextRetrieval"),
    "Context augmentation": t("tabs.contextAugmentation"),
    "Answer generation": t("tabs.answerGeneration"),
    "History": t("tabs.history"),
  };

  if (isLoading) {
    return (
      <div className="w-full space-y-4">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (!project) {
    return <div className="text-center text-muted-foreground">{t("notFound")}</div>;
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
  const storedEmbeddingCredentialId = project.organization_id
    ? (project.org_embedding_api_key_credential_id ?? "")
    : (project.embedding_api_key_credential_id ?? "");
  const storedLlmCredentialId = project.organization_id
    ? (project.org_llm_api_key_credential_id ?? "")
    : (project.llm_api_key_credential_id ?? "");
  const effectiveEmbeddingCredentialId =
    effectiveEmbeddingBackend === ""
      ? ""
      : (embeddingCredentialId ?? storedEmbeddingCredentialId);
  const effectiveLlmCredentialId =
    effectiveLlmBackend === "" ? "" : (llmCredentialId ?? storedLlmCredentialId);
  const effectiveRetrievalStrategy =
    retrievalStrategy ?? (project.retrieval_strategy ?? "hybrid");
  const effectiveRetrievalTopK = retrievalTopK ?? project.retrieval_top_k ?? 8;
  const effectiveRetrievalMinScore = retrievalMinScore ?? project.retrieval_min_score ?? 0.3;
  const effectiveChatHistoryWindowSize =
    chatHistoryWindowSize ?? project.chat_history_window_size ?? 8;
  const effectiveChatHistoryMaxChars =
    chatHistoryMaxChars ?? project.chat_history_max_chars ?? 4000;
  const effectiveRerankingEnabled = rerankingEnabled ?? project.reranking_enabled ?? false;
  const effectiveRerankerBackend = rerankerBackend ?? project.reranker_backend ?? "none";
  const effectiveRerankerModel = rerankerModel ?? project.reranker_model ?? "";
  const effectiveRerankerCandidateMultiplier =
    rerankerCandidateMultiplier ?? project.reranker_candidate_multiplier ?? 3;
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
    effectiveRetrievalStrategy !== (project.retrieval_strategy ?? "hybrid") ||
    effectiveRetrievalTopK !== (project.retrieval_top_k ?? 8) ||
    effectiveRetrievalMinScore !== (project.retrieval_min_score ?? 0.3) ||
    effectiveChatHistoryWindowSize !== (project.chat_history_window_size ?? 8) ||
    effectiveChatHistoryMaxChars !== (project.chat_history_max_chars ?? 4000) ||
    effectiveRerankingEnabled !== (project.reranking_enabled ?? false) ||
    effectiveRerankerBackend !== (project.reranker_backend ?? "none") ||
    effectiveRerankerModel !== (project.reranker_model ?? "") ||
    effectiveRerankerCandidateMultiplier !==
      (project.reranker_candidate_multiplier ?? 3) ||
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
    retrieval_strategy: effectiveRetrievalStrategy,
    retrieval_top_k: effectiveRetrievalTopK,
    retrieval_min_score: effectiveRetrievalMinScore,
    chat_history_window_size: effectiveChatHistoryWindowSize,
    chat_history_max_chars: effectiveChatHistoryMaxChars,
    reranking_enabled: effectiveRerankingEnabled,
    reranker_backend: effectiveRerankerBackend,
    reranker_model: effectiveRerankerModel || null,
    reranker_candidate_multiplier: effectiveRerankerCandidateMultiplier,
  };

  const credentialsByProvider = (credentials ?? [])
    .filter((c) => c.is_active)
    .reduce<Record<ModelProvider, Array<{ id: string; masked_key: string }>>>(
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
    ? modelCatalog?.embedding[effectiveEmbeddingBackend as ProjectEmbeddingBackend] ?? []
    : [];
  const llmModelOptions = effectiveLlmBackend
    ? modelCatalog?.llm[effectiveLlmBackend as ProjectLLMBackend] ?? []
    : [];
  const rerankerModelOptions =
    modelCatalog?.reranker[effectiveRerankerBackend as ProjectRerankerBackend] ?? [];

  function handleSave() {
    const parentChildChanged =
      effectiveParentChildChunking !== project?.parent_child_chunking;
    if (parentChildChanged) {
      setPendingData(payload);
      setReindexWarningOpen(true);
      return;
    }
    updateProject.mutate(payload, {
      onSuccess: () => toast.success(t("updateSuccess")),
      onError: () => toast.error(t("updateError")),
    });
  }

  return (
    <div className="w-full space-y-8">
      <div>
        <div
          role="tablist"
          aria-label="Project settings sections"
          className="flex flex-wrap items-end gap-4 border-b"
        >
          {SETTINGS_TABS.map((tab) => {
            const isActive = activeTab === tab;
            return (
              <button
                key={tab}
                type="button"
                role="tab"
                aria-selected={isActive}
                className={[
                  "cursor-pointer border-b-2 px-1 py-3 text-sm whitespace-nowrap transition-colors",
                  isActive
                    ? "border-primary text-foreground font-medium"
                    : "border-transparent text-muted-foreground hover:text-foreground",
                ].join(" ")}
                onClick={() => handleTabChange(tab)}
              >
                {tabLabels[tab]}
              </button>
            );
          })}
        </div>
      </div>

      {isProjectReindexing && (
        <div className="rounded-md border border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-900">
          {t("reindexingWarning", { progress: project.reindex_progress, total: project.reindex_total })}
        </div>
      )}

      {activeTab === "General" && (
        <div className="max-w-3xl space-y-6">
          <div className="space-y-6 rounded-md">
            <div className="space-y-2">
              <Label htmlFor="name">{t("general.nameLabel")}</Label>
              <Input
                id="name"
                value={effectiveName}
                onChange={(e) => setName(e.target.value)}
                placeholder={t("general.namePlaceholder")}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="description">{t("general.descriptionLabel")}</Label>
              <Textarea
                id="description"
                value={effectiveDescription}
                onChange={(e) => setDescription(e.target.value)}
                placeholder={t("general.descriptionPlaceholder")}
                rows={3}
              />
            </div>
          </div>
          <Button className="cursor-pointer" disabled={isDisabled} onClick={handleSave}>
            {updateProject.isPending ? tCommon("saving") : t("saveChanges")}
          </Button>
          <div className="space-y-3 rounded-md border p-4">
            <p className="text-base font-semibold tracking-tight">{t("general.deleteTitle")}</p>
            <p className="text-sm text-muted-foreground">
              {t("general.deleteDescription")}
            </p>
            <Dialog open={deleteOpen} onOpenChange={setDeleteOpen}>
              <DialogTrigger asChild>
                <Button variant="destructive" className="cursor-pointer">
                  {t("general.deleteButton")}
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>{t("general.deleteDialogTitle")}</DialogTitle>
                  <DialogDescription>
                    {t("general.deleteDialogDescription", { name: project.name })}
                  </DialogDescription>
                </DialogHeader>
                <DialogFooter>
                  <Button
                    variant="outline"
                    className="cursor-pointer"
                    onClick={() => setDeleteOpen(false)}
                  >
                    {tCommon("cancel")}
                  </Button>
                  <Button
                    variant="destructive"
                    className="cursor-pointer"
                    disabled={deleteProject.isPending}
                    onClick={() => {
                      deleteProject.mutate(project.id, {
                        onSuccess: () => {
                          toast.success(t("general.deleteSuccess"));
                          router.push("/projects");
                        },
                        onError: () => toast.error(t("general.deleteError")),
                      });
                    }}
                  >
                    {deleteProject.isPending ? tCommon("deleting") : tCommon("delete")}
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        </div>
      )}

      {activeTab === "Publication" && (
        <div className="max-w-3xl space-y-6">
          <div className="flex items-center gap-3">
            <span className="text-sm font-medium text-muted-foreground">{t("publication.statusLabel")}</span>
            {project.is_published ? (
              <span className="inline-flex items-center gap-1.5 rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-800">
                <span className="h-1.5 w-1.5 rounded-full bg-green-500" />
                {t("publication.published")}
              </span>
            ) : (
              <span className="inline-flex items-center gap-1.5 rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-600">
                <span className="h-1.5 w-1.5 rounded-full bg-gray-400" />
                {t("publication.unpublished")}
              </span>
            )}
          </div>

          {project.is_published && (
            <div className="space-y-2">
              <p className="text-sm font-medium">{t("publication.publicUrl")}</p>
              <div className="flex items-center gap-2 rounded-md border bg-muted/40 px-3 py-2">
                <code className="flex-1 truncate text-xs text-muted-foreground">
                  {typeof window !== "undefined" ? window.location.origin : ""}/chat/{project.id}
                </code>
                <Button
                  type="button"
                  variant="outline"
                  className="h-7 cursor-pointer px-2 text-xs"
                  onClick={() => {
                    navigator.clipboard.writeText(
                      `${window.location.origin}/chat/${project.id}`,
                    );
                    toast.success(t("publication.urlCopied"));
                  }}
                >
                  {t("publication.copy")}
                </Button>
              </div>
              <p className="text-xs text-muted-foreground">
                {t("publication.noteNotAvailable")}
              </p>
            </div>
          )}

          <div className="space-y-3 rounded-md border p-4">
            {project.is_published ? (
              <>
                <p className="text-base font-semibold tracking-tight">{t("publication.unpublishTitle")}</p>
                <p className="text-sm text-muted-foreground">
                  {t("publication.unpublishDescription")}
                </p>
                <Dialog open={unpublishOpen} onOpenChange={setUnpublishOpen}>
                  <DialogTrigger asChild>
                    <Button variant="outline" className="cursor-pointer">
                      {t("publication.unpublishButton")}
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>{t("publication.unpublishDialogTitle")}</DialogTitle>
                      <DialogDescription>
                        {t("publication.unpublishDialogDescription")}
                      </DialogDescription>
                    </DialogHeader>
                    <DialogFooter>
                      <Button
                        variant="outline"
                        className="cursor-pointer"
                        onClick={() => setUnpublishOpen(false)}
                      >
                        {tCommon("cancel")}
                      </Button>
                      <Button
                        className="cursor-pointer"
                        disabled={unpublishProject.isPending}
                        onClick={() => {
                          unpublishProject.mutate(undefined, {
                            onSuccess: () => {
                              toast.success(t("publication.unpublishSuccess"));
                              setUnpublishOpen(false);
                            },
                            onError: () => toast.error(t("publication.unpublishError")),
                          });
                        }}
                      >
                        {unpublishProject.isPending ? t("publication.unpublishing") : tCommon("confirm")}
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </>
            ) : (
              <>
                <p className="text-base font-semibold tracking-tight">{t("publication.publishTitle")}</p>
                <p className="text-sm text-muted-foreground">
                  {t("publication.publishDescription")}
                </p>
                <Dialog open={publishOpen} onOpenChange={setPublishOpen}>
                  <DialogTrigger asChild>
                    <Button className="cursor-pointer">{t("publication.publishButton")}</Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>{t("publication.publishDialogTitle")}</DialogTitle>
                      <DialogDescription>
                        {t("publication.publishDialogDescription")}
                      </DialogDescription>
                    </DialogHeader>
                    <DialogFooter>
                      <Button
                        variant="outline"
                        className="cursor-pointer"
                        onClick={() => setPublishOpen(false)}
                      >
                        {tCommon("cancel")}
                      </Button>
                      <Button
                        className="cursor-pointer"
                        disabled={publishProject.isPending}
                        onClick={() => {
                          publishProject.mutate(undefined, {
                            onSuccess: () => {
                              toast.success(t("publication.publishSuccess"));
                              setPublishOpen(false);
                            },
                            onError: () => toast.error(t("publication.publishError")),
                          });
                        }}
                      >
                        {publishProject.isPending ? t("publication.publishing") : tCommon("confirm")}
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </>
            )}
          </div>
        </div>
      )}

      {activeTab === "Document ingestion" && (
        <div className="max-w-4xl space-y-4">
          <p className="text-muted-foreground text-sm">
            {t("documentIngestion.description")}
          </p>
          <p className="text-sm text-muted-foreground">
            {t("documentIngestion.indexedTotal", { indexed: indexedCount, total: totalCount })}
          </p>
          <DocumentUpload
            isUploading={uploadDocument.isPending}
            uploadProgress={uploadDocument.progress}
            onUpload={(files) => {
              uploadDocument.mutate(files, {
                onSuccess: (result) =>
                  toast.success(t("documentIngestion.uploadSuccess", { succeeded: result.succeeded, failed: result.failed })),
                onError: () => toast.error(t("documentIngestion.uploadError")),
              });
            }}
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
                  embeddingBackend={project.embedding_backend}
                  embeddingModel={project.embedding_model}
                  chunkingStrategy={project.chunking_strategy}
                  parentChildChunking={project.parent_child_chunking}
                  onReindex={(id) => {
                    if (isProjectReindexing) return;
                    reindexDocument.mutate(id, {
                      onSuccess: () => toast.success(t("documentIngestion.reindexSuccess")),
                      onError: () => toast.error(t("documentIngestion.reindexError")),
                    });
                  }}
                  reindexingId={
                    reindexDocument.isPending ? (reindexDocument.variables ?? null) : null
                  }
                  disableReindex={isProjectReindexing}
                  onDelete={(id) => {
                    deleteDocument.mutate(id, {
                      onSuccess: () => toast.success(t("documentIngestion.deleteSuccess")),
                      onError: () => toast.error(t("documentIngestion.deleteError")),
                    });
                  }}
                  isDeleting={deleteDocument.isPending}
                />
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">
              {t("documentIngestion.empty")}
            </p>
          )}
        </div>
      )}

      {activeTab === "Knowledge indexing" && (
        <div className="max-w-3xl space-y-4 rounded-md">
          <p className="text-base font-semibold tracking-tight">{t("knowledgeIndexing.title")}</p>
          <div className="space-y-2">
            <Label htmlFor="chunkingStrategy">{t("knowledgeIndexing.chunkingLabel")}</Label>
            <select
              id="chunkingStrategy"
              value={effectiveChunkingStrategy}
              onChange={(e) => setChunkingStrategy(e.target.value as ChunkingStrategy)}
              className="border-input bg-background w-full rounded-md border px-3 py-2 text-sm"
            >
              <option value="auto">{tForm("chunkingAuto")}</option>
              <option value="fixed_window">{tForm("chunkingFixed")}</option>
              <option value="paragraph">{tForm("chunkingParagraph")}</option>
              <option value="heading_section">{tForm("chunkingHeading")}</option>
              <option value="semantic">{tForm("chunkingSemantic")}</option>
            </select>
          </div>
          <div className="flex items-center gap-2">
            <Switch
              id="parentChildChunking"
              checked={effectiveParentChildChunking}
              onCheckedChange={setParentChildChunking}
            />
            <Label htmlFor="parentChildChunking">{t("knowledgeIndexing.parentChildLabel")}</Label>
          </div>
          <p className="text-xs text-muted-foreground">
            {t("knowledgeIndexing.parentChildRecommendation")}
          </p>
          {isSemanticRecommended ? (
            <p className="text-xs text-amber-700">
              {t("knowledgeIndexing.parentChildWarning")}
            </p>
          ) : null}
          <hr className="border-border" />
          <Button className="cursor-pointer" disabled={isDisabled} onClick={handleSave}>
            {updateProject.isPending ? tCommon("saving") : t("saveChanges")}
          </Button>
          <div className="space-y-3 rounded-md border p-4">
            <p className="text-base font-semibold tracking-tight">{t("knowledgeIndexing.reindexTitle")}</p>
            <p className="text-sm text-muted-foreground">
              {t("knowledgeIndexing.reindexDescription")}
            </p>
            <Button
              className="cursor-pointer"
              disabled={reindexProject.isPending || isProjectReindexing}
              onClick={() => {
                reindexProject.mutate(undefined, {
                  onSuccess: (result) =>
                    toast.success(
                      t("knowledgeIndexing.reindexSuccess", { indexed: result.indexed_documents, total: result.total_documents, failed: result.failed_documents }),
                    ),
                  onError: () => toast.error(t("knowledgeIndexing.reindexError")),
                });
              }}
            >
              {reindexProject.isPending ? t("knowledgeIndexing.reindexing") : t("knowledgeIndexing.reindexButton")}
            </Button>
          </div>
        </div>
      )}

      {activeTab === "Models" && (
        <div className="max-w-3xl space-y-4 rounded-md">
          <p className="text-base font-semibold tracking-tight">{t("models.embeddingTitle")}</p>
          <p className="text-sm text-muted-foreground">
            {t("models.embeddingDescription")}
          </p>
          <div className="space-y-2">
            <Label htmlFor="embeddingBackend">{t("models.embeddingBackendLabel")}</Label>
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
                <Label htmlFor="embeddingCredentialId">{t("models.embeddingApiKeyLabel")}</Label>
                {project.embedding_api_key_masked ? (
                  <p className="text-xs text-muted-foreground">
                    {t("models.existingKey", { key: project.embedding_api_key_masked })}
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
                      ? t("models.noSelection")
                      : t("models.selectEmbeddingFirst")}
                  </option>
                  {embeddingCredentialOptions.map((item) => (
                    <option key={item.id} value={item.id}>
                      {item.masked_key}
                    </option>
                  ))}
                </select>
                {embeddingProviderForHints ? (
                  <p className="text-xs text-muted-foreground">
                    {t("models.savedKeysFor", {
                      provider: embeddingProviderForHints,
                      keys: embeddingCredentialOptions.length > 0
                        ? embeddingCredentialOptions.map((item) => item.masked_key).join(", ")
                        : t("models.noKeys"),
                    })}
                  </p>
                ) : (
                  <p className="text-xs text-muted-foreground">
                    {t("models.embeddingCredentialsNote")}
                  </p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="embeddingModel">{t("models.embeddingModelLabel")}</Label>
                <select
                  id="embeddingModel"
                  value={effectiveEmbeddingModel}
                  onChange={(e) => setEmbeddingModel(e.target.value)}
                  className="border-input bg-background w-full rounded-md border px-3 py-2 text-sm"
                >
                  <option value="">{t("models.selectModel")}</option>
                  {embeddingModelOptions.map((model) => (
                    <option key={model.id} value={model.id}>
                      {model.label}
                    </option>
                  ))}
                </select>
              </div>
            </>
          ) : null}
          <hr className="border-border" />
          <p className="text-base font-semibold tracking-tight">{t("models.llmTitle")}</p>
          <p className="text-sm text-muted-foreground">
            {t("models.llmDescription")}
          </p>
          <div className="space-y-2">
            <Label htmlFor="llmBackend">{t("models.llmBackendLabel")}</Label>
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
                <Label htmlFor="llmCredentialId">{t("models.llmApiKeyLabel")}</Label>
                {project.llm_api_key_masked ? (
                  <p className="text-xs text-muted-foreground">
                    {t("models.existingKey", { key: project.llm_api_key_masked })}
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
                      ? t("models.noSelection")
                      : t("models.selectLlmFirst")}
                  </option>
                  {llmCredentialOptions.map((item) => (
                    <option key={item.id} value={item.id}>
                      {item.masked_key}
                    </option>
                  ))}
                </select>
                {llmProviderForHints ? (
                  <p className="text-xs text-muted-foreground">
                    {t("models.savedKeysFor", {
                      provider: llmProviderForHints,
                      keys: llmCredentialOptions.length > 0
                        ? llmCredentialOptions.map((item) => item.masked_key).join(", ")
                        : t("models.noKeys"),
                    })}
                  </p>
                ) : (
                  <p className="text-xs text-muted-foreground">
                    {t("models.llmCredentialsNote")}
                  </p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="llmModel">{t("models.llmModelLabel")}</Label>
                <select
                  id="llmModel"
                  value={effectiveLlmModel}
                  onChange={(e) => setLlmModel(e.target.value)}
                  className="border-input bg-background w-full rounded-md border px-3 py-2 text-sm"
                >
                  <option value="">{t("models.selectModel")}</option>
                  {llmModelOptions.map((model) => (
                    <option key={model.id} value={model.id}>
                      {model.label}
                    </option>
                  ))}
                </select>
              </div>
            </>
          ) : null}
        </div>
      )}

      {activeTab === "Context retrieval" && (
        <div className="max-w-3xl space-y-4 rounded-md">
          <p className="text-base font-semibold tracking-tight">{t("contextRetrieval.title")}</p>
          <p className="text-sm text-muted-foreground">
            {t("contextRetrieval.description")}
          </p>
          <div className="space-y-2">
            <Label htmlFor="retrievalStrategy">{t("contextRetrieval.searchTypeLabel")}</Label>
            <select
              id="retrievalStrategy"
              value={effectiveRetrievalStrategy}
              onChange={(e) => setRetrievalStrategy(e.target.value as RetrievalStrategy)}
              className="border-input bg-background w-full rounded-md border px-3 py-2 text-sm"
            >
              <option value="hybrid">{t("contextRetrieval.hybrid")}</option>
              <option value="vector">{t("contextRetrieval.vector")}</option>
              <option value="fulltext">{t("contextRetrieval.fulltext")}</option>
            </select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="retrievalTopK">{t("contextRetrieval.topKLabel")}</Label>
            <Input
              id="retrievalTopK"
              type="number"
              min={1}
              max={40}
              value={effectiveRetrievalTopK}
              onChange={(e) => {
                const parsed = Number.parseInt(e.target.value, 10);
                if (Number.isNaN(parsed)) return;
                setRetrievalTopK(Math.max(1, Math.min(40, parsed)));
              }}
            />
            <p className="text-xs text-muted-foreground">
              {t("contextRetrieval.topKNote")}
            </p>
          </div>
          <div className="space-y-2">
            <Label htmlFor="retrievalMinScore">{t("contextRetrieval.minScoreLabel")}</Label>
            <Input
              id="retrievalMinScore"
              type="number"
              min={0}
              max={1}
              step={0.05}
              value={effectiveRetrievalMinScore}
              onChange={(e) => {
                const parsed = Number.parseFloat(e.target.value);
                if (Number.isNaN(parsed)) return;
                const bounded = Math.max(0, Math.min(1, parsed));
                setRetrievalMinScore(Math.round(bounded * 100) / 100);
              }}
            />
            <p className="text-xs text-muted-foreground">
              {t("contextRetrieval.minScoreNote")}
            </p>
          </div>
        </div>
      )}

      {activeTab === "Context augmentation" && (
        <div className="max-w-3xl space-y-4 rounded-md">
          <p className="text-base font-semibold tracking-tight">{t("contextAugmentation.title")}</p>
          <div className="flex items-center justify-between rounded-md border p-3">
            <Label htmlFor="rerankingEnabled">{t("contextAugmentation.rerankingLabel")}</Label>
            <button
              id="rerankingEnabled"
              type="button"
              role="switch"
              aria-checked={effectiveRerankingEnabled}
              onClick={() => setRerankingEnabled(!effectiveRerankingEnabled)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                effectiveRerankingEnabled ? "bg-primary" : "bg-muted"
              }`}
            >
              <span
                className={`inline-block h-5 w-5 transform rounded-full bg-background transition-transform ${
                  effectiveRerankingEnabled ? "translate-x-5" : "translate-x-1"
                }`}
              />
            </button>
          </div>
          {effectiveRerankingEnabled ? (
            <>
              <div className="space-y-2">
                <Label htmlFor="rerankerBackend">{t("contextAugmentation.rerankerBackendLabel")}</Label>
                <select
                  id="rerankerBackend"
                  value={effectiveRerankerBackend}
                  onChange={(e) => {
                    setRerankerBackend(e.target.value as ProjectRerankerBackend);
                    setRerankerModel("");
                  }}
                  className="border-input bg-background w-full rounded-md border px-3 py-2 text-sm"
                >
                  <option value="none">{t("contextAugmentation.rerankerNone")}</option>
                  <option value="cross_encoder">{t("contextAugmentation.rerankerCrossEncoder")}</option>
                  <option value="inmemory">{t("contextAugmentation.rerankerInMemory")}</option>
                  <option value="mmr">{t("contextAugmentation.rerankerMmr")}</option>
                </select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="rerankerModel">{t("contextAugmentation.rerankerModelLabel")}</Label>
                <select
                  id="rerankerModel"
                  value={effectiveRerankerModel}
                  onChange={(e) => setRerankerModel(e.target.value)}
                  disabled={effectiveRerankerBackend === "none"}
                  className="border-input bg-background w-full rounded-md border px-3 py-2 text-sm disabled:opacity-60"
                >
                  <option value="">
                    {effectiveRerankerBackend === "none"
                      ? t("contextAugmentation.selectRerankerBackend")
                      : t("contextAugmentation.selectModel")}
                  </option>
                  {rerankerModelOptions.map((model) => (
                    <option key={model.id} value={model.id}>
                      {model.label}
                    </option>
                  ))}
                </select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="rerankerCandidateMultiplier">{t("contextAugmentation.candidateMultiplierLabel")}</Label>
                <Input
                  id="rerankerCandidateMultiplier"
                  type="number"
                  min={1}
                  max={10}
                  value={effectiveRerankerCandidateMultiplier}
                  onChange={(e) => {
                    const parsed = Number.parseInt(e.target.value, 10);
                    if (Number.isNaN(parsed)) return;
                    setRerankerCandidateMultiplier(Math.max(1, Math.min(10, parsed)));
                  }}
                />
                <p className="text-xs text-muted-foreground">
                  {t("contextAugmentation.candidateMultiplierNote")}
                </p>
              </div>
            </>
          ) : null}
        </div>
      )}

      {activeTab === "Answer generation" && (
        <div className="max-w-3xl space-y-4">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="systemPrompt">{t("answerGeneration.promptLabel")}</Label>
              <span
                className={`text-xs ${nearSystemPromptLimit ? "text-amber-700" : "text-muted-foreground"}`}
              >
                {systemPromptLength}/{MAX_SYSTEM_PROMPT_LENGTH}
              </span>
            </div>
            <Textarea
              id="systemPrompt"
              value={effectiveSystemPrompt}
              onChange={(e) => setSystemPrompt(e.target.value)}
              placeholder={t("answerGeneration.promptPlaceholder")}
              rows={16}
              maxLength={MAX_SYSTEM_PROMPT_LENGTH}
            />
            <p className="text-muted-foreground text-xs">
              {t("answerGeneration.promptLimit")}
            </p>
          </div>
          <div className="space-y-2">
            <Label htmlFor="chatHistoryWindowSize">{t("answerGeneration.chatHistoryWindowLabel")}</Label>
            <Input
              id="chatHistoryWindowSize"
              type="number"
              min={1}
              max={40}
              value={effectiveChatHistoryWindowSize}
              onChange={(e) => {
                const parsed = Number.parseInt(e.target.value, 10);
                if (Number.isNaN(parsed)) return;
                setChatHistoryWindowSize(Math.max(1, Math.min(40, parsed)));
              }}
            />
            <p className="text-xs text-muted-foreground">
              {t("answerGeneration.chatHistoryWindowNote")}
            </p>
          </div>
          <div className="space-y-2">
            <Label htmlFor="chatHistoryMaxChars">{t("answerGeneration.chatHistoryMaxCharsLabel")}</Label>
            <Input
              id="chatHistoryMaxChars"
              type="number"
              min={128}
              max={16000}
              value={effectiveChatHistoryMaxChars}
              onChange={(e) => {
                const parsed = Number.parseInt(e.target.value, 10);
                if (Number.isNaN(parsed)) return;
                setChatHistoryMaxChars(Math.max(128, Math.min(16000, parsed)));
              }}
            />
            <p className="text-xs text-muted-foreground">
              {t("answerGeneration.chatHistoryMaxCharsNote")}
            </p>
          </div>
        </div>
      )}

      {activeTab === "History" && (
        <div className="max-w-3xl space-y-6">
          <ProjectSnapshotsList projectId={params.projectId} />
        </div>
      )}

      {activeTab !== "Document ingestion" && activeTab !== "General" && activeTab !== "Knowledge indexing" && activeTab !== "Publication" && activeTab !== "History" ? (
        <Button className="cursor-pointer" disabled={isDisabled} onClick={handleSave}>
          {updateProject.isPending ? tCommon("saving") : t("saveChanges")}
        </Button>
      ) : null}

      <Dialog open={reindexWarningOpen} onOpenChange={setReindexWarningOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{tForm("reindexTitle")}</DialogTitle>
            <DialogDescription>
              {tForm(effectiveParentChildChunking ? "reindexEnableDescription" : "reindexDisableDescription")}
              {" "}{tForm("reindexDocumentsWarning")}
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
              {tCommon("cancel")}
            </Button>
            <Button
              className="cursor-pointer"
              onClick={() => {
                if (!pendingData) return;
                updateProject.mutate(pendingData, {
                  onSuccess: () => toast.success(t("updateSuccess")),
                  onError: () => toast.error(t("updateError")),
                });
                setReindexWarningOpen(false);
                setPendingData(null);
              }}
            >
              {tForm("confirmAndSave")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
