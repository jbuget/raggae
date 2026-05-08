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
import { useSystemDefaults } from "@/lib/hooks/use-system-defaults";
import { useUserProjectDefaults } from "@/lib/hooks/use-user-project-defaults";
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
  const { data: userDefaults } = useUserProjectDefaults();
  const { data: systemDefaults } = useSystemDefaults();
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

  // User defaults helpers
  const userHasModels = userDefaults != null && (userDefaults.embedding_backend != null || userDefaults.llm_backend != null);
  const userHasIndexing = userDefaults != null && (userDefaults.chunking_strategy != null || userDefaults.parent_child_chunking != null);
  const userHasRetrieval = userDefaults != null && (userDefaults.retrieval_strategy != null || userDefaults.retrieval_top_k != null || userDefaults.retrieval_min_score != null);
  const userHasReranking = userDefaults != null && (userDefaults.reranking_enabled != null || userDefaults.reranker_backend != null);
  const userHasChatHistory = userDefaults != null && (userDefaults.chat_history_window_size != null || userDefaults.chat_history_max_chars != null);

  const lockedByUserModels = !inOrg && userHasModels && !project.overrides_models_from_user;
  const lockedByUserIndexing = !inOrg && userHasIndexing && !project.overrides_indexing_from_user;
  const lockedByUserRetrieval = !inOrg && userHasRetrieval && !project.overrides_retrieval_from_user;
  const lockedByUserReranking = !inOrg && userHasReranking && !project.overrides_reranking_from_user;
  const lockedByUserChatHistory = !inOrg && userHasChatHistory && !project.overrides_chat_history_from_user;

  function handleToggleOverride(flag: string, currentValue: boolean, onUnlock?: () => void, onLock?: () => void) {
    if (!currentValue) onUnlock?.(); else onLock?.();
    updateProject.mutate(
      { [flag]: !currentValue },
      { onSuccess: () => toast.success(t("updateSuccess")), onError: () => toast.error(t("updateError")) },
    );
  }

  function resetModels() { setEmbeddingBackend(undefined); setEmbeddingModel(null); setEmbeddingCredentialId(null); setLlmBackend(undefined); setLlmModel(null); setLlmCredentialId(null); }
  function fillModelsFrom(src: typeof orgDefaults | typeof userDefaults) { setEmbeddingBackend((src?.embedding_backend ?? "") as ProjectEmbeddingBackend | ""); setEmbeddingModel(src?.embedding_model ?? null); setEmbeddingCredentialId(src?.embedding_api_key_credential_id ?? null); setLlmBackend((src?.llm_backend ?? "") as ProjectLLMBackend | ""); setLlmModel(src?.llm_model ?? null); setLlmCredentialId(src?.llm_api_key_credential_id ?? null); }

  function resetIndexing() { setChunkingStrategy(null); setParentChildChunking(null); }
  function fillIndexingFrom(src: typeof orgDefaults | typeof userDefaults) { setChunkingStrategy((src?.chunking_strategy ?? null) as ChunkingStrategy | null); setParentChildChunking(src?.parent_child_chunking ?? null); }

  function resetRetrieval() { setRetrievalStrategy(null); setRetrievalTopK(null); setRetrievalMinScore(null); }
  function fillRetrievalFrom(src: typeof orgDefaults | typeof userDefaults) { setRetrievalStrategy((src?.retrieval_strategy ?? null) as RetrievalStrategy | null); setRetrievalTopK(src?.retrieval_top_k ?? null); setRetrievalMinScore(src?.retrieval_min_score ?? null); }

  function resetReranking() { setRerankingEnabled(null); setRerankerBackend(null); setRerankerModel(null); setRerankerCandidateMultiplier(null); }
  function fillRerankingFrom(src: typeof orgDefaults | typeof userDefaults) { setRerankingEnabled(src?.reranking_enabled ?? null); setRerankerBackend((src?.reranker_backend ?? null) as ProjectRerankerBackend | null); setRerankerModel(src?.reranker_model ?? null); setRerankerCandidateMultiplier(src?.reranker_candidate_multiplier ?? null); }

  function resetHistory() { setChatHistoryWindowSize(null); setChatHistoryMaxChars(null); }
  function fillHistoryFrom(src: typeof orgDefaults | typeof userDefaults) { setChatHistoryWindowSize(src?.chat_history_window_size ?? null); setChatHistoryMaxChars(src?.chat_history_max_chars ?? null); }

  // --- Indexation computed values ---
  const effectiveChunkingStrategy = lockedIndexing
    ? (orgDefaults?.chunking_strategy as ChunkingStrategy | undefined) ?? project.chunking_strategy
    : lockedByUserIndexing
      ? (userDefaults?.chunking_strategy as ChunkingStrategy | undefined) ?? project.chunking_strategy
      : chunkingStrategy ?? project.chunking_strategy;
  const effectiveParentChildChunking = lockedIndexing
    ? (orgDefaults?.parent_child_chunking ?? project.parent_child_chunking)
    : lockedByUserIndexing
      ? (userDefaults?.parent_child_chunking ?? project.parent_child_chunking)
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
    : lockedByUserModels
      ? (userDefaults?.embedding_backend ?? project.embedding_backend ?? "")
      : embeddingBackend === undefined ? (project.embedding_backend ?? systemDefaults?.embedding_backend ?? "") : embeddingBackend;
  const effectiveLlmBackend = lockedModels
    ? (orgDefaults?.llm_backend ?? "")
    : lockedByUserModels
      ? (userDefaults?.llm_backend ?? project.llm_backend ?? "")
      : llmBackend === undefined ? (project.llm_backend ?? systemDefaults?.llm_backend ?? "") : llmBackend;
  const effectiveEmbeddingModel = lockedModels
    ? (orgDefaults?.embedding_model ?? "")
    : lockedByUserModels
      ? (userDefaults?.embedding_model ?? project.embedding_model ?? "")
      : effectiveEmbeddingBackend === "" ? "" : (embeddingModel ?? (project.embedding_model ?? systemDefaults?.embedding_model ?? ""));
  const effectiveLlmModel = lockedModels
    ? (orgDefaults?.llm_model ?? "")
    : lockedByUserModels
      ? (userDefaults?.llm_model ?? project.llm_model ?? "")
      : effectiveLlmBackend === "" ? "" : (llmModel ?? (project.llm_model ?? systemDefaults?.llm_model ?? ""));
  const storedEmbeddingCredentialId = project.organization_id
    ? (project.org_embedding_api_key_credential_id ?? "")
    : (project.embedding_api_key_credential_id ?? "");
  const storedLlmCredentialId = project.organization_id
    ? (project.org_llm_api_key_credential_id ?? "")
    : (project.llm_api_key_credential_id ?? "");
  const effectiveEmbeddingCredentialId = lockedModels
    ? (orgDefaults?.embedding_api_key_credential_id ?? "")
    : lockedByUserModels
      ? (userDefaults?.embedding_api_key_credential_id ?? storedEmbeddingCredentialId)
      : effectiveEmbeddingBackend === "" ? "" : (embeddingCredentialId ?? storedEmbeddingCredentialId);
  const effectiveLlmCredentialId = lockedModels
    ? (orgDefaults?.llm_api_key_credential_id ?? "")
    : lockedByUserModels
      ? (userDefaults?.llm_api_key_credential_id ?? storedLlmCredentialId)
      : effectiveLlmBackend === "" ? "" : (llmCredentialId ?? storedLlmCredentialId);

  const credentialsByProvider = (credentials ?? [])
    .filter((c) => c.is_active)
    .reduce<Record<string, Array<{ id: string; masked_key: string }>>>(
      (acc, c) => { (acc[c.provider] ??= []).push({ id: c.id, masked_key: c.masked_key }); return acc; },
      {},
    );
  const embeddingProviderForHints = effectiveEmbeddingBackend === "openai" || effectiveEmbeddingBackend === "gemini" ? effectiveEmbeddingBackend : null;
  const llmProviderForHints = effectiveLlmBackend === "openai" || effectiveLlmBackend === "gemini" || effectiveLlmBackend === "anthropic" ? effectiveLlmBackend : null;
  const embeddingCredentialOptions = embeddingProviderForHints ? (credentialsByProvider[embeddingProviderForHints] ?? []) : [];
  const llmCredentialOptions = llmProviderForHints ? (credentialsByProvider[llmProviderForHints] ?? []) : [];
  const embeddingModelOptions = effectiveEmbeddingBackend ? (modelCatalog?.embedding[effectiveEmbeddingBackend as ProjectEmbeddingBackend] ?? []) : [];
  const llmModelOptions = effectiveLlmBackend ? (modelCatalog?.llm[effectiveLlmBackend as ProjectLLMBackend] ?? []) : [];

  const hasModelsChanges =
    effectiveEmbeddingBackend !== (project.embedding_backend ?? systemDefaults?.embedding_backend ?? "") ||
    effectiveEmbeddingModel !== (project.embedding_model ?? systemDefaults?.embedding_model ?? "") ||
    effectiveLlmBackend !== (project.llm_backend ?? systemDefaults?.llm_backend ?? "") ||
    effectiveLlmModel !== (project.llm_model ?? systemDefaults?.llm_model ?? "") ||
    effectiveEmbeddingCredentialId !== storedEmbeddingCredentialId ||
    effectiveLlmCredentialId !== storedLlmCredentialId;

  // --- Retrieval computed values ---
  const effectiveRetrievalStrategy = lockedRetrieval
    ? (orgDefaults?.retrieval_strategy as RetrievalStrategy | undefined) ?? (project.retrieval_strategy ?? "hybrid")
    : lockedByUserRetrieval
      ? (userDefaults?.retrieval_strategy as RetrievalStrategy | undefined) ?? (project.retrieval_strategy ?? "hybrid")
      : retrievalStrategy ?? (project.retrieval_strategy ?? systemDefaults?.retrieval_strategy ?? "hybrid");
  const effectiveRetrievalTopK = lockedRetrieval
    ? (orgDefaults?.retrieval_top_k ?? project.retrieval_top_k ?? 8)
    : lockedByUserRetrieval
      ? (userDefaults?.retrieval_top_k ?? project.retrieval_top_k ?? 8)
      : (retrievalTopK ?? project.retrieval_top_k ?? systemDefaults?.retrieval_top_k ?? 8);
  const effectiveRetrievalMinScore = lockedRetrieval
    ? (orgDefaults?.retrieval_min_score ?? project.retrieval_min_score ?? 0.3)
    : lockedByUserRetrieval
      ? (userDefaults?.retrieval_min_score ?? project.retrieval_min_score ?? 0.3)
      : (retrievalMinScore ?? project.retrieval_min_score ?? systemDefaults?.retrieval_min_score ?? 0.3);

  const hasRetrievalChanges =
    effectiveRetrievalStrategy !== (project.retrieval_strategy ?? systemDefaults?.retrieval_strategy ?? "hybrid") ||
    effectiveRetrievalTopK !== (project.retrieval_top_k ?? systemDefaults?.retrieval_top_k ?? 8) ||
    effectiveRetrievalMinScore !== (project.retrieval_min_score ?? systemDefaults?.retrieval_min_score ?? 0.3);

  // --- Augmentation computed values ---
  const effectiveRerankingEnabled = lockedReranking
    ? (orgDefaults?.reranking_enabled ?? project.reranking_enabled ?? false)
    : lockedByUserReranking
      ? (userDefaults?.reranking_enabled ?? project.reranking_enabled ?? false)
      : (rerankingEnabled ?? project.reranking_enabled ?? false);
  const effectiveRerankerBackend = lockedReranking
    ? (orgDefaults?.reranker_backend ?? project.reranker_backend ?? "none")
    : lockedByUserReranking
      ? (userDefaults?.reranker_backend ?? project.reranker_backend ?? "none")
      : (rerankerBackend ?? project.reranker_backend ?? systemDefaults?.reranker_backend ?? "none");
  const effectiveRerankerModel = lockedReranking
    ? (orgDefaults?.reranker_model ?? project.reranker_model ?? "")
    : lockedByUserReranking
      ? (userDefaults?.reranker_model ?? project.reranker_model ?? "")
      : (rerankerModel ?? project.reranker_model ?? systemDefaults?.reranker_model ?? "");
  const effectiveRerankerCandidateMultiplier = lockedReranking
    ? (orgDefaults?.reranker_candidate_multiplier ?? project.reranker_candidate_multiplier ?? 3)
    : lockedByUserReranking
      ? (userDefaults?.reranker_candidate_multiplier ?? project.reranker_candidate_multiplier ?? 3)
      : (rerankerCandidateMultiplier ?? project.reranker_candidate_multiplier ?? systemDefaults?.reranker_candidate_multiplier ?? 3);
  const rerankerModelOptions = modelCatalog?.reranker[effectiveRerankerBackend as ProjectRerankerBackend] ?? [];

  const hasAugmentationChanges =
    effectiveRerankingEnabled !== (project.reranking_enabled ?? false) ||
    effectiveRerankerBackend !== (project.reranker_backend ?? systemDefaults?.reranker_backend ?? "none") ||
    effectiveRerankerModel !== (project.reranker_model ?? systemDefaults?.reranker_model ?? "") ||
    effectiveRerankerCandidateMultiplier !== (project.reranker_candidate_multiplier ?? systemDefaults?.reranker_candidate_multiplier ?? 3);

  // --- History computed values ---
  const effectiveChatHistoryWindowSize = lockedChatHistory
    ? (orgDefaults?.chat_history_window_size ?? project.chat_history_window_size ?? 8)
    : lockedByUserChatHistory
      ? (userDefaults?.chat_history_window_size ?? project.chat_history_window_size ?? 8)
      : (chatHistoryWindowSize ?? project.chat_history_window_size ?? systemDefaults?.chat_history_window_size ?? 8);
  const effectiveChatHistoryMaxChars = lockedChatHistory
    ? (orgDefaults?.chat_history_max_chars ?? project.chat_history_max_chars ?? 4000)
    : lockedByUserChatHistory
      ? (userDefaults?.chat_history_max_chars ?? project.chat_history_max_chars ?? 4000)
      : (chatHistoryMaxChars ?? project.chat_history_max_chars ?? systemDefaults?.chat_history_max_chars ?? 4000);

  const hasHistoryChanges =
    effectiveChatHistoryWindowSize !== (project.chat_history_window_size ?? systemDefaults?.chat_history_window_size ?? 8) ||
    effectiveChatHistoryMaxChars !== (project.chat_history_max_chars ?? systemDefaults?.chat_history_max_chars ?? 4000);

  return (
    <div className="space-y-6">

      {/* Settings card */}
      <Card className="px-5 py-1">

        <Accordion type="multiple" className="w-full">

          {/* Models */}
          <AccordionItem value="models">
            <AccordionTrigger className="text-base">{t("tabs.models")}</AccordionTrigger>
            <AccordionContent>
              <div className="space-y-4">
                {orgHasModels && (
                  <div className="flex items-center justify-between gap-4 rounded-md border bg-muted/40 px-3 py-2">
                    <Label htmlFor="overrides-models" className="text-sm cursor-pointer">{t("overrideOrgDefaults")}</Label>
                    <Switch
                      id="overrides-models"
                      checked={project.overrides_models_from_org}
                      onCheckedChange={() => handleToggleOverride("overrides_models_from_org", project.overrides_models_from_org, () => fillModelsFrom(orgDefaults), resetModels)}
                      disabled={updateProject.isPending}
                    />
                  </div>
                )}
                {lockedModels && <p className="text-xs text-foreground">{t("orgDefaultsApplied")}</p>}
                {!inOrg && userHasModels && (
                  <div className="flex items-center justify-between gap-4 rounded-md border bg-muted/40 px-3 py-2">
                    <Label htmlFor="overrides-models-user" className="text-sm cursor-pointer">{t("overrideUserDefaults")}</Label>
                    <Switch
                      id="overrides-models-user"
                      checked={project.overrides_models_from_user}
                      onCheckedChange={() => handleToggleOverride("overrides_models_from_user", project.overrides_models_from_user, () => fillModelsFrom(userDefaults), resetModels)}
                      disabled={updateProject.isPending}
                    />
                  </div>
                )}
                {lockedByUserModels && <p className="text-xs text-foreground">{t("userDefaultsApplied")}</p>}
                {(!lockedModels && !lockedByUserModels && !project.embedding_backend && !project.llm_backend && systemDefaults) && (
                  <p className="text-xs text-foreground">{t("systemDefaultsApplied")}</p>
                )}
                <fieldset disabled={lockedModels || lockedByUserModels} className="space-y-4 disabled:opacity-60">
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
                  {!lockedModels && !lockedByUserModels && (
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
            <AccordionTrigger className="text-base">{t("tabs.knowledgeIndexing")}</AccordionTrigger>
            <AccordionContent>
              <div className="space-y-4">
                {orgHasIndexing && (
                  <div className="flex items-center justify-between gap-4 rounded-md border bg-muted/40 px-3 py-2">
                    <Label htmlFor="overrides-indexing" className="text-sm cursor-pointer">{t("overrideOrgDefaults")}</Label>
                    <Switch
                      id="overrides-indexing"
                      checked={project.overrides_indexing_from_org}
                      onCheckedChange={() => handleToggleOverride("overrides_indexing_from_org", project.overrides_indexing_from_org, () => fillIndexingFrom(orgDefaults), resetIndexing)}
                      disabled={updateProject.isPending}
                    />
                  </div>
                )}
                {lockedIndexing && <p className="text-xs text-foreground">{t("orgDefaultsApplied")}</p>}
                {!inOrg && userHasIndexing && (
                  <div className="flex items-center justify-between gap-4 rounded-md border bg-muted/40 px-3 py-2">
                    <Label htmlFor="overrides-indexing-user" className="text-sm cursor-pointer">{t("overrideUserDefaults")}</Label>
                    <Switch
                      id="overrides-indexing-user"
                      checked={project.overrides_indexing_from_user}
                      onCheckedChange={() => handleToggleOverride("overrides_indexing_from_user", project.overrides_indexing_from_user, () => fillIndexingFrom(userDefaults), resetIndexing)}
                      disabled={updateProject.isPending}
                    />
                  </div>
                )}
                {lockedByUserIndexing && <p className="text-xs text-foreground">{t("userDefaultsApplied")}</p>}
                {isProjectReindexing && (
                  <div className="rounded-md border border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-900">
                    {t("reindexingWarning", { progress: project.reindex_progress, total: project.reindex_total })}
                  </div>
                )}
                <fieldset disabled={lockedIndexing || lockedByUserIndexing} className="space-y-4 disabled:opacity-60">
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
                  {!lockedIndexing && !lockedByUserIndexing && (
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
            <AccordionTrigger className="text-base">{t("tabs.contextRetrieval")}</AccordionTrigger>
            <AccordionContent>
              <div className="space-y-4">
                {orgHasRetrieval && (
                  <div className="flex items-center justify-between gap-4 rounded-md border bg-muted/40 px-3 py-2">
                    <Label htmlFor="overrides-retrieval" className="text-sm cursor-pointer">{t("overrideOrgDefaults")}</Label>
                    <Switch
                      id="overrides-retrieval"
                      checked={project.overrides_retrieval_from_org}
                      onCheckedChange={() => handleToggleOverride("overrides_retrieval_from_org", project.overrides_retrieval_from_org, () => fillRetrievalFrom(orgDefaults), resetRetrieval)}
                      disabled={updateProject.isPending}
                    />
                  </div>
                )}
                {lockedRetrieval && <p className="text-xs text-foreground">{t("orgDefaultsApplied")}</p>}
                {!inOrg && userHasRetrieval && (
                  <div className="flex items-center justify-between gap-4 rounded-md border bg-muted/40 px-3 py-2">
                    <Label htmlFor="overrides-retrieval-user" className="text-sm cursor-pointer">{t("overrideUserDefaults")}</Label>
                    <Switch
                      id="overrides-retrieval-user"
                      checked={project.overrides_retrieval_from_user}
                      onCheckedChange={() => handleToggleOverride("overrides_retrieval_from_user", project.overrides_retrieval_from_user, () => fillRetrievalFrom(userDefaults), resetRetrieval)}
                      disabled={updateProject.isPending}
                    />
                  </div>
                )}
                {lockedByUserRetrieval && <p className="text-xs text-foreground">{t("userDefaultsApplied")}</p>}
                {(!lockedRetrieval && !lockedByUserRetrieval && !project.retrieval_strategy && systemDefaults) && (
                  <p className="text-xs text-foreground">{t("systemDefaultsApplied")}</p>
                )}
                <fieldset disabled={lockedRetrieval || lockedByUserRetrieval} className="space-y-4 disabled:opacity-60">
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
                  {!lockedRetrieval && !lockedByUserRetrieval && (
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
            <AccordionTrigger className="text-base">{t("tabs.contextAugmentation")}</AccordionTrigger>
            <AccordionContent>
              <div className="space-y-4">
                {orgHasReranking && (
                  <div className="flex items-center justify-between gap-4 rounded-md border bg-muted/40 px-3 py-2">
                    <Label htmlFor="overrides-reranking" className="text-sm cursor-pointer">{t("overrideOrgDefaults")}</Label>
                    <Switch
                      id="overrides-reranking"
                      checked={project.overrides_reranking_from_org}
                      onCheckedChange={() => handleToggleOverride("overrides_reranking_from_org", project.overrides_reranking_from_org, () => fillRerankingFrom(orgDefaults), resetReranking)}
                      disabled={updateProject.isPending}
                    />
                  </div>
                )}
                {lockedReranking && <p className="text-xs text-foreground">{t("orgDefaultsApplied")}</p>}
                {!inOrg && userHasReranking && (
                  <div className="flex items-center justify-between gap-4 rounded-md border bg-muted/40 px-3 py-2">
                    <Label htmlFor="overrides-reranking-user" className="text-sm cursor-pointer">{t("overrideUserDefaults")}</Label>
                    <Switch
                      id="overrides-reranking-user"
                      checked={project.overrides_reranking_from_user}
                      onCheckedChange={() => handleToggleOverride("overrides_reranking_from_user", project.overrides_reranking_from_user, () => fillRerankingFrom(userDefaults), resetReranking)}
                      disabled={updateProject.isPending}
                    />
                  </div>
                )}
                {lockedByUserReranking && <p className="text-xs text-foreground">{t("userDefaultsApplied")}</p>}
                {(!lockedReranking && !lockedByUserReranking && !project.reranker_backend && systemDefaults) && (
                  <p className="text-xs text-foreground">{t("systemDefaultsApplied")}</p>
                )}
                <fieldset disabled={lockedReranking || lockedByUserReranking} className="space-y-4 disabled:opacity-60">
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
                  {!lockedReranking && !lockedByUserReranking && (
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
            <AccordionTrigger className="text-base">{t("tabs.answerGeneration")}</AccordionTrigger>
            <AccordionContent>
              <div className="space-y-4">
                {orgHasChatHistory && (
                  <div className="flex items-center justify-between gap-4 rounded-md border bg-muted/40 px-3 py-2">
                    <Label htmlFor="overrides-chat-history" className="text-sm cursor-pointer">{t("overrideOrgDefaults")}</Label>
                    <Switch
                      id="overrides-chat-history"
                      checked={project.overrides_chat_history_from_org}
                      onCheckedChange={() => handleToggleOverride("overrides_chat_history_from_org", project.overrides_chat_history_from_org, () => fillHistoryFrom(orgDefaults), resetHistory)}
                      disabled={updateProject.isPending}
                    />
                  </div>
                )}
                {lockedChatHistory && <p className="text-xs text-foreground">{t("orgDefaultsApplied")}</p>}
                {!inOrg && userHasChatHistory && (
                  <div className="flex items-center justify-between gap-4 rounded-md border bg-muted/40 px-3 py-2">
                    <Label htmlFor="overrides-chat-history-user" className="text-sm cursor-pointer">{t("overrideUserDefaults")}</Label>
                    <Switch
                      id="overrides-chat-history-user"
                      checked={project.overrides_chat_history_from_user}
                      onCheckedChange={() => handleToggleOverride("overrides_chat_history_from_user", project.overrides_chat_history_from_user, () => fillHistoryFrom(userDefaults), resetHistory)}
                      disabled={updateProject.isPending}
                    />
                  </div>
                )}
                {lockedByUserChatHistory && <p className="text-xs text-foreground">{t("userDefaultsApplied")}</p>}
                {(!lockedChatHistory && !lockedByUserChatHistory && !project.chat_history_window_size && systemDefaults) && (
                  <p className="text-xs text-foreground">{t("systemDefaultsApplied")}</p>
                )}
                <fieldset disabled={lockedChatHistory || lockedByUserChatHistory} className="space-y-4 disabled:opacity-60">
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
                  {!lockedChatHistory && !lockedByUserChatHistory && (
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
