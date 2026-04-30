"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { useTranslations } from "next-intl";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
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
import { Switch } from "@/components/ui/switch";
import { ProjectSnapshotsList } from "@/components/organisms/project/project-snapshots-list";
import { useDeleteProject, useProject, useReindexProject, useUpdateProject } from "@/lib/hooks/use-projects";
import { useModelCatalog } from "@/lib/hooks/use-model-catalog";
import { useModelCredentials } from "@/lib/hooks/use-model-credentials";
import { useOrgModelCredentials } from "@/lib/hooks/use-org-model-credentials";
import { useOrganizationProjectDefaults } from "@/lib/hooks/use-org-project-defaults";
import type {
  ChunkingStrategy,
  ModelProvider,
  ProjectEmbeddingBackend,
  ProjectLLMBackend,
  ProjectRerankerBackend,
  RetrievalStrategy,
  UpdateProjectRequest,
} from "@/lib/types/api";

export function ProjectAdvancedPanel({ projectId }: { projectId: string }) {
  const t = useTranslations("projects.settings");
  const tCommon = useTranslations("common");
  const tForm = useTranslations("projects.form");
  const router = useRouter();

  const { data: project } = useProject(projectId);
  const updateProject = useUpdateProject(projectId);
  const reindexProject = useReindexProject(projectId);
  const deleteProject = useDeleteProject();
  const { data: modelCatalog } = useModelCatalog();
  const { data: userCredentials } = useModelCredentials();
  const { data: orgCredentials } = useOrgModelCredentials(project?.organization_id);
  const { data: orgDefaults } = useOrganizationProjectDefaults(project?.organization_id);
  const credentials = project?.organization_id ? orgCredentials : userCredentials;

  // Indexation state
  const [chunkingStrategy, setChunkingStrategy] = useState<ChunkingStrategy | null>(null);
  const [parentChildChunking, setParentChildChunking] = useState<boolean | null>(null);
  const [reindexWarningOpen, setReindexWarningOpen] = useState(false);
  const [pendingIndexingData, setPendingIndexingData] = useState<UpdateProjectRequest | null>(null);

  // Models state
  const [embeddingBackend, setEmbeddingBackend] = useState<ProjectEmbeddingBackend | "" | undefined>(undefined);
  const [embeddingModel, setEmbeddingModel] = useState<string | null>(null);
  const [embeddingCredentialId, setEmbeddingCredentialId] = useState<string | null>(null);
  const [llmBackend, setLlmBackend] = useState<ProjectLLMBackend | "" | undefined>(undefined);
  const [llmModel, setLlmModel] = useState<string | null>(null);
  const [llmCredentialId, setLlmCredentialId] = useState<string | null>(null);

  // Retrieval state
  const [retrievalStrategy, setRetrievalStrategy] = useState<RetrievalStrategy | null>(null);
  const [retrievalTopK, setRetrievalTopK] = useState<number | null>(null);
  const [retrievalMinScore, setRetrievalMinScore] = useState<number | null>(null);

  // Augmentation state
  const [rerankingEnabled, setRerankingEnabled] = useState<boolean | null>(null);
  const [rerankerBackend, setRerankerBackend] = useState<ProjectRerankerBackend | null>(null);
  const [rerankerModel, setRerankerModel] = useState<string | null>(null);
  const [rerankerCandidateMultiplier, setRerankerCandidateMultiplier] = useState<number | null>(null);

  // History state
  const [chatHistoryWindowSize, setChatHistoryWindowSize] = useState<number | null>(null);
  const [chatHistoryMaxChars, setChatHistoryMaxChars] = useState<number | null>(null);

  const [deleteOpen, setDeleteOpen] = useState(false);

  if (!project) return null;

  const isProjectReindexing = project.reindex_status === "in_progress";

  // Org override helpers
  const inOrg = !!project.organization_id;
  const orgHasModels = inOrg && orgDefaults != null && (orgDefaults.embedding_backend != null || orgDefaults.llm_backend != null);
  const orgHasIndexing = inOrg && orgDefaults != null && (orgDefaults.chunking_strategy != null || orgDefaults.parent_child_chunking != null);
  const orgHasRetrieval = inOrg && orgDefaults != null && (orgDefaults.retrieval_strategy != null || orgDefaults.retrieval_top_k != null || orgDefaults.retrieval_min_score != null);
  const orgHasReranking = inOrg && orgDefaults != null && (orgDefaults.reranking_enabled != null || orgDefaults.reranker_backend != null);
  const orgHasChatHistory = inOrg && orgDefaults != null && (orgDefaults.chat_history_window_size != null || orgDefaults.chat_history_max_chars != null);

  const lockedModels = orgHasModels && !project.overrides_models_from_org;
  const lockedIndexing = orgHasIndexing && !project.overrides_indexing_from_org;
  const lockedRetrieval = orgHasRetrieval && !project.overrides_retrieval_from_org;
  const lockedReranking = orgHasReranking && !project.overrides_reranking_from_org;
  const lockedChatHistory = orgHasChatHistory && !project.overrides_chat_history_from_org;

  const orgHasAnyDefaults = orgHasModels || orgHasIndexing || orgHasRetrieval || orgHasReranking || orgHasChatHistory;
  const globalOverride = (
    (orgHasModels && project.overrides_models_from_org) ||
    (orgHasIndexing && project.overrides_indexing_from_org) ||
    (orgHasRetrieval && project.overrides_retrieval_from_org) ||
    (orgHasReranking && project.overrides_reranking_from_org) ||
    (orgHasChatHistory && project.overrides_chat_history_from_org)
  );

  function handleGlobalToggle() {
    const newValue = !globalOverride;
    updateProject.mutate(
      {
        ...(orgHasModels && { overrides_models_from_org: newValue }),
        ...(orgHasIndexing && { overrides_indexing_from_org: newValue }),
        ...(orgHasRetrieval && { overrides_retrieval_from_org: newValue }),
        ...(orgHasReranking && { overrides_reranking_from_org: newValue }),
        ...(orgHasChatHistory && { overrides_chat_history_from_org: newValue }),
      },
      { onSuccess: () => toast.success(t("updateSuccess")), onError: () => toast.error(t("updateError")) },
    );
  }

  function handleToggleOverride(flag: string, currentValue: boolean) {
    updateProject.mutate(
      { [flag]: !currentValue },
      { onSuccess: () => toast.success(t("updateSuccess")), onError: () => toast.error(t("updateError")) },
    );
  }

  // --- Indexation computed values ---
  const effectiveChunkingStrategy = lockedIndexing
    ? (orgDefaults?.chunking_strategy as ChunkingStrategy | undefined) ?? project.chunking_strategy
    : chunkingStrategy ?? project.chunking_strategy;
  const effectiveParentChildChunking = lockedIndexing
    ? (orgDefaults?.parent_child_chunking ?? project.parent_child_chunking)
    : (parentChildChunking ?? project.parent_child_chunking);
  const hasIndexingChanges =
    effectiveChunkingStrategy !== project.chunking_strategy ||
    effectiveParentChildChunking !== project.parent_child_chunking;
  const isSemanticRecommended = effectiveParentChildChunking && effectiveChunkingStrategy !== "semantic";
  const indexingPayload: UpdateProjectRequest = {
    chunking_strategy: effectiveChunkingStrategy,
    parent_child_chunking: effectiveParentChildChunking,
  };

  function handleIndexingSave() {
    const parentChildChanged = effectiveParentChildChunking !== project?.parent_child_chunking;
    if (parentChildChanged) {
      setPendingIndexingData(indexingPayload);
      setReindexWarningOpen(true);
      return;
    }
    updateProject.mutate(indexingPayload, {
      onSuccess: () => toast.success(t("updateSuccess")),
      onError: () => toast.error(t("updateError")),
    });
  }

  // --- Models computed values ---
  const effectiveEmbeddingBackend = lockedModels
    ? (orgDefaults?.embedding_backend ?? "")
    : embeddingBackend === undefined ? (project.embedding_backend ?? "") : embeddingBackend;
  const effectiveLlmBackend = lockedModels
    ? (orgDefaults?.llm_backend ?? "")
    : llmBackend === undefined ? (project.llm_backend ?? "") : llmBackend;
  const effectiveEmbeddingModel = lockedModels
    ? (orgDefaults?.embedding_model ?? "")
    : effectiveEmbeddingBackend === "" ? "" : (embeddingModel ?? (project.embedding_model ?? ""));
  const effectiveLlmModel = lockedModels
    ? (orgDefaults?.llm_model ?? "")
    : effectiveLlmBackend === "" ? "" : (llmModel ?? (project.llm_model ?? ""));
  const storedEmbeddingCredentialId = project.organization_id
    ? (project.org_embedding_api_key_credential_id ?? "")
    : (project.embedding_api_key_credential_id ?? "");
  const storedLlmCredentialId = project.organization_id
    ? (project.org_llm_api_key_credential_id ?? "")
    : (project.llm_api_key_credential_id ?? "");
  const effectiveEmbeddingCredentialId = lockedModels
    ? (orgDefaults?.embedding_api_key_credential_id ?? "")
    : effectiveEmbeddingBackend === "" ? "" : (embeddingCredentialId ?? storedEmbeddingCredentialId);
  const effectiveLlmCredentialId = lockedModels
    ? (orgDefaults?.llm_api_key_credential_id ?? "")
    : effectiveLlmBackend === "" ? "" : (llmCredentialId ?? storedLlmCredentialId);

  const credentialsByProvider = (credentials ?? [])
    .filter((c) => c.is_active)
    .reduce<Record<ModelProvider, Array<{ id: string; masked_key: string }>>>(
      (acc, c) => { acc[c.provider].push({ id: c.id, masked_key: c.masked_key }); return acc; },
      { openai: [], gemini: [], anthropic: [] },
    );
  const embeddingProviderForHints = effectiveEmbeddingBackend === "openai" || effectiveEmbeddingBackend === "gemini" ? effectiveEmbeddingBackend : null;
  const llmProviderForHints = effectiveLlmBackend === "openai" || effectiveLlmBackend === "gemini" || effectiveLlmBackend === "anthropic" ? effectiveLlmBackend : null;
  const embeddingCredentialOptions = embeddingProviderForHints ? credentialsByProvider[embeddingProviderForHints] : [];
  const llmCredentialOptions = llmProviderForHints ? credentialsByProvider[llmProviderForHints] : [];
  const embeddingModelOptions = effectiveEmbeddingBackend ? (modelCatalog?.embedding[effectiveEmbeddingBackend as ProjectEmbeddingBackend] ?? []) : [];
  const llmModelOptions = effectiveLlmBackend ? (modelCatalog?.llm[effectiveLlmBackend as ProjectLLMBackend] ?? []) : [];

  const hasModelsChanges =
    effectiveEmbeddingBackend !== (project.embedding_backend ?? "") ||
    effectiveEmbeddingModel !== (project.embedding_model ?? "") ||
    effectiveLlmBackend !== (project.llm_backend ?? "") ||
    effectiveLlmModel !== (project.llm_model ?? "") ||
    effectiveEmbeddingCredentialId !== "" ||
    effectiveLlmCredentialId !== "";

  // --- Retrieval computed values ---
  const effectiveRetrievalStrategy = lockedRetrieval
    ? (orgDefaults?.retrieval_strategy as RetrievalStrategy | undefined) ?? (project.retrieval_strategy ?? "hybrid")
    : retrievalStrategy ?? (project.retrieval_strategy ?? "hybrid");
  const effectiveRetrievalTopK = lockedRetrieval
    ? (orgDefaults?.retrieval_top_k ?? project.retrieval_top_k ?? 8)
    : (retrievalTopK ?? project.retrieval_top_k ?? 8);
  const effectiveRetrievalMinScore = lockedRetrieval
    ? (orgDefaults?.retrieval_min_score ?? project.retrieval_min_score ?? 0.3)
    : (retrievalMinScore ?? project.retrieval_min_score ?? 0.3);

  const hasRetrievalChanges =
    effectiveRetrievalStrategy !== (project.retrieval_strategy ?? "hybrid") ||
    effectiveRetrievalTopK !== (project.retrieval_top_k ?? 8) ||
    effectiveRetrievalMinScore !== (project.retrieval_min_score ?? 0.3);

  // --- Augmentation computed values ---
  const effectiveRerankingEnabled = lockedReranking
    ? (orgDefaults?.reranking_enabled ?? project.reranking_enabled ?? false)
    : (rerankingEnabled ?? project.reranking_enabled ?? false);
  const effectiveRerankerBackend = lockedReranking
    ? (orgDefaults?.reranker_backend ?? project.reranker_backend ?? "none")
    : (rerankerBackend ?? project.reranker_backend ?? "none");
  const effectiveRerankerModel = lockedReranking
    ? (orgDefaults?.reranker_model ?? project.reranker_model ?? "")
    : (rerankerModel ?? project.reranker_model ?? "");
  const effectiveRerankerCandidateMultiplier = lockedReranking
    ? (orgDefaults?.reranker_candidate_multiplier ?? project.reranker_candidate_multiplier ?? 3)
    : (rerankerCandidateMultiplier ?? project.reranker_candidate_multiplier ?? 3);
  const rerankerModelOptions = modelCatalog?.reranker[effectiveRerankerBackend as ProjectRerankerBackend] ?? [];

  const hasAugmentationChanges =
    effectiveRerankingEnabled !== (project.reranking_enabled ?? false) ||
    effectiveRerankerBackend !== (project.reranker_backend ?? "none") ||
    effectiveRerankerModel !== (project.reranker_model ?? "") ||
    effectiveRerankerCandidateMultiplier !== (project.reranker_candidate_multiplier ?? 3);

  // --- History computed values ---
  const effectiveChatHistoryWindowSize = lockedChatHistory
    ? (orgDefaults?.chat_history_window_size ?? project.chat_history_window_size ?? 8)
    : (chatHistoryWindowSize ?? project.chat_history_window_size ?? 8);
  const effectiveChatHistoryMaxChars = lockedChatHistory
    ? (orgDefaults?.chat_history_max_chars ?? project.chat_history_max_chars ?? 4000)
    : (chatHistoryMaxChars ?? project.chat_history_max_chars ?? 4000);

  const hasHistoryChanges =
    effectiveChatHistoryWindowSize !== (project.chat_history_window_size ?? 8) ||
    effectiveChatHistoryMaxChars !== (project.chat_history_max_chars ?? 4000);

  return (
    <div className="max-w-3xl space-y-6">

      {/* Settings card */}
      <Card className="px-5 py-1">

        {/* Global override */}
        {orgHasAnyDefaults && (
          <div className="flex items-center justify-between gap-4 border-b py-4">
            <div className="space-y-0.5">
              <p className="text-sm font-medium">{t("globalOverrideLabel")}</p>
              <p className="text-xs text-muted-foreground">{t("globalOverrideDescription")}</p>
            </div>
            <Switch
              checked={globalOverride}
              onCheckedChange={handleGlobalToggle}
              disabled={updateProject.isPending}
            />
          </div>
        )}

        <Accordion type="multiple" className="w-full">

          {/* Models */}
          <AccordionItem value="models">
            <AccordionTrigger>{t("tabs.models")}</AccordionTrigger>
            <AccordionContent>
              <div className="space-y-4">
                {orgHasModels && (
                  <div className="flex items-center justify-between gap-4 rounded-md border bg-muted/40 px-3 py-2">
                    <Label htmlFor="overrides-models" className="text-sm cursor-pointer">{t("overrideOrgDefaults")}</Label>
                    <Switch
                      id="overrides-models"
                      checked={project.overrides_models_from_org}
                      onCheckedChange={() => handleToggleOverride("overrides_models_from_org", project.overrides_models_from_org)}
                      disabled={!globalOverride || updateProject.isPending}
                    />
                  </div>
                )}
                {lockedModels && <p className="text-xs text-muted-foreground">{t("orgDefaultsApplied")}</p>}
                <fieldset disabled={lockedModels} className="space-y-4 disabled:opacity-60">
                  <div className="space-y-1">
                    <p className="text-sm font-medium">{t("models.embeddingTitle")}</p>
                    <p className="text-sm text-muted-foreground">{t("models.embeddingDescription")}</p>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="embeddingBackend">{t("models.embeddingBackendLabel")}</Label>
                    <select id="embeddingBackend" value={effectiveEmbeddingBackend}
                      onChange={(e) => { setEmbeddingBackend((e.target.value || "") as ProjectEmbeddingBackend | ""); setEmbeddingModel(""); setEmbeddingCredentialId(""); }}
                      className="border-input bg-background w-full rounded-md border px-3 py-2 text-sm"
                    >
                      <option value="">—</option>
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
                        <select id="embeddingCredentialId" value={effectiveEmbeddingCredentialId}
                          onChange={(e) => setEmbeddingCredentialId(e.target.value)}
                          disabled={!embeddingProviderForHints}
                          className="border-input bg-background w-full rounded-md border px-3 py-2 text-sm disabled:opacity-60"
                        >
                          <option value="">{embeddingProviderForHints ? t("models.noSelection") : t("models.selectEmbeddingFirst")}</option>
                          {embeddingCredentialOptions.map((item) => <option key={item.id} value={item.id}>{item.masked_key}</option>)}
                        </select>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="embeddingModel">{t("models.embeddingModelLabel")}</Label>
                        <select id="embeddingModel" value={effectiveEmbeddingModel}
                          onChange={(e) => setEmbeddingModel(e.target.value)}
                          className="border-input bg-background w-full rounded-md border px-3 py-2 text-sm"
                        >
                          <option value="">{t("models.selectModel")}</option>
                          {embeddingModelOptions.map((m) => <option key={m.id} value={m.id}>{m.label}</option>)}
                        </select>
                      </div>
                    </>
                  ) : null}
                  <hr className="border-border" />
                  <div className="space-y-1">
                    <p className="text-sm font-medium">{t("models.llmTitle")}</p>
                    <p className="text-sm text-muted-foreground">{t("models.llmDescription")}</p>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="llmBackend">{t("models.llmBackendLabel")}</Label>
                    <select id="llmBackend" value={effectiveLlmBackend}
                      onChange={(e) => { setLlmBackend((e.target.value || "") as ProjectLLMBackend | ""); setLlmModel(""); setLlmCredentialId(""); }}
                      className="border-input bg-background w-full rounded-md border px-3 py-2 text-sm"
                    >
                      <option value="">—</option>
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
                        <select id="llmCredentialId" value={effectiveLlmCredentialId}
                          onChange={(e) => setLlmCredentialId(e.target.value)}
                          disabled={!llmProviderForHints}
                          className="border-input bg-background w-full rounded-md border px-3 py-2 text-sm disabled:opacity-60"
                        >
                          <option value="">{llmProviderForHints ? t("models.noSelection") : t("models.selectLlmFirst")}</option>
                          {llmCredentialOptions.map((item) => <option key={item.id} value={item.id}>{item.masked_key}</option>)}
                        </select>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="llmModel">{t("models.llmModelLabel")}</Label>
                        <select id="llmModel" value={effectiveLlmModel}
                          onChange={(e) => setLlmModel(e.target.value)}
                          className="border-input bg-background w-full rounded-md border px-3 py-2 text-sm"
                        >
                          <option value="">{t("models.selectModel")}</option>
                          {llmModelOptions.map((m) => <option key={m.id} value={m.id}>{m.label}</option>)}
                        </select>
                      </div>
                    </>
                  ) : null}
                  {!lockedModels && (
                    <Button className="cursor-pointer" disabled={!hasModelsChanges || updateProject.isPending}
                      onClick={() => updateProject.mutate(
                        { embedding_backend: (effectiveEmbeddingBackend || null) as ProjectEmbeddingBackend | null, embedding_model: effectiveEmbeddingModel || null, embedding_api_key: null, embedding_api_key_credential_id: effectiveEmbeddingCredentialId || null, llm_backend: (effectiveLlmBackend || null) as ProjectLLMBackend | null, llm_model: effectiveLlmModel || null, llm_api_key: null, llm_api_key_credential_id: effectiveLlmCredentialId || null },
                        { onSuccess: () => toast.success(t("updateSuccess")), onError: () => toast.error(t("updateError")) },
                      )}
                    >
                      {updateProject.isPending ? tCommon("saving") : t("saveChanges")}
                    </Button>
                  )}
                </fieldset>
              </div>
            </AccordionContent>
          </AccordionItem>

          {/* Indexation */}
          <AccordionItem value="indexing">
            <AccordionTrigger>{t("tabs.knowledgeIndexing")}</AccordionTrigger>
            <AccordionContent>
              <div className="space-y-4">
                {orgHasIndexing && (
                  <div className="flex items-center justify-between gap-4 rounded-md border bg-muted/40 px-3 py-2">
                    <Label htmlFor="overrides-indexing" className="text-sm cursor-pointer">{t("overrideOrgDefaults")}</Label>
                    <Switch
                      id="overrides-indexing"
                      checked={project.overrides_indexing_from_org}
                      onCheckedChange={() => handleToggleOverride("overrides_indexing_from_org", project.overrides_indexing_from_org)}
                      disabled={!globalOverride || updateProject.isPending}
                    />
                  </div>
                )}
                {isProjectReindexing && (
                  <div className="rounded-md border border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-900">
                    {t("reindexingWarning", { progress: project.reindex_progress, total: project.reindex_total })}
                  </div>
                )}
                {lockedIndexing && <p className="text-xs text-muted-foreground">{t("orgDefaultsApplied")}</p>}
                <fieldset disabled={lockedIndexing} className="space-y-4 disabled:opacity-60">
                  <div className="space-y-2">
                    <Label htmlFor="chunkingStrategy">{t("knowledgeIndexing.chunkingLabel")}</Label>
                    <select id="chunkingStrategy" value={effectiveChunkingStrategy}
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
                    <Switch id="parentChildChunking" checked={effectiveParentChildChunking} onCheckedChange={setParentChildChunking} />
                    <Label htmlFor="parentChildChunking">{t("knowledgeIndexing.parentChildLabel")}</Label>
                  </div>
                  <p className="text-xs text-muted-foreground">{t("knowledgeIndexing.parentChildRecommendation")}</p>
                  {isSemanticRecommended && <p className="text-xs text-amber-700">{t("knowledgeIndexing.parentChildWarning")}</p>}
                  {!lockedIndexing && (
                    <Button className="cursor-pointer" disabled={!hasIndexingChanges || updateProject.isPending} onClick={handleIndexingSave}>
                      {updateProject.isPending ? tCommon("saving") : t("saveChanges")}
                    </Button>
                  )}
                </fieldset>
                <div className="space-y-3 rounded-md border p-4">
                  <p className="text-sm font-medium">{t("knowledgeIndexing.reindexTitle")}</p>
                  <p className="text-sm text-muted-foreground">{t("knowledgeIndexing.reindexDescription")}</p>
                  <Button className="cursor-pointer" disabled={reindexProject.isPending || isProjectReindexing}
                    onClick={() => reindexProject.mutate(undefined, {
                      onSuccess: (result) => toast.success(t("knowledgeIndexing.reindexSuccess", { indexed: result.indexed_documents, total: result.total_documents, failed: result.failed_documents })),
                      onError: () => toast.error(t("knowledgeIndexing.reindexError")),
                    })}
                  >
                    {reindexProject.isPending ? t("knowledgeIndexing.reindexing") : t("knowledgeIndexing.reindexButton")}
                  </Button>
                </div>
              </div>
            </AccordionContent>
          </AccordionItem>

          {/* Retrieval */}
          <AccordionItem value="retrieval">
            <AccordionTrigger>{t("tabs.contextRetrieval")}</AccordionTrigger>
            <AccordionContent>
              <div className="space-y-4">
                {orgHasRetrieval && (
                  <div className="flex items-center justify-between gap-4 rounded-md border bg-muted/40 px-3 py-2">
                    <Label htmlFor="overrides-retrieval" className="text-sm cursor-pointer">{t("overrideOrgDefaults")}</Label>
                    <Switch
                      id="overrides-retrieval"
                      checked={project.overrides_retrieval_from_org}
                      onCheckedChange={() => handleToggleOverride("overrides_retrieval_from_org", project.overrides_retrieval_from_org)}
                      disabled={!globalOverride || updateProject.isPending}
                    />
                  </div>
                )}
                {lockedRetrieval && <p className="text-xs text-muted-foreground">{t("orgDefaultsApplied")}</p>}
                <fieldset disabled={lockedRetrieval} className="space-y-4 disabled:opacity-60">
                  <p className="text-sm text-muted-foreground">{t("contextRetrieval.description")}</p>
                  <div className="space-y-2">
                    <Label htmlFor="retrievalStrategy">{t("contextRetrieval.searchTypeLabel")}</Label>
                    <select id="retrievalStrategy" value={effectiveRetrievalStrategy}
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
                    <Input id="retrievalTopK" type="number" min={1} max={40} value={effectiveRetrievalTopK}
                      onChange={(e) => { const v = Number.parseInt(e.target.value, 10); if (!Number.isNaN(v)) setRetrievalTopK(Math.max(1, Math.min(40, v))); }}
                    />
                    <p className="text-xs text-muted-foreground">{t("contextRetrieval.topKNote")}</p>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="retrievalMinScore">{t("contextRetrieval.minScoreLabel")}</Label>
                    <Input id="retrievalMinScore" type="number" min={0} max={1} step={0.05} value={effectiveRetrievalMinScore}
                      onChange={(e) => { const v = Number.parseFloat(e.target.value); if (!Number.isNaN(v)) setRetrievalMinScore(Math.round(Math.max(0, Math.min(1, v)) * 100) / 100); }}
                    />
                    <p className="text-xs text-muted-foreground">{t("contextRetrieval.minScoreNote")}</p>
                  </div>
                  {!lockedRetrieval && (
                    <Button className="cursor-pointer" disabled={!hasRetrievalChanges || updateProject.isPending}
                      onClick={() => updateProject.mutate(
                        { retrieval_strategy: effectiveRetrievalStrategy, retrieval_top_k: effectiveRetrievalTopK, retrieval_min_score: effectiveRetrievalMinScore },
                        { onSuccess: () => toast.success(t("updateSuccess")), onError: () => toast.error(t("updateError")) },
                      )}
                    >
                      {updateProject.isPending ? tCommon("saving") : t("saveChanges")}
                    </Button>
                  )}
                </fieldset>
              </div>
            </AccordionContent>
          </AccordionItem>

          {/* Augmentation */}
          <AccordionItem value="augmentation">
            <AccordionTrigger>{t("tabs.contextAugmentation")}</AccordionTrigger>
            <AccordionContent>
              <div className="space-y-4">
                {orgHasReranking && (
                  <div className="flex items-center justify-between gap-4 rounded-md border bg-muted/40 px-3 py-2">
                    <Label htmlFor="overrides-reranking" className="text-sm cursor-pointer">{t("overrideOrgDefaults")}</Label>
                    <Switch
                      id="overrides-reranking"
                      checked={project.overrides_reranking_from_org}
                      onCheckedChange={() => handleToggleOverride("overrides_reranking_from_org", project.overrides_reranking_from_org)}
                      disabled={!globalOverride || updateProject.isPending}
                    />
                  </div>
                )}
                {lockedReranking && <p className="text-xs text-muted-foreground">{t("orgDefaultsApplied")}</p>}
                <fieldset disabled={lockedReranking} className="space-y-4 disabled:opacity-60">
                  <div className="flex items-center gap-2">
                    <Switch id="rerankingEnabled" checked={effectiveRerankingEnabled} onCheckedChange={setRerankingEnabled} />
                    <Label htmlFor="rerankingEnabled">{t("contextAugmentation.rerankingLabel")}</Label>
                  </div>
                  {effectiveRerankingEnabled && (
                    <>
                      <div className="space-y-2">
                        <Label htmlFor="rerankerBackend">{t("contextAugmentation.rerankerBackendLabel")}</Label>
                        <select id="rerankerBackend" value={effectiveRerankerBackend}
                          onChange={(e) => { setRerankerBackend(e.target.value as ProjectRerankerBackend); setRerankerModel(""); }}
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
                        <select id="rerankerModel" value={effectiveRerankerModel}
                          onChange={(e) => setRerankerModel(e.target.value)}
                          disabled={effectiveRerankerBackend === "none"}
                          className="border-input bg-background w-full rounded-md border px-3 py-2 text-sm disabled:opacity-60"
                        >
                          <option value="">{effectiveRerankerBackend === "none" ? t("contextAugmentation.selectRerankerBackend") : t("contextAugmentation.selectModel")}</option>
                          {rerankerModelOptions.map((m) => <option key={m.id} value={m.id}>{m.label}</option>)}
                        </select>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="rerankerCandidateMultiplier">{t("contextAugmentation.candidateMultiplierLabel")}</Label>
                        <Input id="rerankerCandidateMultiplier" type="number" min={1} max={10} value={effectiveRerankerCandidateMultiplier}
                          onChange={(e) => { const v = Number.parseInt(e.target.value, 10); if (!Number.isNaN(v)) setRerankerCandidateMultiplier(Math.max(1, Math.min(10, v))); }}
                        />
                        <p className="text-xs text-muted-foreground">{t("contextAugmentation.candidateMultiplierNote")}</p>
                      </div>
                    </>
                  )}
                  {!lockedReranking && (
                    <Button className="cursor-pointer" disabled={!hasAugmentationChanges || updateProject.isPending}
                      onClick={() => updateProject.mutate(
                        { reranking_enabled: effectiveRerankingEnabled, reranker_backend: effectiveRerankerBackend as ProjectRerankerBackend, reranker_model: effectiveRerankerModel || null, reranker_candidate_multiplier: effectiveRerankerCandidateMultiplier },
                        { onSuccess: () => toast.success(t("updateSuccess")), onError: () => toast.error(t("updateError")) },
                      )}
                    >
                      {updateProject.isPending ? tCommon("saving") : t("saveChanges")}
                    </Button>
                  )}
                </fieldset>
              </div>
            </AccordionContent>
          </AccordionItem>

          {/* Chat history */}
          <AccordionItem value="history">
            <AccordionTrigger>{t("tabs.answerGeneration")}</AccordionTrigger>
            <AccordionContent>
              <div className="space-y-4">
                {orgHasChatHistory && (
                  <div className="flex items-center justify-between gap-4 rounded-md border bg-muted/40 px-3 py-2">
                    <Label htmlFor="overrides-chat-history" className="text-sm cursor-pointer">{t("overrideOrgDefaults")}</Label>
                    <Switch
                      id="overrides-chat-history"
                      checked={project.overrides_chat_history_from_org}
                      onCheckedChange={() => handleToggleOverride("overrides_chat_history_from_org", project.overrides_chat_history_from_org)}
                      disabled={!globalOverride || updateProject.isPending}
                    />
                  </div>
                )}
                {lockedChatHistory && <p className="text-xs text-muted-foreground">{t("orgDefaultsApplied")}</p>}
                <fieldset disabled={lockedChatHistory} className="space-y-4 disabled:opacity-60">
                  <div className="space-y-2">
                    <Label htmlFor="chatHistoryWindowSize">{t("answerGeneration.chatHistoryWindowLabel")}</Label>
                    <Input id="chatHistoryWindowSize" type="number" min={1} max={40} value={effectiveChatHistoryWindowSize}
                      onChange={(e) => { const v = Number.parseInt(e.target.value, 10); if (!Number.isNaN(v)) setChatHistoryWindowSize(Math.max(1, Math.min(40, v))); }}
                    />
                    <p className="text-xs text-muted-foreground">{t("answerGeneration.chatHistoryWindowNote")}</p>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="chatHistoryMaxChars">{t("answerGeneration.chatHistoryMaxCharsLabel")}</Label>
                    <Input id="chatHistoryMaxChars" type="number" min={128} max={16000} value={effectiveChatHistoryMaxChars}
                      onChange={(e) => { const v = Number.parseInt(e.target.value, 10); if (!Number.isNaN(v)) setChatHistoryMaxChars(Math.max(128, Math.min(16000, v))); }}
                    />
                    <p className="text-xs text-muted-foreground">{t("answerGeneration.chatHistoryMaxCharsNote")}</p>
                  </div>
                  {!lockedChatHistory && (
                    <Button className="cursor-pointer" disabled={!hasHistoryChanges || updateProject.isPending}
                      onClick={() => updateProject.mutate(
                        { chat_history_window_size: effectiveChatHistoryWindowSize, chat_history_max_chars: effectiveChatHistoryMaxChars },
                        { onSuccess: () => toast.success(t("updateSuccess")), onError: () => toast.error(t("updateError")) },
                      )}
                    >
                      {updateProject.isPending ? tCommon("saving") : t("saveChanges")}
                    </Button>
                  )}
                </fieldset>
              </div>
            </AccordionContent>
          </AccordionItem>

        </Accordion>
      </Card>

      <Dialog open={reindexWarningOpen} onOpenChange={setReindexWarningOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{tForm("reindexTitle")}</DialogTitle>
            <DialogDescription>
              {tForm(effectiveParentChildChunking ? "reindexEnableDescription" : "reindexDisableDescription")}{" "}
              {tForm("reindexDocumentsWarning")}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" className="cursor-pointer" onClick={() => { setReindexWarningOpen(false); setPendingIndexingData(null); }}>
              {tCommon("cancel")}
            </Button>
            <Button className="cursor-pointer" onClick={() => {
              if (!pendingIndexingData) return;
              updateProject.mutate(pendingIndexingData, {
                onSuccess: () => toast.success(t("updateSuccess")),
                onError: () => toast.error(t("updateError")),
              });
              setReindexWarningOpen(false);
              setPendingIndexingData(null);
            }}>
              {tForm("confirmAndSave")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Versions */}
      <Card className="space-y-4 p-5">
        <h3 className="text-base font-semibold tracking-tight">{t("tabs.history")}</h3>
        <ProjectSnapshotsList projectId={projectId} />
      </Card>

      {/* Danger zone */}
      <div className="space-y-3 rounded-md border border-destructive/30 p-4">
        <p className="text-sm font-medium">{t("general.deleteTitle")}</p>
        <p className="text-sm text-muted-foreground">{t("general.deleteDescription")}</p>
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
              <Button variant="outline" className="cursor-pointer" onClick={() => setDeleteOpen(false)}>
                {tCommon("cancel")}
              </Button>
              <Button variant="destructive" className="cursor-pointer" disabled={deleteProject.isPending}
                onClick={() => deleteProject.mutate(project.id, {
                  onSuccess: () => { toast.success(t("general.deleteSuccess")); router.push("/projects"); },
                  onError: () => toast.error(t("general.deleteError")),
                })}
              >
                {deleteProject.isPending ? tCommon("deleting") : tCommon("delete")}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
}
