"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
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
import { BACKEND_LABELS } from "@/lib/constants/backends";
import { DirtyDot } from "@/components/atoms/feedback/dirty-dot";

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
  const tForm = useTranslations("projects.form");
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

  function renderDefaultPlaceholder(val: string | null | undefined): string | undefined {
    if (!val) return undefined;
    return `Par défaut (${BACKEND_LABELS[val] ?? val})`;
  }

  const activeCredentials = credentials.filter((c) => c.is_active);
  const credentialsByProvider = activeCredentials.reduce<Record<string, Array<{ id: string; masked_key: string }>>>(
    (acc, c) => { (acc[c.provider] ??= []).push({ id: c.id, masked_key: c.masked_key }); return acc; },
    {},
  );
  const embeddingProviderForHints = effectiveEmbeddingBackend === "openai" || effectiveEmbeddingBackend === "gemini" ? effectiveEmbeddingBackend : null;
  const llmProviderForHints = effectiveLlmBackend === "openai" || effectiveLlmBackend === "gemini" || effectiveLlmBackend === "anthropic" ? effectiveLlmBackend : null;
  const embeddingCredentialOptions = embeddingProviderForHints ? (credentialsByProvider[embeddingProviderForHints] ?? []) : [];
  const llmCredentialOptions = llmProviderForHints ? (credentialsByProvider[llmProviderForHints] ?? []) : [];
  const embeddingModelOptions = effectiveEmbeddingBackend !== "none" ? (modelCatalog?.embedding[effectiveEmbeddingBackend as ProjectEmbeddingBackend] ?? []) : [];
  const llmModelOptions = effectiveLlmBackend !== "none" ? (modelCatalog?.llm[effectiveLlmBackend as ProjectLLMBackend] ?? []) : [];

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
  const rerankerModelOptions = modelCatalog?.reranker[effectiveRerankerBackend as ProjectRerankerBackend] ?? [];

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
    defaults?.reranking_enabled != null || defaults?.reranker_backend != null
  );
  const hasHistoryConfigured = showReset && (
    defaults?.chat_history_window_size != null || defaults?.chat_history_max_chars != null
  );

  // Base payload from persisted defaults — prevents a section save from overwriting other sections
  function buildBasePayload(): ProjectDefaultsConfig {
    return {
      embedding_backend: (defaults?.embedding_backend as ProjectEmbeddingBackend) || null,
      embedding_model: defaults?.embedding_model ?? null,
      embedding_api_key_credential_id: defaults?.embedding_api_key_credential_id ?? null,
      llm_backend: (defaults?.llm_backend as ProjectLLMBackend) || null,
      llm_model: defaults?.llm_model ?? null,
      llm_api_key_credential_id: defaults?.llm_api_key_credential_id ?? null,
      chunking_strategy: defaults?.chunking_strategy ?? null,
      parent_child_chunking: defaults?.parent_child_chunking ?? null,
      retrieval_strategy: defaults?.retrieval_strategy ?? null,
      retrieval_top_k: defaults?.retrieval_top_k ?? null,
      retrieval_min_score: defaults?.retrieval_min_score ?? null,
      reranking_enabled: defaults?.reranking_enabled ?? null,
      reranker_backend: defaults?.reranker_backend ?? null,
      reranker_model: defaults?.reranker_model ?? null,
      reranker_candidate_multiplier: defaults?.reranker_candidate_multiplier ?? null,
      chat_history_window_size: defaults?.chat_history_window_size ?? null,
      chat_history_max_chars: defaults?.chat_history_max_chars ?? null,
    };
  }

  const hasAnyChanges = hasModelsChanges || hasIndexingChanges || hasRetrievalChanges || hasRerankingChanges || hasHistoryChanges;
  const hasAnyConfigured = hasModelsConfigured || hasIndexingConfigured || hasRetrievalConfigured || hasRerankingConfigured || hasHistoryConfigured;

  const id = (field: string) => `${idPrefix}-${field}`;

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
                <div className="space-y-1">
                  <p className="text-sm font-medium">{tSettings("models.embeddingTitle")}</p>
                  <p className="text-sm text-muted-foreground">{tSettings("models.embeddingDescription")}</p>
                </div>
                <div className="space-y-2">
                  <Label htmlFor={id("embeddingBackend")}>{tSettings("models.embeddingBackendLabel")}<DirtyDot dirty={dirtyEmbeddingBackend} /></Label>
                  <Select
                    value={effectiveEmbeddingBackend}
                    onValueChange={(val) => {
                      setEmbeddingBackend((val === "none" ? "" : val) as ProjectEmbeddingBackend | "");
                      setEmbeddingModel("");
                      setEmbeddingCredentialId("");
                    }}
                  >
                    <SelectTrigger id={id("embeddingBackend")}>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="none">{renderDefaultPlaceholder(systemDefaults?.embedding_backend) ?? "—"}</SelectItem>
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
                      <Label htmlFor={id("embeddingCredentialId")}>{tSettings("models.embeddingApiKeyLabel")}<DirtyDot dirty={dirtyEmbeddingCredentialId} /></Label>
                      <Select
                        value={effectiveEmbeddingCredentialId || "none"}
                        onValueChange={(val) => setEmbeddingCredentialId(val === "none" ? "" : val)}
                        disabled={!embeddingProviderForHints}
                      >
                        <SelectTrigger id={id("embeddingCredentialId")}>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="none">
                            {embeddingProviderForHints ? tSettings("models.noSelection") : tSettings("models.selectEmbeddingFirst")}
                          </SelectItem>
                          {embeddingCredentialOptions.map((item) => (
                            <SelectItem key={item.id} value={item.id}>{item.masked_key}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor={id("embeddingModel")}>{tSettings("models.embeddingModelLabel")}<DirtyDot dirty={dirtyEmbeddingModel} /></Label>
                      <Select
                        value={embeddingModelOptions.some(m => m.id === effectiveEmbeddingModel) ? effectiveEmbeddingModel : "none"}
                        onValueChange={(val) => setEmbeddingModel(val === "none" ? "" : val)}
                      >
                        <SelectTrigger id={id("embeddingModel")}>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="none">{tSettings("models.selectModel")}</SelectItem>
                          {embeddingModelOptions.map((m) => (
                            <SelectItem key={m.id} value={m.id}>{m.label}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </>
                ) : null}
                <hr className="border-border" />
                <p className="text-sm font-medium">{tSettings("models.llmTitle")}</p>
                <p className="text-sm text-muted-foreground">{tSettings("models.llmDescription")}</p>
                <div className="space-y-2">
                  <Label htmlFor={id("llmBackend")}>{tSettings("models.llmBackendLabel")}<DirtyDot dirty={dirtyLlmBackend} /></Label>
                  <Select
                    value={effectiveLlmBackend}
                    onValueChange={(val) => {
                      setLlmBackend((val === "none" ? "" : val) as ProjectLLMBackend | "");
                      setLlmModel("");
                      setLlmCredentialId("");
                    }}
                  >
                    <SelectTrigger id={id("llmBackend")}>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="none">{renderDefaultPlaceholder(systemDefaults?.llm_backend) ?? "—"}</SelectItem>
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
                      <Label htmlFor={id("llmCredentialId")}>{tSettings("models.llmApiKeyLabel")}<DirtyDot dirty={dirtyLlmCredentialId} /></Label>
                      <Select
                        value={effectiveLlmCredentialId || "none"}
                        onValueChange={(val) => setLlmCredentialId(val === "none" ? "" : val)}
                        disabled={!llmProviderForHints}
                      >
                        <SelectTrigger id={id("llmCredentialId")}>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="none">
                            {llmProviderForHints ? tSettings("models.noSelection") : tSettings("models.selectLlmFirst")}
                          </SelectItem>
                          {llmCredentialOptions.map((item) => (
                            <SelectItem key={item.id} value={item.id}>{item.masked_key}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor={id("llmModel")}>{tSettings("models.llmModelLabel")}<DirtyDot dirty={dirtyLlmModel} /></Label>
                      <Select
                        value={llmModelOptions.some(m => m.id === effectiveLlmModel) ? effectiveLlmModel : "none"}
                        onValueChange={(val) => setLlmModel(val === "none" ? "" : val)}
                      >
                        <SelectTrigger id={id("llmModel")}>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="none">{tSettings("models.selectModel")}</SelectItem>
                          {llmModelOptions.map((m) => (
                            <SelectItem key={m.id} value={m.id}>{m.label}</SelectItem>
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
            <AccordionTrigger className="text-base">{tSettings("tabs.knowledgeIndexing")}</AccordionTrigger>
            <AccordionContent>
              <div className="space-y-4 pb-2">
                <div className="space-y-2">
                  <Label htmlFor={id("chunkingStrategy")}>{tSettings("knowledgeIndexing.chunkingLabel")}<DirtyDot dirty={dirtyChunkingStrategy} /></Label>
                  <Select
                    value={effectiveChunkingStrategy}
                    onValueChange={(val) => setChunkingStrategy(val === "none" ? null : val as ChunkingStrategy)}
                  >
                    <SelectTrigger id={id("chunkingStrategy")}>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="none">{renderDefaultPlaceholder(systemDefaults?.chunking_strategy) ?? "—"}</SelectItem>
                      <SelectItem value="auto">{tForm("chunkingAuto")}</SelectItem>
                      <SelectItem value="fixed_window">{tForm("chunkingFixed")}</SelectItem>
                      <SelectItem value="paragraph">{tForm("chunkingParagraph")}</SelectItem>
                      <SelectItem value="heading_section">{tForm("chunkingHeading")}</SelectItem>
                      <SelectItem value="semantic">{tForm("chunkingSemantic")}</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex items-center gap-2">
                  <Switch
                    id={id("parentChildChunking")}
                    checked={effectiveParentChildChunking}
                    onCheckedChange={setParentChildChunking}
                  />
                  <Label htmlFor={id("parentChildChunking")}>{tSettings("knowledgeIndexing.parentChildLabel")}<DirtyDot dirty={dirtyParentChildChunking} /></Label>
                </div>
              </div>
            </AccordionContent>
          </AccordionItem>

          {/* Retrieval */}
          <AccordionItem value="retrieval">
            <AccordionTrigger className="text-base">{tSettings("tabs.contextRetrieval")}</AccordionTrigger>
            <AccordionContent>
              <div className="space-y-4 pb-2">
                <p className="text-sm text-muted-foreground">{tSettings("contextRetrieval.description")}</p>
                <div className="space-y-2">
                  <Label htmlFor={id("retrievalStrategy")}>{tSettings("contextRetrieval.searchTypeLabel")}<DirtyDot dirty={dirtyRetrievalStrategy} /></Label>
                  <Select
                    value={effectiveRetrievalStrategy}
                    onValueChange={(val) => setRetrievalStrategy(val === "none" ? null : val as RetrievalStrategy)}
                  >
                    <SelectTrigger id={id("retrievalStrategy")}>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="none">{renderDefaultPlaceholder(systemDefaults?.retrieval_strategy) ?? "—"}</SelectItem>
                      <SelectItem value="hybrid">{tSettings("contextRetrieval.hybrid")}</SelectItem>
                      <SelectItem value="vector">{tSettings("contextRetrieval.vector")}</SelectItem>
                      <SelectItem value="fulltext">{tSettings("contextRetrieval.fulltext")}</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor={id("retrievalTopK")}>{tSettings("contextRetrieval.topKLabel")}<DirtyDot dirty={dirtyRetrievalTopK} /></Label>
                  <Input
                    id={id("retrievalTopK")}
                    type="number"
                    min={1}
                    max={40}
                    value={effectiveRetrievalTopK}
                    onChange={(e) => { const v = Number.parseInt(e.target.value, 10); if (!Number.isNaN(v)) setRetrievalTopK(Math.max(1, Math.min(40, v))); }}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor={id("retrievalMinScore")}>{tSettings("contextRetrieval.minScoreLabel")}<DirtyDot dirty={dirtyRetrievalMinScore} /></Label>
                  <Input
                    id={id("retrievalMinScore")}
                    type="number"
                    min={0}
                    max={1}
                    step={0.05}
                    value={effectiveRetrievalMinScore}
                    onChange={(e) => { const v = Number.parseFloat(e.target.value); if (!Number.isNaN(v)) setRetrievalMinScore(Math.round(Math.max(0, Math.min(1, v)) * 100) / 100); }}
                  />
                </div>
              </div>
            </AccordionContent>
          </AccordionItem>

          {/* Reranking */}
          <AccordionItem value="augmentation">
            <AccordionTrigger className="text-base">{tSettings("tabs.contextAugmentation")}</AccordionTrigger>
            <AccordionContent>
              <div className="space-y-4 pb-2">
                <div className="flex items-center gap-2">
                  <Switch
                    id={id("rerankingEnabled")}
                    checked={effectiveRerankingEnabled}
                    onCheckedChange={setRerankingEnabled}
                  />
                  <Label htmlFor={id("rerankingEnabled")}>{tSettings("contextAugmentation.rerankingLabel")}<DirtyDot dirty={dirtyRerankingEnabled} /></Label>
                </div>
                {effectiveRerankingEnabled && (
                  <>
                    <div className="space-y-2">
                      <Label htmlFor={id("rerankerBackend")}>{tSettings("contextAugmentation.rerankerBackendLabel")}<DirtyDot dirty={dirtyRerankerBackend} /></Label>
                      <Select
                        value={effectiveRerankerBackend}
                        onValueChange={(val) => {
                          setRerankerBackend(val as ProjectRerankerBackend);
                          setRerankerModel("");
                        }}
                      >
                        <SelectTrigger id={id("rerankerBackend")}>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="none">{tSettings("contextAugmentation.rerankerNone")}</SelectItem>
                          <SelectItem value="cross_encoder">{tSettings("contextAugmentation.rerankerCrossEncoder")}</SelectItem>
                          <SelectItem value="inmemory">{tSettings("contextAugmentation.rerankerInMemory")}</SelectItem>
                          <SelectItem value="mmr">{tSettings("contextAugmentation.rerankerMmr")}</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor={id("rerankerModel")}>{tSettings("contextAugmentation.rerankerModelLabel")}<DirtyDot dirty={dirtyRerankerModel} /></Label>
                      <Select
                        value={rerankerModelOptions.some(m => m.id === effectiveRerankerModel) ? effectiveRerankerModel : "none"}
                        onValueChange={(val) => setRerankerModel(val === "none" ? "" : val)}
                        disabled={effectiveRerankerBackend === "none"}
                      >
                        <SelectTrigger id={id("rerankerModel")}>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="none">
                            {effectiveRerankerBackend === "none" ? tSettings("contextAugmentation.selectRerankerBackend") : tSettings("contextAugmentation.selectModel")}
                          </SelectItem>
                          {rerankerModelOptions.map((m) => (
                            <SelectItem key={m.id} value={m.id}>{m.label}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor={id("rerankerCandidateMultiplier")}>{tSettings("contextAugmentation.candidateMultiplierLabel")}<DirtyDot dirty={dirtyRerankerCandidateMultiplier} /></Label>
                      <Input
                        id={id("rerankerCandidateMultiplier")}
                        type="number"
                        min={1}
                        max={10}
                        value={effectiveRerankerCandidateMultiplier}
                        onChange={(e) => { const v = Number.parseInt(e.target.value, 10); if (!Number.isNaN(v)) setRerankerCandidateMultiplier(Math.max(1, Math.min(10, v))); }}
                      />
                    </div>
                  </>
                )}
              </div>
            </AccordionContent>
          </AccordionItem>

          {/* Chat history */}
          <AccordionItem value="history">
            <AccordionTrigger className="text-base">{tSettings("tabs.answerGeneration")}</AccordionTrigger>
            <AccordionContent>
              <div className="space-y-4 pb-2">
                <div className="space-y-2">
                  <Label htmlFor={id("chatHistoryWindowSize")}>{tSettings("answerGeneration.chatHistoryWindowLabel")}<DirtyDot dirty={dirtyChatHistoryWindowSize} /></Label>
                  <Input
                    id={id("chatHistoryWindowSize")}
                    type="number"
                    min={1}
                    max={40}
                    value={effectiveChatHistoryWindowSize}
                    onChange={(e) => { const v = Number.parseInt(e.target.value, 10); if (!Number.isNaN(v)) setChatHistoryWindowSize(Math.max(1, Math.min(40, v))); }}
                  />
                  <p className="text-xs text-muted-foreground">{tSettings("answerGeneration.chatHistoryWindowNote")}</p>
                </div>
                <div className="space-y-2">
                  <Label htmlFor={id("chatHistoryMaxChars")}>{tSettings("answerGeneration.chatHistoryMaxCharsLabel")}<DirtyDot dirty={dirtyChatHistoryMaxChars} /></Label>
                  <Input
                    id={id("chatHistoryMaxChars")}
                    type="number"
                    min={128}
                    max={16000}
                    value={effectiveChatHistoryMaxChars}
                    onChange={(e) => { const v = Number.parseInt(e.target.value, 10); if (!Number.isNaN(v)) setChatHistoryMaxChars(Math.max(128, Math.min(16000, v))); }}
                  />
                  <p className="text-xs text-muted-foreground">{tSettings("answerGeneration.chatHistoryMaxCharsNote")}</p>
                </div>
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
