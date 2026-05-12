"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type {
  ChunkingStrategy,
  ModelCatalogResponse,
  ModelProvider,
  ProjectDefaultsConfig,
  ProjectEmbeddingBackend,
  ProjectLLMBackend,
  ProjectRerankerBackend,
  RetrievalStrategy,
  SystemDefaultsResponse,
} from "@/lib/types/api";
import { ModelSettingsFields } from "./model-settings-fields";
import { IndexingSettingsFields } from "./indexing-settings-fields";
import { RetrievalSettingsFields } from "./retrieval-settings-fields";
import { AugmentationSettingsFields } from "./augmentation-settings-fields";
import { HistorySettingsFields } from "./history-settings-fields";

type Credential = { id: string; provider: ModelProvider; masked_key: string; is_active: boolean };

type SaveCallbacks = { onSuccess?: () => void; onError?: () => void };

type ProjectDefaultsFormProps = {
  defaults: ProjectDefaultsConfig | null | undefined;
  systemDefaults: SystemDefaultsResponse | undefined;
  showReset?: boolean;
  credentials: Credential[];
  modelCatalog: ModelCatalogResponse | undefined;
  onSave: (payload: ProjectDefaultsConfig, callbacks?: SaveCallbacks) => void;
  isPending: boolean;
  idPrefix: string;
  title?: string;
  description?: string;
};

