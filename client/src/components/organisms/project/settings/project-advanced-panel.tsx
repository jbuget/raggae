"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { useTranslations } from "next-intl";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { useModelCatalog } from "@/lib/hooks/use-model-catalog";
import { useModelCredentials } from "@/lib/hooks/use-model-credentials";
import { useOrgModelCredentials } from "@/lib/hooks/use-org-model-credentials";
import { useOrganizationProjectDefaults } from "@/lib/hooks/use-org-project-defaults";
import {
  useDeleteProject,
  useProject,
  useProjectConfiguration,
  useReindexProject,
  useUpdateProjectConfiguration,
} from "@/lib/hooks/use-projects";
import { useSystemDefaults } from "@/lib/hooks/use-system-defaults";
import { useUserProjectDefaults } from "@/lib/hooks/use-user-project-defaults";
import type {
  ChunkingStrategy,
  ProjectEmbeddingBackend,
  ProjectLLMBackend,
  ProjectRerankerBackend,
  RetrievalStrategy,
  UpdateAgentConfigurationRequest,
} from "@/lib/types/api";
import { BACKEND_LABELS } from "@/lib/constants/backends";
import { InlineAlert } from "@/components/atoms/feedback/inline-alert";
import { DirtyDot } from "@/components/atoms/feedback/dirty-dot";

