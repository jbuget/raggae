"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { useTranslations } from "next-intl";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
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
import { InlineAlert } from "@/components/atoms/feedback/inline-alert";
import { ModelSettingsFields } from "@/components/molecules/settings/model-settings-fields";
import { IndexingSettingsFields } from "@/components/molecules/settings/indexing-settings-fields";
import { RetrievalSettingsFields } from "@/components/molecules/settings/retrieval-settings-fields";
import { AugmentationSettingsFields } from "@/components/molecules/settings/augmentation-settings-fields";
import { HistorySettingsFields } from "@/components/molecules/settings/history-settings-fields";

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

  const isOrgProject = project?.organization_id != null;
  const ownerType = isOrgProject ? "org" as const : "user" as const;

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
                <ModelSettingsFields
                  idPrefix={projectId}
                  values={{
                    embeddingBackend: effectiveEmbeddingBackend,
                    embeddingModel: effectiveEmbeddingModel,
                    embeddingCredentialId: effectiveEmbeddingCredentialId,
                    llmBackend: effectiveLlmBackend,
                    llmModel: effectiveLlmModel,
                    llmCredentialId: effectiveLlmCredentialId,
                  }}
                  storedValues={projectConfig}
                  inheritedValues={inheritedDefaults}
                  fallbackValues={systemDefaults}
                  ownerType={ownerType}
                  dirty={{
                    embeddingBackend: dirtyEmbeddingBackend,
                    embeddingModel: dirtyEmbeddingModel,
                    embeddingCredentialId: dirtyEmbeddingCredentialId,
                    llmBackend: dirtyLlmBackend,
                    llmModel: dirtyLlmModel,
                    llmCredentialId: dirtyLlmCredentialId,
                  }}
                  onChange={{
                    embeddingBackend: (val) => setEmbeddingBackend((val === "none" ? "" : val) as ProjectEmbeddingBackend | ""),
                    embeddingModel: (val) => setEmbeddingModel(val === "none" ? "" : val),
                    embeddingCredentialId: (val) => setEmbeddingCredentialId(val === "none" ? "" : val),
                    llmBackend: (val) => setLlmBackend((val === "none" ? "" : val) as ProjectLLMBackend | ""),
                    llmModel: (val) => setLlmModel(val === "none" ? "" : val),
                    llmCredentialId: (val) => setLlmCredentialId(val === "none" ? "" : val),
                  }}
                  modelCatalog={modelCatalog}
                  credentials={credentials ?? []}
                />
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
                <IndexingSettingsFields
                  idPrefix={projectId}
                  values={{
                    chunkingStrategy: effectiveChunkingStrategy,
                    parentChildChunking: effectiveParentChildChunking,
                  }}
                  storedValues={projectConfig}
                  inheritedValues={inheritedDefaults}
                  fallbackValues={systemDefaults}
                  ownerType={ownerType}
                  dirty={{
                    chunkingStrategy: dirtyChunkingStrategy,
                    parentChildChunking: dirtyParentChildChunking,
                  }}
                  onChange={{
                    chunkingStrategy: setChunkingStrategy,
                    parentChildChunking: setParentChildChunking,
                  }}
                />
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
                <RetrievalSettingsFields
                  idPrefix={projectId}
                  values={{
                    retrievalStrategy: effectiveRetrievalStrategy,
                    retrievalTopK: effectiveRetrievalTopK,
                    retrievalMinScore: effectiveRetrievalMinScore,
                  }}
                  storedValues={projectConfig}
                  inheritedValues={inheritedDefaults}
                  fallbackValues={systemDefaults}
                  ownerType={ownerType}
                  dirty={{
                    retrievalStrategy: dirtyRetrievalStrategy,
                    retrievalTopK: dirtyRetrievalTopK,
                    retrievalMinScore: dirtyRetrievalMinScore,
                  }}
                  onChange={{
                    retrievalStrategy: setRetrievalStrategy,
                    retrievalTopK: setRetrievalTopK,
                    retrievalMinScore: setRetrievalMinScore,
                  }}
                />
              </div>
            </AccordionContent>
          </AccordionItem>

          {/* Augmentation */}
          <AccordionItem value="augmentation">
            <AccordionTrigger className="text-base">{t("tabs.contextAugmentation")}</AccordionTrigger>
            <AccordionContent>
              <div className="space-y-4">
                <AugmentationSettingsFields
                  idPrefix={projectId}
                  values={{
                    rerankingEnabled: effectiveRerankingEnabled,
                    rerankerBackend: effectiveRerankerBackend,
                    rerankerModel: effectiveRerankerModel,
                    rerankerCandidateMultiplier: effectiveRerankerCandidateMultiplier,
                  }}
                  storedValues={projectConfig}
                  inheritedValues={inheritedDefaults}
                  ownerType={ownerType}
                  dirty={{
                    rerankingEnabled: dirtyRerankingEnabled,
                    rerankerBackend: dirtyRerankerBackend,
                    rerankerModel: dirtyRerankerModel,
                    rerankerCandidateMultiplier: dirtyRerankerCandidateMultiplier,
                  }}
                  onChange={{
                    rerankingEnabled: (val) => setRerankingEnabled(val),
                    rerankerBackend: setRerankerBackend,
                    rerankerModel: (val) => setRerankerModel(val),
                    rerankerCandidateMultiplier: setRerankerCandidateMultiplier,
                  }}
                  modelCatalog={modelCatalog}
                />
              </div>
            </AccordionContent>
          </AccordionItem>

          {/* Chat history */}
          <AccordionItem value="history">
            <AccordionTrigger className="text-base">{t("tabs.answerGeneration")}</AccordionTrigger>
            <AccordionContent>
              <div className="space-y-4">
                <HistorySettingsFields
                  idPrefix={projectId}
                  values={{
                    chatHistoryWindowSize: effectiveChatHistoryWindowSize,
                    chatHistoryMaxChars: effectiveChatHistoryMaxChars,
                  }}
                  storedValues={projectConfig}
                  inheritedValues={inheritedDefaults}
                  ownerType={ownerType}
                  dirty={{
                    chatHistoryWindowSize: dirtyChatHistoryWindowSize,
                    chatHistoryMaxChars: dirtyChatHistoryMaxChars,
                  }}
                  onChange={{
                    chatHistoryWindowSize: setChatHistoryWindowSize,
                    chatHistoryMaxChars: setChatHistoryMaxChars,
                  }}
                />
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
          {hasAnyChanges && (
            <Button
              variant="ghost"
              className="cursor-pointer"
              disabled={updateProjectConfig.isPending}
              onClick={resetLocalState}
            >
              {t("cancelChanges")}
            </Button>
          )}
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