export function ProjectDefaultsForm({
  defaults,
  systemDefaults,
  showReset,
  credentials,
  modelCatalog,
  onSave,
  isPending,
  idPrefix,
  title,
  description,
}: ProjectDefaultsFormProps) {
  const tSettings = useTranslations("projects.settings");
  const tCommon = useTranslations("common");

  // Models state
  const [embeddingBackend, setEmbeddingBackend] = useState<ProjectEmbeddingBackend | "" | undefined>(undefined);
  const [embeddingModel, setEmbeddingModel] = useState<string | undefined>(undefined);
  const [embeddingCredentialId, setEmbeddingCredentialId] = useState<string | undefined>(undefined);
  const [llmBackend, setLlmBackend] = useState<ProjectLLMBackend | "" | undefined>(undefined);
  const [llmModel, setLlmModel] = useState<string | undefined>(undefined);
  const [llmCredentialId, setLlmCredentialId] = useState<string | undefined>(undefined);

  // Indexation state
  const [chunkingStrategy, setChunkingStrategy] = useState<ChunkingStrategy | null | undefined>(undefined);
  const [parentChildChunking, setParentChildChunking] = useState<boolean | undefined>(undefined);

  // Retrieval state
  const [retrievalStrategy, setRetrievalStrategy] = useState<RetrievalStrategy | null | undefined>(undefined);
  const [retrievalTopK, setRetrievalTopK] = useState<number | undefined>(undefined);
  const [retrievalMinScore, setRetrievalMinScore] = useState<number | undefined>(undefined);

  // Reranking state
  const [rerankingEnabled, setRerankingEnabled] = useState<boolean | undefined>(undefined);
  const [rerankerBackend, setRerankerBackend] = useState<ProjectRerankerBackend | undefined>(undefined);
  const [rerankerModel, setRerankerModel] = useState<string | undefined>(undefined);
  const [rerankerCandidateMultiplier, setRerankerCandidateMultiplier] = useState<number | undefined>(undefined);

  // Chat history state
  const [chatHistoryWindowSize, setChatHistoryWindowSize] = useState<number | undefined>(undefined);
  const [chatHistoryMaxChars, setChatHistoryMaxChars] = useState<number | undefined>(undefined);

  function resetLocalState() {
    setEmbeddingBackend(undefined); setEmbeddingModel(undefined); setEmbeddingCredentialId(undefined);
    setLlmBackend(undefined); setLlmModel(undefined); setLlmCredentialId(undefined);
    setChunkingStrategy(undefined); setParentChildChunking(undefined);
    setRetrievalStrategy(undefined); setRetrievalTopK(undefined); setRetrievalMinScore(undefined);
    setRerankingEnabled(undefined); setRerankerBackend(undefined); setRerankerModel(undefined); setRerankerCandidateMultiplier(undefined);
    setChatHistoryWindowSize(undefined); setChatHistoryMaxChars(undefined);
  }

  // Effective values = local state ?? persisted defaults (no system fallback for backends/models — use placeholder instead)
  const effectiveEmbeddingBackend = (embeddingBackend === undefined ? (defaults?.embedding_backend ?? "") : embeddingBackend) || "none";
  const effectiveLlmBackend = (llmBackend === undefined ? (defaults?.llm_backend ?? "") : llmBackend) || "none";
  const effectiveEmbeddingModel = (embeddingModel === undefined ? (defaults?.embedding_model ?? "") : (embeddingModel ?? "")) || "none";
  const effectiveLlmModel = (llmModel === undefined ? (defaults?.llm_model ?? "") : (llmModel ?? "")) || "none";
  const effectiveEmbeddingCredentialId = embeddingCredentialId ?? (defaults?.embedding_api_key_credential_id ?? "");
  const effectiveLlmCredentialId = llmCredentialId ?? (defaults?.llm_api_key_credential_id ?? "");

  const effectiveChunkingStrategy = chunkingStrategy === undefined
    ? (defaults?.chunking_strategy ?? "none")
    : (chunkingStrategy ?? "none");
  const effectiveParentChildChunking = parentChildChunking ?? defaults?.parent_child_chunking ?? systemDefaults?.parent_child_chunking ?? true;

  const effectiveRetrievalStrategy = retrievalStrategy === undefined
    ? (defaults?.retrieval_strategy ?? "none")
    : (retrievalStrategy ?? "none");
  const effectiveRetrievalTopK = retrievalTopK ?? defaults?.retrieval_top_k ?? systemDefaults?.retrieval_top_k ?? 8;
  const effectiveRetrievalMinScore = retrievalMinScore ?? defaults?.retrieval_min_score ?? systemDefaults?.retrieval_min_score ?? 0.3;

  const effectiveRerankingEnabled = rerankingEnabled ?? defaults?.reranking_enabled ?? false;
  const effectiveRerankerBackend = rerankerBackend ?? (defaults?.reranker_backend as ProjectRerankerBackend | undefined) ?? (systemDefaults?.reranker_backend as ProjectRerankerBackend | undefined) ?? "none";
  const effectiveRerankerModel = rerankerModel ?? defaults?.reranker_model ?? systemDefaults?.reranker_model ?? "";
  const effectiveRerankerCandidateMultiplier = rerankerCandidateMultiplier ?? defaults?.reranker_candidate_multiplier ?? systemDefaults?.reranker_candidate_multiplier ?? 3;

  const effectiveChatHistoryWindowSize = chatHistoryWindowSize ?? defaults?.chat_history_window_size ?? systemDefaults?.chat_history_window_size ?? 8;
  const effectiveChatHistoryMaxChars = chatHistoryMaxChars ?? defaults?.chat_history_max_chars ?? systemDefaults?.chat_history_max_chars ?? 4000;

  // Per-field dirty flags (effective value differs from persisted default)
  const dirtyEmbeddingBackend = effectiveEmbeddingBackend !== ((defaults?.embedding_backend ?? "") || "none");
  const dirtyEmbeddingModel = effectiveEmbeddingModel !== ((defaults?.embedding_model ?? "") || "none");
  const dirtyEmbeddingCredentialId = embeddingCredentialId !== undefined &&
    (embeddingCredentialId || null) !== (defaults?.embedding_api_key_credential_id ?? null);
  const dirtyLlmBackend = effectiveLlmBackend !== ((defaults?.llm_backend ?? "") || "none");
  const dirtyLlmModel = effectiveLlmModel !== ((defaults?.llm_model ?? "") || "none");
  const dirtyLlmCredentialId = llmCredentialId !== undefined &&
    (llmCredentialId || null) !== (defaults?.llm_api_key_credential_id ?? null);
  const dirtyChunkingStrategy = effectiveChunkingStrategy !== (defaults?.chunking_strategy ?? "none");
  const dirtyParentChildChunking = effectiveParentChildChunking !== (defaults?.parent_child_chunking ?? systemDefaults?.parent_child_chunking ?? true);
  const dirtyRetrievalStrategy = effectiveRetrievalStrategy !== (defaults?.retrieval_strategy ?? "none");
  const dirtyRetrievalTopK = effectiveRetrievalTopK !== (defaults?.retrieval_top_k ?? systemDefaults?.retrieval_top_k ?? 8);
  const dirtyRetrievalMinScore = effectiveRetrievalMinScore !== (defaults?.retrieval_min_score ?? systemDefaults?.retrieval_min_score ?? 0.3);
  const dirtyRerankingEnabled = effectiveRerankingEnabled !== (defaults?.reranking_enabled ?? false);
  const dirtyRerankerBackend = effectiveRerankerBackend !== (defaults?.reranker_backend ?? systemDefaults?.reranker_backend ?? "none");
  const dirtyRerankerModel = effectiveRerankerModel !== (defaults?.reranker_model ?? systemDefaults?.reranker_model ?? "");
  const dirtyRerankerCandidateMultiplier = effectiveRerankerCandidateMultiplier !== (defaults?.reranker_candidate_multiplier ?? systemDefaults?.reranker_candidate_multiplier ?? 3);
  const dirtyChatHistoryWindowSize = effectiveChatHistoryWindowSize !== (defaults?.chat_history_window_size ?? systemDefaults?.chat_history_window_size ?? 8);
  const dirtyChatHistoryMaxChars = effectiveChatHistoryMaxChars !== (defaults?.chat_history_max_chars ?? systemDefaults?.chat_history_max_chars ?? 4000);

  const hasModelsChanges = dirtyEmbeddingBackend || dirtyEmbeddingModel || dirtyEmbeddingCredentialId || dirtyLlmBackend || dirtyLlmModel || dirtyLlmCredentialId;
  const hasIndexingChanges = dirtyChunkingStrategy || dirtyParentChildChunking;
  const hasRetrievalChanges = dirtyRetrievalStrategy || dirtyRetrievalTopK || dirtyRetrievalMinScore;
  const hasRerankingChanges = dirtyRerankingEnabled || dirtyRerankerBackend || dirtyRerankerModel || dirtyRerankerCandidateMultiplier;
  const hasHistoryChanges = dirtyChatHistoryWindowSize || dirtyChatHistoryMaxChars;

  const hasModelsConfigured = showReset && (
    defaults?.embedding_backend != null || defaults?.llm_backend != null
  );
  const hasIndexingConfigured = showReset && (
    defaults?.chunking_strategy != null || defaults?.parent_child_chunking != null
  );
  const hasRetrievalConfigured = showReset && (
    defaults?.retrieval_strategy != null || defaults?.retrieval_top_k != null || defaults?.retrieval_min_score != null
  );
  const hasRerankingConfigured = showReset && (
    defaults?.reranking_enabled != null ||
    defaults?.reranker_backend != null ||
    defaults?.reranker_model != null ||
    defaults?.reranker_candidate_multiplier != null
  );
  const hasHistoryConfigured = showReset && (
    defaults?.chat_history_window_size != null || defaults?.chat_history_max_chars != null
  );

  const hasAnyChanges = hasModelsChanges || hasIndexingChanges || hasRetrievalChanges || hasRerankingChanges || hasHistoryChanges;
  const hasAnyConfigured = hasModelsConfigured || hasIndexingConfigured || hasRetrievalConfigured || hasRerankingConfigured || hasHistoryConfigured;

  return (
    <div className="space-y-6">
      <Card className="px-5 py-1">
        {(title || description) && (
          <div className="space-y-1 pt-4 pb-2">
            {title && <h2 className="text-lg font-medium">{title}</h2>}
            {description && <p className="text-sm text-muted-foreground">{description}</p>}
          </div>
        )}
        <Accordion type="multiple" className="w-full">

          {/* Models */}
          <AccordionItem value="models">
            <AccordionTrigger className="text-base">{tSettings("tabs.models")}</AccordionTrigger>
            <AccordionContent>
              <div className="space-y-4 pb-2">
                <ModelSettingsFields
                  idPrefix={idPrefix}
                  values={{
                    embeddingBackend: effectiveEmbeddingBackend,
                    embeddingModel: effectiveEmbeddingModel,
                    embeddingCredentialId: effectiveEmbeddingCredentialId || "none",
                    llmBackend: effectiveLlmBackend,
                    llmModel: effectiveLlmModel,
                    llmCredentialId: effectiveLlmCredentialId || "none",
                  }}
                  storedValues={defaults}
                  inheritedValues={systemDefaults}
                  fallbackValues={undefined}
                  ownerType="system"
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
                  credentials={credentials}
                />
              </div>
            </AccordionContent>
          </AccordionItem>

          {/* Indexation */}
          <AccordionItem value="indexing">
            <AccordionTrigger className="text-base">{tSettings("tabs.knowledgeIndexing")}</AccordionTrigger>
            <AccordionContent>
              <div className="space-y-4 pb-2">
                <IndexingSettingsFields
                  idPrefix={idPrefix}
                  values={{
                    chunkingStrategy: effectiveChunkingStrategy,
                    parentChildChunking: effectiveParentChildChunking,
                  }}
                  storedValues={defaults}
                  inheritedValues={systemDefaults}
                  fallbackValues={undefined}
                  ownerType="system"
                  dirty={{
                    chunkingStrategy: dirtyChunkingStrategy,
                    parentChildChunking: dirtyParentChildChunking,
                  }}
                  onChange={{
                    chunkingStrategy: setChunkingStrategy,
                    parentChildChunking: setParentChildChunking,
                  }}
                />
              </div>
            </AccordionContent>
          </AccordionItem>

          {/* Retrieval */}
          <AccordionItem value="retrieval">
            <AccordionTrigger className="text-base">{tSettings("tabs.contextRetrieval")}</AccordionTrigger>
            <AccordionContent>
              <div className="space-y-4 pb-2">
                <RetrievalSettingsFields
                  idPrefix={idPrefix}
                  values={{
                    retrievalStrategy: effectiveRetrievalStrategy,
                    retrievalTopK: effectiveRetrievalTopK,
                    retrievalMinScore: effectiveRetrievalMinScore,
                  }}
                  storedValues={defaults}
                  inheritedValues={systemDefaults}
                  fallbackValues={undefined}
                  ownerType="system"
                  dirty={{
                    retrievalStrategy: dirtyRetrievalStrategy,
                    retrievalTopK: dirtyRetrievalTopK,
                    retrievalMinScore: dirtyRetrievalMinScore,
                  }}
                  onChange={{
                    retrievalStrategy: setRetrievalStrategy,
                    retrievalTopK: (val) => setRetrievalTopK(val ?? undefined),
                    retrievalMinScore: (val) => setRetrievalMinScore(val ?? undefined),
                  }}
                />
              </div>
            </AccordionContent>
          </AccordionItem>

          {/* Reranking */}
          <AccordionItem value="augmentation">
            <AccordionTrigger className="text-base">{tSettings("tabs.contextAugmentation")}</AccordionTrigger>
            <AccordionContent>
              <div className="space-y-4 pb-2">
                <AugmentationSettingsFields
                  idPrefix={idPrefix}
                  values={{
                    rerankingEnabled: effectiveRerankingEnabled,
                    rerankerBackend: effectiveRerankerBackend,
                    rerankerModel: effectiveRerankerModel,
                    rerankerCandidateMultiplier: effectiveRerankerCandidateMultiplier,
                  }}
                  storedValues={defaults}
                  inheritedValues={systemDefaults}
                  ownerType="system"
                  dirty={{
                    rerankingEnabled: dirtyRerankingEnabled,
                    rerankerBackend: dirtyRerankerBackend,
                    rerankerModel: dirtyRerankerModel,
                    rerankerCandidateMultiplier: dirtyRerankerCandidateMultiplier,
                  }}
                  onChange={{
                    rerankingEnabled: setRerankingEnabled,
                    rerankerBackend: (val) => setRerankerBackend(val ?? undefined),
                    rerankerModel: setRerankerModel,
                    rerankerCandidateMultiplier: (val) => setRerankerCandidateMultiplier(val ?? undefined),
                  }}
                  modelCatalog={modelCatalog}
                />
              </div>
            </AccordionContent>
          </AccordionItem>

          {/* Chat history */}
          <AccordionItem value="history">
            <AccordionTrigger className="text-base">{tSettings("tabs.answerGeneration")}</AccordionTrigger>
            <AccordionContent>
              <div className="space-y-4 pb-2">
                <HistorySettingsFields
                  idPrefix={idPrefix}
                  values={{
                    chatHistoryWindowSize: effectiveChatHistoryWindowSize,
                    chatHistoryMaxChars: effectiveChatHistoryMaxChars,
                  }}
                  storedValues={defaults}
                  inheritedValues={systemDefaults}
                  ownerType="system"
                  dirty={{
                    chatHistoryWindowSize: dirtyChatHistoryWindowSize,
                    chatHistoryMaxChars: dirtyChatHistoryMaxChars,
                  }}
                  onChange={{
                    chatHistoryWindowSize: (val) => setChatHistoryWindowSize(val ?? undefined),
                    chatHistoryMaxChars: (val) => setChatHistoryMaxChars(val ?? undefined),
                  }}
                />
              </div>
            </AccordionContent>
          </AccordionItem>

        </Accordion>
        <div className="flex gap-2 px-1 pb-4 pt-2">
          <Button
            className="cursor-pointer"
            disabled={!hasAnyChanges || isPending}
            onClick={() => onSave(
              {
                embedding_backend: effectiveEmbeddingBackend === "none" ? null : (effectiveEmbeddingBackend as ProjectEmbeddingBackend),
                embedding_model: effectiveEmbeddingModel === "none" ? null : effectiveEmbeddingModel,
                embedding_api_key_credential_id: effectiveEmbeddingCredentialId || null,
                llm_backend: effectiveLlmBackend === "none" ? null : (effectiveLlmBackend as ProjectLLMBackend),
                llm_model: effectiveLlmModel === "none" ? null : effectiveLlmModel,
                llm_api_key_credential_id: effectiveLlmCredentialId || null,
                chunking_strategy: effectiveChunkingStrategy === "none" ? null : effectiveChunkingStrategy as ChunkingStrategy,
                parent_child_chunking: effectiveParentChildChunking,
                retrieval_strategy: effectiveRetrievalStrategy === "none" ? null : effectiveRetrievalStrategy as RetrievalStrategy,
                retrieval_top_k: effectiveRetrievalTopK,
                retrieval_min_score: effectiveRetrievalMinScore,
                reranking_enabled: effectiveRerankingEnabled,
                reranker_backend: effectiveRerankerBackend,
                reranker_model: effectiveRerankerModel || null,
                reranker_candidate_multiplier: effectiveRerankerCandidateMultiplier,
                chat_history_window_size: effectiveChatHistoryWindowSize,
                chat_history_max_chars: effectiveChatHistoryMaxChars,
              },
              { onSuccess: () => resetLocalState() },
            )}
          >
            <span className="relative">
              {isPending ? tCommon("saving") : tSettings("saveChanges")}
              {hasAnyChanges && !isPending && (
                <span className="absolute -top-0 -right-2 h-1.5 w-1.5 rounded-full bg-blue-500" />
              )}
            </span>
          </Button>
          {hasAnyChanges && (
            <Button
              variant="ghost"
              className="cursor-pointer"
              disabled={isPending}
              onClick={resetLocalState}
            >
              {tSettings("cancelChanges")}
            </Button>
          )}
          {hasAnyConfigured && (
            <Button
              variant="outline"
              className="cursor-pointer"
              disabled={isPending}
              onClick={() => {
                resetLocalState();
                onSave({
                  embedding_backend: null, embedding_model: null, embedding_api_key_credential_id: null,
                  llm_backend: null, llm_model: null, llm_api_key_credential_id: null,
                  chunking_strategy: null, parent_child_chunking: null,
                  retrieval_strategy: null, retrieval_top_k: null, retrieval_min_score: null,
                  reranking_enabled: null, reranker_backend: null, reranker_model: null, reranker_candidate_multiplier: null,
                  chat_history_window_size: null, chat_history_max_chars: null,
                });
              }}
            >
              {tSettings("resetToInherited")}
            </Button>
          )}
        </div>
      </Card>
    </div>
  );
}