export function ProjectAdvancedPanel({ projectId }: { projectId: string }) {
  const t = useTranslations("projects.settings");
  const tCommon = useTranslations("common");
  const tForm = useTranslations("projects.form");
  const router = useRouter();

  const { data: project } = useProject(projectId);
  const { data: projectConfig } = useProjectConfiguration(projectId);
  const updateProjectConfig = useUpdateProjectConfiguration(projectId);
  const reindexProject = useReindexProject(projectId);
  const deleteProject = useDeleteProject();
  const { data: modelCatalog } = useModelCatalog();
  const { data: userCredentials } = useModelCredentials();
  const { data: orgCredentials } = useOrgModelCredentials(project?.organization_id);
  const { data: orgDefaults } = useOrganizationProjectDefaults(project?.organization_id);
  const { data: userDefaults } = useUserProjectDefaults();
  const { data: systemDefaults } = useSystemDefaults();
  const credentials = project?.organization_id ? orgCredentials : userCredentials;

  const inheritedDefaults = project?.organization_id ? orgDefaults : userDefaults;

  const currentOwnerType = project?.organization_id ? "ORGANIZATION" : "USER";

  const renderInheritedValue = (val: string | number | undefined | null, defaultValue?: string | number) => {
    const normalizedVal = val === "" ? undefined : val;
    const finalVal = normalizedVal ?? defaultValue;
    const inheritsFromApp = normalizedVal === undefined || normalizedVal === null;
    const label = inheritsFromApp
      ? t("inherited.default")
      : (currentOwnerType === "USER" ? t("inherited.user") : t("inherited.organization"));
    if (finalVal === undefined || finalVal === null || finalVal === "") {
      return <span>{label} ({t("inherited.emptyValue")})</span>;
    }
    const displayVal = typeof finalVal === "string" ? (BACKEND_LABELS[finalVal] ?? finalVal) : finalVal;
    return <span>{label} ({displayVal})</span>;
  };

  // Indexation state
  const [chunkingStrategy, setChunkingStrategy] = useState<ChunkingStrategy | null | undefined>(undefined);
  const [parentChildChunking, setParentChildChunking] = useState<boolean | null | undefined>(undefined);
  const [reindexWarningOpen, setReindexWarningOpen] = useState(false);
  const [pendingIndexingData, setPendingIndexingData] = useState<UpdateAgentConfigurationRequest | null>(null);

  // Models state
  const [embeddingBackend, setEmbeddingBackend] = useState<ProjectEmbeddingBackend | "" | undefined>(undefined);
  const [embeddingModel, setEmbeddingModel] = useState<string | null | undefined>(undefined);
  const [embeddingCredentialId, setEmbeddingCredentialId] = useState<string | null | undefined>(undefined);
  const [llmBackend, setLlmBackend] = useState<ProjectLLMBackend | "" | undefined>(undefined);
  const [llmModel, setLlmModel] = useState<string | null | undefined>(undefined);
  const [llmCredentialId, setLlmCredentialId] = useState<string | null | undefined>(undefined);

  // Retrieval state
  const [retrievalStrategy, setRetrievalStrategy] = useState<RetrievalStrategy | null | undefined>(undefined);
  const [retrievalTopK, setRetrievalTopK] = useState<number | null | undefined>(undefined);
  const [retrievalMinScore, setRetrievalMinScore] = useState<number | null | undefined>(undefined);

  // Augmentation state
  const [rerankingEnabled, setRerankingEnabled] = useState<boolean | null | undefined>(undefined);
  const [rerankerBackend, setRerankerBackend] = useState<ProjectRerankerBackend | null | undefined>(undefined);
  const [rerankerModel, setRerankerModel] = useState<string | null | undefined>(undefined);
  const [rerankerCandidateMultiplier, setRerankerCandidateMultiplier] = useState<number | null | undefined>(undefined);

  // History state
  const [chatHistoryWindowSize, setChatHistoryWindowSize] = useState<number | null | undefined>(undefined);
  const [chatHistoryMaxChars, setChatHistoryMaxChars] = useState<number | null | undefined>(undefined);

  const [deleteOpen, setDeleteOpen] = useState(false);

  function resetLocalState() {
    setChunkingStrategy(undefined);
    setParentChildChunking(undefined);
    setEmbeddingBackend(undefined);
    setEmbeddingModel(undefined);
    setEmbeddingCredentialId(undefined);
    setLlmBackend(undefined);
    setLlmModel(undefined);
    setLlmCredentialId(undefined);
    setRetrievalStrategy(undefined);
    setRetrievalTopK(undefined);
    setRetrievalMinScore(undefined);
    setRerankingEnabled(undefined);
    setRerankerBackend(undefined);
    setRerankerModel(undefined);
    setRerankerCandidateMultiplier(undefined);
    setChatHistoryWindowSize(undefined);
    setChatHistoryMaxChars(undefined);
  }

  if (!project) return null;

  const isProjectReindexing = project.reindex_status === "in_progress";

  // --- Models computed values ---
  const effectiveEmbeddingBackend = (embeddingBackend === undefined
    ? (projectConfig?.embedding_backend ?? "")
    : embeddingBackend) || "none";
  const effectiveLlmBackend = (llmBackend === undefined
    ? (projectConfig?.llm_backend ?? "")
    : llmBackend) || "none";
  const effectiveEmbeddingModel = (embeddingModel === undefined
    ? (projectConfig?.embedding_model ?? "")
    : (embeddingModel ?? "")) || "none";
  const effectiveLlmModel = (llmModel === undefined
    ? (projectConfig?.llm_model ?? "")
    : (llmModel ?? "")) || "none";
  const effectiveEmbeddingCredentialId = (embeddingCredentialId === undefined
    ? (projectConfig?.embedding_api_key_credential_id ?? "")
    : (embeddingCredentialId ?? "")) || "none";
  const effectiveLlmCredentialId = (llmCredentialId === undefined
    ? (projectConfig?.llm_api_key_credential_id ?? "")
    : (llmCredentialId ?? "")) || "none";

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
  const embeddingModelOptions = (effectiveEmbeddingBackend && effectiveEmbeddingBackend !== "none") ? (modelCatalog?.embedding[effectiveEmbeddingBackend as ProjectEmbeddingBackend] ?? []) : [];
  const llmModelOptions = (effectiveLlmBackend && effectiveLlmBackend !== "none") ? (modelCatalog?.llm[effectiveLlmBackend as ProjectLLMBackend] ?? []) : [];

  const storedEmbeddingBackend = projectConfig?.embedding_backend ?? "";
  const storedLlmBackend = projectConfig?.llm_backend ?? "";
  const storedEmbeddingModel = projectConfig?.embedding_model ?? "";
  const storedLlmModel = projectConfig?.llm_model ?? "";
  const storedEmbeddingCredentialId = projectConfig?.embedding_api_key_credential_id ?? "";
  const storedLlmCredentialId = projectConfig?.llm_api_key_credential_id ?? "";

  const hasModelsChanges =
    (effectiveEmbeddingBackend === "none" ? "" : effectiveEmbeddingBackend) !== storedEmbeddingBackend ||
    (effectiveEmbeddingModel === "none" ? "" : effectiveEmbeddingModel) !== storedEmbeddingModel ||
    (effectiveLlmBackend === "none" ? "" : effectiveLlmBackend) !== storedLlmBackend ||
    (effectiveLlmModel === "none" ? "" : effectiveLlmModel) !== storedLlmModel ||
    (effectiveEmbeddingCredentialId === "none" ? "" : effectiveEmbeddingCredentialId) !== storedEmbeddingCredentialId ||
    (effectiveLlmCredentialId === "none" ? "" : effectiveLlmCredentialId) !== storedLlmCredentialId;

  const hasModelsConfigured =
    projectConfig?.embedding_backend != null ||
    projectConfig?.llm_backend != null;

  // --- Indexation computed values ---
  const effectiveChunkingStrategy = (chunkingStrategy === undefined
    ? (projectConfig?.chunking_strategy as ChunkingStrategy | null ?? null)
    : chunkingStrategy) ?? "none";
  const effectiveParentChildChunking = parentChildChunking === undefined
    ? (projectConfig?.parent_child_chunking ?? inheritedDefaults?.parent_child_chunking ?? systemDefaults?.parent_child_chunking ?? true)
    : (parentChildChunking ?? true);

  const storedChunkingStrategy = projectConfig?.chunking_strategy as ChunkingStrategy | null ?? null;
  const storedParentChildChunking = projectConfig?.parent_child_chunking ?? inheritedDefaults?.parent_child_chunking ?? systemDefaults?.parent_child_chunking ?? true;

  const hasIndexingChanges =
    (effectiveChunkingStrategy === "none" ? null : effectiveChunkingStrategy) !== storedChunkingStrategy ||
    effectiveParentChildChunking !== storedParentChildChunking;
  const isSemanticRecommended = effectiveParentChildChunking && effectiveChunkingStrategy !== "semantic";

  const hasIndexingConfigured =
    projectConfig?.chunking_strategy != null ||
    projectConfig?.parent_child_chunking != null;

  const indexingPayload: UpdateAgentConfigurationRequest = {
    chunking_strategy: effectiveChunkingStrategy === "none" ? null : effectiveChunkingStrategy as ChunkingStrategy,
    parent_child_chunking: effectiveParentChildChunking,
  };

  // --- Retrieval computed values ---
  const effectiveRetrievalStrategy = (retrievalStrategy === undefined
    ? (projectConfig?.retrieval_strategy as RetrievalStrategy | null ?? null)
    : retrievalStrategy) ?? "none";
  const effectiveRetrievalTopK = retrievalTopK === undefined
    ? (projectConfig?.retrieval_top_k ?? inheritedDefaults?.retrieval_top_k ?? systemDefaults?.retrieval_top_k ?? null)
    : retrievalTopK;
  const effectiveRetrievalMinScore = retrievalMinScore === undefined
    ? (projectConfig?.retrieval_min_score ?? inheritedDefaults?.retrieval_min_score ?? systemDefaults?.retrieval_min_score ?? null)
    : retrievalMinScore;

  const storedRetrievalStrategy = projectConfig?.retrieval_strategy as RetrievalStrategy | null ?? null;
  const storedRetrievalTopK = projectConfig?.retrieval_top_k ?? inheritedDefaults?.retrieval_top_k ?? systemDefaults?.retrieval_top_k ?? null;
  const storedRetrievalMinScore = projectConfig?.retrieval_min_score ?? inheritedDefaults?.retrieval_min_score ?? systemDefaults?.retrieval_min_score ?? null;

  const hasRetrievalChanges =
    (effectiveRetrievalStrategy === "none" ? null : effectiveRetrievalStrategy) !== storedRetrievalStrategy ||
    effectiveRetrievalTopK !== storedRetrievalTopK ||
    effectiveRetrievalMinScore !== storedRetrievalMinScore;

  const hasRetrievalConfigured =
    projectConfig?.retrieval_strategy != null ||
    projectConfig?.retrieval_top_k != null ||
    projectConfig?.retrieval_min_score != null;

  // --- Augmentation computed values ---
  const effectiveRerankingEnabled = rerankingEnabled === undefined
    ? (projectConfig?.reranking_enabled ?? inheritedDefaults?.reranking_enabled ?? false)
    : (rerankingEnabled ?? false);
  const effectiveRerankerBackend = (rerankerBackend === undefined
    ? (projectConfig?.reranker_backend as ProjectRerankerBackend | null ?? null)
    : rerankerBackend) ?? "none";
  const effectiveRerankerModel = (rerankerModel === undefined
    ? (projectConfig?.reranker_model ?? "")
    : (rerankerModel ?? "")) || "none";
  const effectiveRerankerCandidateMultiplier = rerankerCandidateMultiplier === undefined
    ? (projectConfig?.reranker_candidate_multiplier ?? inheritedDefaults?.reranker_candidate_multiplier ?? systemDefaults?.reranker_candidate_multiplier ?? null)
    : rerankerCandidateMultiplier;

  const storedRerankingEnabled = projectConfig?.reranking_enabled ?? inheritedDefaults?.reranking_enabled ?? false;
  const storedRerankerBackend = projectConfig?.reranker_backend as ProjectRerankerBackend | null ?? null;
  const storedRerankerModel = projectConfig?.reranker_model ?? "";
  const storedRerankerCandidateMultiplier = projectConfig?.reranker_candidate_multiplier ?? inheritedDefaults?.reranker_candidate_multiplier ?? systemDefaults?.reranker_candidate_multiplier ?? null;

  const rerankerModelOptions = (effectiveRerankerBackend && effectiveRerankerBackend !== "none") ? (modelCatalog?.reranker[effectiveRerankerBackend as ProjectRerankerBackend] ?? []) : [];

  const hasAugmentationChanges =
    effectiveRerankingEnabled !== storedRerankingEnabled ||
    (effectiveRerankerBackend === "none" ? null : effectiveRerankerBackend) !== storedRerankerBackend ||
    (effectiveRerankerModel === "none" ? "" : effectiveRerankerModel) !== storedRerankerModel ||
    effectiveRerankerCandidateMultiplier !== storedRerankerCandidateMultiplier;

  const hasRerankingConfigured =
    projectConfig?.reranking_enabled != null ||
    projectConfig?.reranker_backend != null;

  // --- History computed values ---
  const effectiveChatHistoryWindowSize = chatHistoryWindowSize === undefined
    ? (projectConfig?.chat_history_window_size ?? inheritedDefaults?.chat_history_window_size ?? systemDefaults?.chat_history_window_size ?? null)
    : chatHistoryWindowSize;
  const effectiveChatHistoryMaxChars = chatHistoryMaxChars === undefined
    ? (projectConfig?.chat_history_max_chars ?? inheritedDefaults?.chat_history_max_chars ?? systemDefaults?.chat_history_max_chars ?? null)
    : chatHistoryMaxChars;

  const storedChatHistoryWindowSize = projectConfig?.chat_history_window_size ?? inheritedDefaults?.chat_history_window_size ?? systemDefaults?.chat_history_window_size ?? null;
  const storedChatHistoryMaxChars = projectConfig?.chat_history_max_chars ?? inheritedDefaults?.chat_history_max_chars ?? systemDefaults?.chat_history_max_chars ?? null;

  const hasHistoryChanges =
    effectiveChatHistoryWindowSize !== storedChatHistoryWindowSize ||
    effectiveChatHistoryMaxChars !== storedChatHistoryMaxChars;

  const hasHistoryConfigured =
    projectConfig?.chat_history_window_size != null ||
    projectConfig?.chat_history_max_chars != null;

  const hasInheritedModels = inheritedDefaults?.embedding_backend != null || inheritedDefaults?.llm_backend != null;
  const hasInheritedIndexing = inheritedDefaults?.chunking_strategy != null || inheritedDefaults?.parent_child_chunking != null;
  const hasInheritedRetrieval = inheritedDefaults?.retrieval_strategy != null || inheritedDefaults?.retrieval_top_k != null || inheritedDefaults?.retrieval_min_score != null;
  const hasInheritedReranking = inheritedDefaults?.reranking_enabled != null || inheritedDefaults?.reranker_backend != null;
  const hasInheritedHistory = inheritedDefaults?.chat_history_window_size != null || inheritedDefaults?.chat_history_max_chars != null;

  const isOrgProject = project?.organization_id != null;

  const allModelsOverridden = hasInheritedModels &&
    (inheritedDefaults?.embedding_backend == null || projectConfig?.embedding_backend != null) &&
    (inheritedDefaults?.llm_backend == null || projectConfig?.llm_backend != null);
  const allIndexingOverridden = hasInheritedIndexing &&
    (inheritedDefaults?.chunking_strategy == null || projectConfig?.chunking_strategy != null) &&
    (inheritedDefaults?.parent_child_chunking == null || projectConfig?.parent_child_chunking != null);
  const allRetrievalOverridden = hasInheritedRetrieval &&
    (inheritedDefaults?.retrieval_strategy == null || projectConfig?.retrieval_strategy != null) &&
    (inheritedDefaults?.retrieval_top_k == null || projectConfig?.retrieval_top_k != null) &&
    (inheritedDefaults?.retrieval_min_score == null || projectConfig?.retrieval_min_score != null);
  const allRerankingOverridden = hasInheritedReranking &&
    (inheritedDefaults?.reranking_enabled == null || projectConfig?.reranking_enabled != null) &&
    (inheritedDefaults?.reranker_backend == null || projectConfig?.reranker_backend != null);
  const allHistoryOverridden = hasInheritedHistory &&
    (inheritedDefaults?.chat_history_window_size == null || projectConfig?.chat_history_window_size != null) &&
    (inheritedDefaults?.chat_history_max_chars == null || projectConfig?.chat_history_max_chars != null);

  function parentOverrideMessage(hasConfigured: boolean, hasInherited: boolean, allOverridden: boolean) {
    if (!hasInherited) return null;
    if (!hasConfigured) {
      return <p className="text-xs text-muted-foreground">{t(isOrgProject ? "orgDefaultsActive" : "userDefaultsActive")}</p>;
    }
    if (isOrgProject) {
      return <p className="text-xs text-muted-foreground">{t(allOverridden ? "orgOverrideAll" : "orgOverrideSome")}</p>;
    }
    return <p className="text-xs text-muted-foreground">{t(allOverridden ? "userOverrideAll" : "userOverrideSome")}</p>;
  }

  const hasAnyChanges = hasModelsChanges || hasIndexingChanges || hasRetrievalChanges || hasAugmentationChanges || hasHistoryChanges;
  const hasAnyConfigured = hasModelsConfigured || hasIndexingConfigured || hasRetrievalConfigured || hasRerankingConfigured || hasHistoryConfigured;

  const dirtyEmbeddingBackend = (effectiveEmbeddingBackend === "none" ? "" : effectiveEmbeddingBackend) !== storedEmbeddingBackend;
  const dirtyEmbeddingModel = (effectiveEmbeddingModel === "none" ? "" : effectiveEmbeddingModel) !== storedEmbeddingModel;
  const dirtyEmbeddingCredentialId = (effectiveEmbeddingCredentialId === "none" ? "" : effectiveEmbeddingCredentialId) !== storedEmbeddingCredentialId;
  const dirtyLlmBackend = (effectiveLlmBackend === "none" ? "" : effectiveLlmBackend) !== storedLlmBackend;
  const dirtyLlmModel = (effectiveLlmModel === "none" ? "" : effectiveLlmModel) !== storedLlmModel;
  const dirtyLlmCredentialId = (effectiveLlmCredentialId === "none" ? "" : effectiveLlmCredentialId) !== storedLlmCredentialId;
  const dirtyChunkingStrategy = (effectiveChunkingStrategy === "none" ? null : effectiveChunkingStrategy) !== storedChunkingStrategy;
  const dirtyParentChildChunking = effectiveParentChildChunking !== storedParentChildChunking;
  const dirtyRetrievalStrategy = (effectiveRetrievalStrategy === "none" ? null : effectiveRetrievalStrategy) !== storedRetrievalStrategy;
  const dirtyRetrievalTopK = effectiveRetrievalTopK !== storedRetrievalTopK;
  const dirtyRetrievalMinScore = effectiveRetrievalMinScore !== storedRetrievalMinScore;
  const dirtyRerankingEnabled = effectiveRerankingEnabled !== storedRerankingEnabled;
  const dirtyRerankerBackend = (effectiveRerankerBackend === "none" ? null : effectiveRerankerBackend) !== storedRerankerBackend;
  const dirtyRerankerModel = (effectiveRerankerModel === "none" ? "" : effectiveRerankerModel) !== storedRerankerModel;
  const dirtyRerankerCandidateMultiplier = effectiveRerankerCandidateMultiplier !== storedRerankerCandidateMultiplier;
  const dirtyChatHistoryWindowSize = effectiveChatHistoryWindowSize !== storedChatHistoryWindowSize;
  const dirtyChatHistoryMaxChars = effectiveChatHistoryMaxChars !== storedChatHistoryMaxChars;

  function handleSaveAll() {
    const payload: UpdateAgentConfigurationRequest = {
      embedding_backend: (effectiveEmbeddingBackend === "none" ? null : effectiveEmbeddingBackend as ProjectEmbeddingBackend),
      embedding_model: effectiveEmbeddingModel === "none" ? null : effectiveEmbeddingModel,
      embedding_api_key_credential_id: effectiveEmbeddingCredentialId === "none" ? null : effectiveEmbeddingCredentialId,
      llm_backend: (effectiveLlmBackend === "none" ? null : effectiveLlmBackend as ProjectLLMBackend),
      llm_model: effectiveLlmModel === "none" ? null : effectiveLlmModel,
      llm_api_key_credential_id: effectiveLlmCredentialId === "none" ? null : effectiveLlmCredentialId,
      chunking_strategy: effectiveChunkingStrategy === "none" ? null : effectiveChunkingStrategy as ChunkingStrategy,
      parent_child_chunking: effectiveParentChildChunking,
      retrieval_strategy: effectiveRetrievalStrategy === "none" ? null : effectiveRetrievalStrategy as RetrievalStrategy,
      retrieval_top_k: effectiveRetrievalTopK,
      retrieval_min_score: effectiveRetrievalMinScore,
      reranking_enabled: effectiveRerankingEnabled,
      reranker_backend: effectiveRerankerBackend === "none" ? null : effectiveRerankerBackend as ProjectRerankerBackend,
      reranker_model: effectiveRerankerModel === "none" ? null : effectiveRerankerModel,
      reranker_candidate_multiplier: effectiveRerankerCandidateMultiplier,
      chat_history_window_size: effectiveChatHistoryWindowSize,
      chat_history_max_chars: effectiveChatHistoryMaxChars,
    };
    const parentChildChanged = effectiveParentChildChunking !== storedParentChildChunking;
    if (parentChildChanged) {
      setPendingIndexingData(payload);
      setReindexWarningOpen(true);
      return;
    }
    updateProjectConfig.mutate(payload, {
      onSuccess: () => { resetLocalState(); toast.success(t("updateSuccess")); },
      onError: () => toast.error(t("updateError")),
    });
  }

  return (
    <div className="space-y-6">

      {/* Settings card */}
      <Card className="px-5 py-1">
        <div className="space-y-1 pt-4 pb-2">
          <h2 className="text-lg font-medium">{t("advanced.title")}</h2>
          <p className="text-sm text-muted-foreground">{t("advanced.description")}</p>
        </div>

        <Accordion type="multiple" className="w-full">

          {/* Models */}
          <AccordionItem value="models">
            <AccordionTrigger className="text-base">{t("tabs.models")}</AccordionTrigger>
            <AccordionContent>
              <div className="space-y-4">
                {parentOverrideMessage(hasModelsConfigured, hasInheritedModels, allModelsOverridden)}
                {(!hasModelsConfigured && !hasInheritedModels && systemDefaults && !isOrgProject) && (
                  <p className="text-xs text-foreground">{t("systemDefaultsApplied")}</p>
                )}
                <div className="space-y-1">
                  <p className="text-sm font-medium">{t("models.embeddingTitle")}</p>
                  <p className="text-sm text-muted-foreground">{t("models.embeddingDescription")}</p>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="embeddingBackend">{t("models.embeddingBackendLabel")}<DirtyDot dirty={dirtyEmbeddingBackend} /></Label>
                  <Select
                    value={effectiveEmbeddingBackend}
                    onValueChange={(val) => {
                      setEmbeddingBackend((val === "none" ? "" : val) as ProjectEmbeddingBackend | "");
                      setEmbeddingModel("");
                      setEmbeddingCredentialId("");
                    }}
                  >
                    <SelectTrigger id="embeddingBackend">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="none">
                        {renderInheritedValue(inheritedDefaults?.embedding_backend, systemDefaults?.embedding_backend)}
                      </SelectItem>
                      <SelectItem value="openai">{BACKEND_LABELS.openai}</SelectItem>
                      <SelectItem value="gemini">{BACKEND_LABELS.gemini}</SelectItem>
                      <SelectItem value="ollama">{BACKEND_LABELS.ollama}</SelectItem>
                      <SelectItem value="inmemory">{BACKEND_LABELS.inmemory}</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                {effectiveEmbeddingBackend !== "none" ? (
                  <>
                    <div className="space-y-2">
                      <Label htmlFor="embeddingCredentialId">{t("models.embeddingApiKeyLabel")}<DirtyDot dirty={dirtyEmbeddingCredentialId} /></Label>
                      <Select
                        value={effectiveEmbeddingCredentialId}
                        onValueChange={setEmbeddingCredentialId}
                        disabled={!embeddingProviderForHints}
                      >
                        <SelectTrigger id="embeddingCredentialId">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="none">
                            {embeddingProviderForHints ? t("models.noSelection") : t("models.selectEmbeddingFirst")}
                          </SelectItem>
                          {embeddingCredentialOptions.map((item) => (
                            <SelectItem key={item.id} value={item.id}>
                              {item.masked_key}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="embeddingModel">{t("models.embeddingModelLabel")}<DirtyDot dirty={dirtyEmbeddingModel} /></Label>
                      <Select
                        value={embeddingModelOptions.some(m => m.id === effectiveEmbeddingModel) ? effectiveEmbeddingModel : "none"}
                        onValueChange={setEmbeddingModel}
                      >
                        <SelectTrigger id="embeddingModel">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="none">{t("models.selectModel")}</SelectItem>
                          {embeddingModelOptions.map((m) => (
                            <SelectItem key={m.id} value={m.id}>
                              {m.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </>
                ) : null}
                <hr className="border-border" />
                <div className="space-y-1">
                  <p className="text-sm font-medium">{t("models.llmTitle")}</p>
                  <p className="text-sm text-muted-foreground">{t("models.llmDescription")}</p>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="llmBackend">{t("models.llmBackendLabel")}<DirtyDot dirty={dirtyLlmBackend} /></Label>
                  <Select
                    value={effectiveLlmBackend}
                    onValueChange={(val) => {
                      setLlmBackend((val === "none" ? "" : val) as ProjectLLMBackend | "");
                      setLlmModel("");
                      setLlmCredentialId("");
                    }}
                  >
                    <SelectTrigger id="llmBackend">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="none">
                        {renderInheritedValue(inheritedDefaults?.llm_backend, systemDefaults?.llm_backend)}
                      </SelectItem>
                      <SelectItem value="openai">{BACKEND_LABELS.openai}</SelectItem>
                      <SelectItem value="gemini">{BACKEND_LABELS.gemini}</SelectItem>
                      <SelectItem value="anthropic">{BACKEND_LABELS.anthropic}</SelectItem>
                      <SelectItem value="ollama">{BACKEND_LABELS.ollama}</SelectItem>
                      <SelectItem value="inmemory">{BACKEND_LABELS.inmemory}</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                {effectiveLlmBackend !== "none" ? (
                  <>
                    <div className="space-y-2">
                      <Label htmlFor="llmCredentialId">{t("models.llmApiKeyLabel")}<DirtyDot dirty={dirtyLlmCredentialId} /></Label>
                      <Select
                        value={effectiveLlmCredentialId}
                        onValueChange={setLlmCredentialId}
                        disabled={!llmProviderForHints}
                      >
                        <SelectTrigger id="llmCredentialId">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="none">
                            {llmProviderForHints ? t("models.noSelection") : t("models.selectLlmFirst")}
                          </SelectItem>
                          {llmCredentialOptions.map((item) => (
                            <SelectItem key={item.id} value={item.id}>
                              {item.masked_key}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="llmModel">{t("models.llmModelLabel")}<DirtyDot dirty={dirtyLlmModel} /></Label>
                      <Select
                        value={llmModelOptions.some(m => m.id === effectiveLlmModel) ? effectiveLlmModel : "none"}
                        onValueChange={setLlmModel}
                      >
                        <SelectTrigger id="llmModel">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="none">{t("models.selectModel")}</SelectItem>
                          {llmModelOptions.map((m) => (
                            <SelectItem key={m.id} value={m.id}>
                              {m.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </>
                ) : null}
              </div>
            </AccordionContent>
          </AccordionItem>

          {/* Indexation */}
          <AccordionItem value="indexing">
            <AccordionTrigger className="text-base">{t("tabs.knowledgeIndexing")}</AccordionTrigger>
            <AccordionContent>
              <div className="space-y-4">
                {isProjectReindexing && (
                  <InlineAlert variant="loading">
                    {t("reindexingWarning", { progress: project.reindex_progress, total: project.reindex_total })}
                  </InlineAlert>
                )}
                {parentOverrideMessage(hasIndexingConfigured, hasInheritedIndexing, allIndexingOverridden)}
                {(!hasIndexingConfigured && !hasInheritedIndexing && systemDefaults && !isOrgProject) && (
                  <p className="text-xs text-foreground">{t("systemDefaultsApplied")}</p>
                )}
                <div className="space-y-2">
                  <Label htmlFor="chunkingStrategy">{t("knowledgeIndexing.chunkingLabel")}<DirtyDot dirty={dirtyChunkingStrategy} /></Label>
                  <Select
                    value={effectiveChunkingStrategy}
                    onValueChange={(val) => setChunkingStrategy(val === "none" ? null : val as ChunkingStrategy)}
                  >
                    <SelectTrigger id="chunkingStrategy">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="none">
                        {renderInheritedValue(inheritedDefaults?.chunking_strategy, systemDefaults?.chunking_strategy)}
                      </SelectItem>
                      <SelectItem value="auto">{tForm("chunkingAuto")}</SelectItem>
                      <SelectItem value="fixed_window">{tForm("chunkingFixed")}</SelectItem>
                      <SelectItem value="paragraph">{tForm("chunkingParagraph")}</SelectItem>
                      <SelectItem value="heading_section">{tForm("chunkingHeading")}</SelectItem>
                      <SelectItem value="semantic">{tForm("chunkingSemantic")}</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex items-center gap-2">
                  <Switch id="parentChildChunking" checked={effectiveParentChildChunking} onCheckedChange={setParentChildChunking} />
                  <Label htmlFor="parentChildChunking">{t("knowledgeIndexing.parentChildLabel")}<DirtyDot dirty={dirtyParentChildChunking} /></Label>
                </div>
                <p className="text-xs text-muted-foreground">{t("knowledgeIndexing.parentChildRecommendation")}</p>
                {isSemanticRecommended && <InlineAlert>{t("knowledgeIndexing.parentChildWarning")}</InlineAlert>}
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
                {parentOverrideMessage(hasRetrievalConfigured, hasInheritedRetrieval, allRetrievalOverridden)}
                {(!hasRetrievalConfigured && !hasInheritedRetrieval && systemDefaults && !isOrgProject) && (
                  <p className="text-xs text-foreground">{t("systemDefaultsApplied")}</p>
                )}
                <p className="text-sm text-muted-foreground">{t("contextRetrieval.description")}</p>
                <div className="space-y-2">
                  <Label htmlFor="retrievalStrategy">{t("contextRetrieval.searchTypeLabel")}<DirtyDot dirty={dirtyRetrievalStrategy} /></Label>
                  <Select
                    value={effectiveRetrievalStrategy}
                    onValueChange={(val) => setRetrievalStrategy(val === "none" ? null : val as RetrievalStrategy)}
                  >
                    <SelectTrigger id="retrievalStrategy">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="none">
                        {renderInheritedValue(inheritedDefaults?.retrieval_strategy, systemDefaults?.retrieval_strategy ?? "hybrid")}
                      </SelectItem>
                      <SelectItem value="hybrid">{t("contextRetrieval.hybrid")}</SelectItem>
                      <SelectItem value="vector">{t("contextRetrieval.vector")}</SelectItem>
                      <SelectItem value="fulltext">{t("contextRetrieval.fulltext")}</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="retrievalTopK">{t("contextRetrieval.topKLabel")}<DirtyDot dirty={dirtyRetrievalTopK} /></Label>
                  <Input id="retrievalTopK" type="number" min={1} max={40}
                    value={effectiveRetrievalTopK ?? ""}
                    onChange={(e) => { const v = Number.parseInt(e.target.value, 10); setRetrievalTopK(Number.isNaN(v) ? null : Math.max(1, Math.min(40, v))); }}
                  />
                  <p className="text-xs text-muted-foreground">{t("contextRetrieval.topKNote")}</p>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="retrievalMinScore">{t("contextRetrieval.minScoreLabel")}<DirtyDot dirty={dirtyRetrievalMinScore} /></Label>
                  <Input id="retrievalMinScore" type="number" min={0} max={1} step={0.05}
                    value={effectiveRetrievalMinScore ?? ""}
                    onChange={(e) => { const v = Number.parseFloat(e.target.value); setRetrievalMinScore(Number.isNaN(v) ? null : Math.round(Math.max(0, Math.min(1, v)) * 100) / 100); }}
                  />
                  <p className="text-xs text-muted-foreground">{t("contextRetrieval.minScoreNote")}</p>
                </div>
              </div>
            </AccordionContent>
          </AccordionItem>

          {/* Augmentation */}
          <AccordionItem value="augmentation">
            <AccordionTrigger className="text-base">{t("tabs.contextAugmentation")}</AccordionTrigger>
            <AccordionContent>
              <div className="space-y-4">
                {parentOverrideMessage(hasRerankingConfigured, hasInheritedReranking, allRerankingOverridden)}
                {(!hasRerankingConfigured && !hasInheritedReranking && systemDefaults && !isOrgProject) && (
                  <p className="text-xs text-foreground">{t("systemDefaultsApplied")}</p>
                )}
                <div className="flex items-center gap-2">
                  <Switch id="rerankingEnabled" checked={effectiveRerankingEnabled} onCheckedChange={setRerankingEnabled} />
                  <Label htmlFor="rerankingEnabled">{t("contextAugmentation.rerankingLabel")}<DirtyDot dirty={dirtyRerankingEnabled} /></Label>
                </div>
                {effectiveRerankingEnabled && (
                  <>
                    <div className="space-y-2">
                      <Label htmlFor="rerankerBackend">{t("contextAugmentation.rerankerBackendLabel")}<DirtyDot dirty={dirtyRerankerBackend} /></Label>
                      <Select
                        value={effectiveRerankerBackend}
                        onValueChange={(val) => {
                          setRerankerBackend(val === "none" ? null : val as ProjectRerankerBackend);
                          setRerankerModel("");
                        }}
                      >
                        <SelectTrigger id="rerankerBackend">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="none">{t("contextAugmentation.rerankerNone")}</SelectItem>
                          <SelectItem value="cross_encoder">{t("contextAugmentation.rerankerCrossEncoder")}</SelectItem>
                          <SelectItem value="inmemory">{t("contextAugmentation.rerankerInMemory")}</SelectItem>
                          <SelectItem value="mmr">{t("contextAugmentation.rerankerMmr")}</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="rerankerModel">{t("contextAugmentation.rerankerModelLabel")}<DirtyDot dirty={dirtyRerankerModel} /></Label>
                      <Select
                        value={rerankerModelOptions.some(m => m.id === effectiveRerankerModel) ? effectiveRerankerModel : "none"}
                        onValueChange={setRerankerModel}
                        disabled={effectiveRerankerBackend === "none" || effectiveRerankerBackend === null}
                      >
                        <SelectTrigger id="rerankerModel">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="none">
                            {effectiveRerankerBackend === "none" || effectiveRerankerBackend === null ? t("contextAugmentation.selectRerankerBackend") : t("contextAugmentation.selectModel")}
                          </SelectItem>
                          {rerankerModelOptions.map((m) => (
                            <SelectItem key={m.id} value={m.id}>
                              {m.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="rerankerCandidateMultiplier">{t("contextAugmentation.candidateMultiplierLabel")}<DirtyDot dirty={dirtyRerankerCandidateMultiplier} /></Label>
                      <Input id="rerankerCandidateMultiplier" type="number" min={1} max={10}
                        value={effectiveRerankerCandidateMultiplier ?? ""}
                        onChange={(e) => { const v = Number.parseInt(e.target.value, 10); setRerankerCandidateMultiplier(Number.isNaN(v) ? null : Math.max(1, Math.min(10, v))); }}
                      />
                      <p className="text-xs text-muted-foreground">{t("contextAugmentation.candidateMultiplierNote")}</p>
                    </div>
                  </>
                )}
              </div>
            </AccordionContent>
          </AccordionItem>

          {/* Chat history */}
          <AccordionItem value="history">
            <AccordionTrigger className="text-base">{t("tabs.answerGeneration")}</AccordionTrigger>
            <AccordionContent>
              <div className="space-y-4">
                {parentOverrideMessage(hasHistoryConfigured, hasInheritedHistory, allHistoryOverridden)}
                {(!hasHistoryConfigured && !hasInheritedHistory && systemDefaults && !isOrgProject) && (
                  <p className="text-xs text-foreground">{t("systemDefaultsApplied")}</p>
                )}
                <div className="space-y-2">
                  <Label htmlFor="chatHistoryWindowSize">{t("answerGeneration.chatHistoryWindowLabel")}<DirtyDot dirty={dirtyChatHistoryWindowSize} /></Label>
                  <Input id="chatHistoryWindowSize" type="number" min={1} max={40}
                    value={effectiveChatHistoryWindowSize ?? ""}
                    onChange={(e) => { const v = Number.parseInt(e.target.value, 10); setChatHistoryWindowSize(Number.isNaN(v) ? null : Math.max(1, Math.min(40, v))); }}
                  />
                  <p className="text-xs text-muted-foreground">{t("answerGeneration.chatHistoryWindowNote")}</p>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="chatHistoryMaxChars">{t("answerGeneration.chatHistoryMaxCharsLabel")}<DirtyDot dirty={dirtyChatHistoryMaxChars} /></Label>
                  <Input id="chatHistoryMaxChars" type="number" min={128} max={16000}
                    value={effectiveChatHistoryMaxChars ?? ""}
                    onChange={(e) => { const v = Number.parseInt(e.target.value, 10); setChatHistoryMaxChars(Number.isNaN(v) ? null : Math.max(128, Math.min(16000, v))); }}
                  />
                  <p className="text-xs text-muted-foreground">{t("answerGeneration.chatHistoryMaxCharsNote")}</p>
                </div>
              </div>
            </AccordionContent>
          </AccordionItem>

        </Accordion>
        <div className="flex gap-2 px-1 pb-4 pt-2">
          <Button
            className="cursor-pointer"
            disabled={!hasAnyChanges || updateProjectConfig.isPending}
            onClick={handleSaveAll}
          >
            {updateProjectConfig.isPending ? tCommon("saving") : t("saveChanges")}
          </Button>
          {hasAnyConfigured && (
            <Button
              variant="outline"
              className="cursor-pointer"
              disabled={updateProjectConfig.isPending}
              onClick={() => updateProjectConfig.mutate(
                {
                  embedding_backend: null, embedding_model: null, embedding_api_key_credential_id: null,
                  llm_backend: null, llm_model: null, llm_api_key_credential_id: null,
                  chunking_strategy: null, parent_child_chunking: null,
                  retrieval_strategy: null, retrieval_top_k: null, retrieval_min_score: null,
                  reranking_enabled: null, reranker_backend: null, reranker_model: null, reranker_candidate_multiplier: null,
                  chat_history_window_size: null, chat_history_max_chars: null,
                },
                { onSuccess: () => { resetLocalState(); toast.success(t("updateSuccess")); }, onError: () => toast.error(t("updateError")) },
              )}
            >
              {t(isOrgProject ? "resetToOrg" : "resetToUser")}
            </Button>
          )}
        </div>
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
              updateProjectConfig.mutate(pendingIndexingData, {
                onSuccess: () => { resetLocalState(); toast.success(t("updateSuccess")); },
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
