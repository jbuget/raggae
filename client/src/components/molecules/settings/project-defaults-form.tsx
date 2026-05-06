"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
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

type Credential = { id: string; provider: ModelProvider; masked_key: string; is_active: boolean };

type SaveCallbacks = { onSuccess?: () => void; onError?: () => void };

type ProjectDefaultsFormProps = {
  defaults: ProjectDefaultsConfig | null | undefined;
  systemDefaults: SystemDefaultsResponse | undefined;
  inheritedDefaults?: ProjectDefaultsConfig | null | undefined;
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
  inheritedDefaults,
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
  const [chunkingStrategy, setChunkingStrategy] = useState<ChunkingStrategy | undefined>(undefined);
  const [parentChildChunking, setParentChildChunking] = useState<boolean | undefined>(undefined);

  // Retrieval state
  const [retrievalStrategy, setRetrievalStrategy] = useState<RetrievalStrategy | undefined>(undefined);
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

  // Effective values = local state ?? persisted defaults ?? system defaults ?? hardcoded
  const effectiveEmbeddingBackend = embeddingBackend === undefined ? (defaults?.embedding_backend ?? systemDefaults?.embedding_backend ?? "") : embeddingBackend;
  const effectiveLlmBackend = llmBackend === undefined ? (defaults?.llm_backend ?? systemDefaults?.llm_backend ?? "") : llmBackend;
  const effectiveEmbeddingModel = embeddingModel ?? (defaults?.embedding_model ?? systemDefaults?.embedding_model ?? "");
  const effectiveLlmModel = llmModel ?? (defaults?.llm_model ?? systemDefaults?.llm_model ?? "");
  const effectiveEmbeddingCredentialId = embeddingCredentialId ?? (defaults?.embedding_api_key_credential_id ?? "");
  const effectiveLlmCredentialId = llmCredentialId ?? (defaults?.llm_api_key_credential_id ?? "");

  const activeCredentials = credentials.filter((c) => c.is_active);
  const credentialsByProvider = activeCredentials.reduce<Record<string, Array<{ id: string; masked_key: string }>>>(
    (acc, c) => { (acc[c.provider] ??= []).push({ id: c.id, masked_key: c.masked_key }); return acc; },
    {},
  );
  const embeddingProviderForHints = effectiveEmbeddingBackend === "openai" || effectiveEmbeddingBackend === "gemini" ? effectiveEmbeddingBackend : null;
  const llmProviderForHints = effectiveLlmBackend === "openai" || effectiveLlmBackend === "gemini" || effectiveLlmBackend === "anthropic" ? effectiveLlmBackend : null;
  const embeddingCredentialOptions = embeddingProviderForHints ? (credentialsByProvider[embeddingProviderForHints] ?? []) : [];
  const llmCredentialOptions = llmProviderForHints ? (credentialsByProvider[llmProviderForHints] ?? []) : [];
  const embeddingModelOptions = effectiveEmbeddingBackend ? (modelCatalog?.embedding[effectiveEmbeddingBackend as ProjectEmbeddingBackend] ?? []) : [];
  const llmModelOptions = effectiveLlmBackend ? (modelCatalog?.llm[effectiveLlmBackend as ProjectLLMBackend] ?? []) : [];

  const effectiveChunkingStrategy = chunkingStrategy ?? (defaults?.chunking_strategy as ChunkingStrategy | undefined) ?? "auto";
  const effectiveParentChildChunking = parentChildChunking ?? defaults?.parent_child_chunking ?? false;

  const effectiveRetrievalStrategy = retrievalStrategy ?? (defaults?.retrieval_strategy as RetrievalStrategy | undefined) ?? (systemDefaults?.retrieval_strategy as RetrievalStrategy | undefined) ?? "hybrid";
  const effectiveRetrievalTopK = retrievalTopK ?? defaults?.retrieval_top_k ?? systemDefaults?.retrieval_top_k ?? 8;
  const effectiveRetrievalMinScore = retrievalMinScore ?? defaults?.retrieval_min_score ?? systemDefaults?.retrieval_min_score ?? 0.3;

  const effectiveRerankingEnabled = rerankingEnabled ?? defaults?.reranking_enabled ?? false;
  const effectiveRerankerBackend = rerankerBackend ?? (defaults?.reranker_backend as ProjectRerankerBackend | undefined) ?? (systemDefaults?.reranker_backend as ProjectRerankerBackend | undefined) ?? "none";
  const effectiveRerankerModel = rerankerModel ?? defaults?.reranker_model ?? systemDefaults?.reranker_model ?? "";
  const effectiveRerankerCandidateMultiplier = rerankerCandidateMultiplier ?? defaults?.reranker_candidate_multiplier ?? systemDefaults?.reranker_candidate_multiplier ?? 3;
  const rerankerModelOptions = modelCatalog?.reranker[effectiveRerankerBackend as ProjectRerankerBackend] ?? [];

  const effectiveChatHistoryWindowSize = chatHistoryWindowSize ?? defaults?.chat_history_window_size ?? systemDefaults?.chat_history_window_size ?? 8;
  const effectiveChatHistoryMaxChars = chatHistoryMaxChars ?? defaults?.chat_history_max_chars ?? systemDefaults?.chat_history_max_chars ?? 4000;

  // Per-section hasChanges
  const hasModelsChanges =
    effectiveEmbeddingBackend !== (defaults?.embedding_backend ?? systemDefaults?.embedding_backend ?? "") ||
    effectiveEmbeddingModel !== (defaults?.embedding_model ?? systemDefaults?.embedding_model ?? "") ||
    effectiveLlmBackend !== (defaults?.llm_backend ?? systemDefaults?.llm_backend ?? "") ||
    effectiveLlmModel !== (defaults?.llm_model ?? systemDefaults?.llm_model ?? "") ||
    embeddingCredentialId !== undefined ||
    llmCredentialId !== undefined;

  const hasIndexingChanges =
    effectiveChunkingStrategy !== (defaults?.chunking_strategy ?? "auto") ||
    effectiveParentChildChunking !== (defaults?.parent_child_chunking ?? false);

  const hasRetrievalChanges =
    effectiveRetrievalStrategy !== (defaults?.retrieval_strategy ?? systemDefaults?.retrieval_strategy ?? "hybrid") ||
    effectiveRetrievalTopK !== (defaults?.retrieval_top_k ?? systemDefaults?.retrieval_top_k ?? 8) ||
    effectiveRetrievalMinScore !== (defaults?.retrieval_min_score ?? systemDefaults?.retrieval_min_score ?? 0.3);

  const hasRerankingChanges =
    effectiveRerankingEnabled !== (defaults?.reranking_enabled ?? false) ||
    effectiveRerankerBackend !== (defaults?.reranker_backend ?? systemDefaults?.reranker_backend ?? "none") ||
    effectiveRerankerModel !== (defaults?.reranker_model ?? systemDefaults?.reranker_model ?? "") ||
    effectiveRerankerCandidateMultiplier !== (defaults?.reranker_candidate_multiplier ?? systemDefaults?.reranker_candidate_multiplier ?? 3);

  const hasHistoryChanges =
    effectiveChatHistoryWindowSize !== (defaults?.chat_history_window_size ?? systemDefaults?.chat_history_window_size ?? 8) ||
    effectiveChatHistoryMaxChars !== (defaults?.chat_history_max_chars ?? systemDefaults?.chat_history_max_chars ?? 4000);

  const hasModelsConfigured = inheritedDefaults !== undefined && (
    defaults?.embedding_backend != null || defaults?.llm_backend != null
  );
  const hasIndexingConfigured = inheritedDefaults !== undefined && (
    defaults?.chunking_strategy != null || defaults?.parent_child_chunking != null
  );
  const hasRetrievalConfigured = inheritedDefaults !== undefined && (
    defaults?.retrieval_strategy != null || defaults?.retrieval_top_k != null || defaults?.retrieval_min_score != null
  );
  const hasRerankingConfigured = inheritedDefaults !== undefined && (
    defaults?.reranking_enabled != null || defaults?.reranker_backend != null
  );
  const hasHistoryConfigured = inheritedDefaults !== undefined && (
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
                  <Label htmlFor={id("embeddingBackend")}>{tSettings("models.embeddingBackendLabel")}</Label>
                  <select
                    id={id("embeddingBackend")}
                    value={effectiveEmbeddingBackend}
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
                      <Label htmlFor={id("embeddingCredentialId")}>{tSettings("models.embeddingApiKeyLabel")}</Label>
                      <select
                        id={id("embeddingCredentialId")}
                        value={effectiveEmbeddingCredentialId}
                        onChange={(e) => setEmbeddingCredentialId(e.target.value)}
                        disabled={!embeddingProviderForHints}
                        className="border-input bg-background w-full rounded-md border px-3 py-2 text-sm disabled:opacity-60"
                      >
                        <option value="">{embeddingProviderForHints ? tSettings("models.noSelection") : tSettings("models.selectEmbeddingFirst")}</option>
                        {embeddingCredentialOptions.map((item) => <option key={item.id} value={item.id}>{item.masked_key}</option>)}
                      </select>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor={id("embeddingModel")}>{tSettings("models.embeddingModelLabel")}</Label>
                      <select
                        id={id("embeddingModel")}
                        value={effectiveEmbeddingModel}
                        onChange={(e) => setEmbeddingModel(e.target.value)}
                        className="border-input bg-background w-full rounded-md border px-3 py-2 text-sm"
                      >
                        <option value="">{tSettings("models.selectModel")}</option>
                        {embeddingModelOptions.map((m) => <option key={m.id} value={m.id}>{m.label}</option>)}
                      </select>
                    </div>
                  </>
                ) : null}
                <hr className="border-border" />
                <p className="text-sm font-medium">{tSettings("models.llmTitle")}</p>
                <p className="text-sm text-muted-foreground">{tSettings("models.llmDescription")}</p>
                <div className="space-y-2">
                  <Label htmlFor={id("llmBackend")}>{tSettings("models.llmBackendLabel")}</Label>
                  <select
                    id={id("llmBackend")}
                    value={effectiveLlmBackend}
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
                      <Label htmlFor={id("llmCredentialId")}>{tSettings("models.llmApiKeyLabel")}</Label>
                      <select
                        id={id("llmCredentialId")}
                        value={effectiveLlmCredentialId}
                        onChange={(e) => setLlmCredentialId(e.target.value)}
                        disabled={!llmProviderForHints}
                        className="border-input bg-background w-full rounded-md border px-3 py-2 text-sm disabled:opacity-60"
                      >
                        <option value="">{llmProviderForHints ? tSettings("models.noSelection") : tSettings("models.selectLlmFirst")}</option>
                        {llmCredentialOptions.map((item) => <option key={item.id} value={item.id}>{item.masked_key}</option>)}
                      </select>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor={id("llmModel")}>{tSettings("models.llmModelLabel")}</Label>
                      <select
                        id={id("llmModel")}
                        value={effectiveLlmModel}
                        onChange={(e) => setLlmModel(e.target.value)}
                        className="border-input bg-background w-full rounded-md border px-3 py-2 text-sm"
                      >
                        <option value="">{tSettings("models.selectModel")}</option>
                        {llmModelOptions.map((m) => <option key={m.id} value={m.id}>{m.label}</option>)}
                      </select>
                    </div>
                  </>
                ) : null}
                <div className="flex gap-2">
                  <Button
                    className="cursor-pointer"
                    disabled={!hasModelsChanges || isPending}
                    onClick={() => onSave(
                      {
                        ...buildBasePayload(),
                        embedding_backend: (effectiveEmbeddingBackend as ProjectEmbeddingBackend) || null,
                        embedding_model: effectiveEmbeddingModel || null,
                        embedding_api_key_credential_id: effectiveEmbeddingCredentialId || null,
                        llm_backend: (effectiveLlmBackend as ProjectLLMBackend) || null,
                        llm_model: effectiveLlmModel || null,
                        llm_api_key_credential_id: effectiveLlmCredentialId || null,
                      },
                      {
                        onSuccess: () => { setEmbeddingCredentialId(undefined); setLlmCredentialId(undefined); },
                      },
                    )}
                  >
                    {isPending ? tCommon("saving") : tSettings("saveChanges")}
                  </Button>
                  {hasModelsConfigured && (
                    <Button
                      variant="outline"
                      className="cursor-pointer"
                      disabled={isPending}
                      onClick={() => onSave({ ...buildBasePayload(), embedding_backend: null, embedding_model: null, embedding_api_key_credential_id: null, llm_backend: null, llm_model: null, llm_api_key_credential_id: null })}
                    >
                      {tSettings("resetToInherited")}
                    </Button>
                  )}
                </div>
              </div>
            </AccordionContent>
          </AccordionItem>

          {/* Indexation */}
          <AccordionItem value="indexing">
            <AccordionTrigger className="text-base">{tSettings("tabs.knowledgeIndexing")}</AccordionTrigger>
            <AccordionContent>
              <div className="space-y-4 pb-2">
                <div className="space-y-2">
                  <Label htmlFor={id("chunkingStrategy")}>{tSettings("knowledgeIndexing.chunkingLabel")}</Label>
                  <select
                    id={id("chunkingStrategy")}
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
                    id={id("parentChildChunking")}
                    checked={effectiveParentChildChunking}
                    onCheckedChange={setParentChildChunking}
                  />
                  <Label htmlFor={id("parentChildChunking")}>{tSettings("knowledgeIndexing.parentChildLabel")}</Label>
                </div>
                <div className="flex gap-2">
                  <Button
                    className="cursor-pointer"
                    disabled={!hasIndexingChanges || isPending}
                    onClick={() => onSave({
                      ...buildBasePayload(),
                      chunking_strategy: effectiveChunkingStrategy,
                      parent_child_chunking: effectiveParentChildChunking,
                    })}
                  >
                    {isPending ? tCommon("saving") : tSettings("saveChanges")}
                  </Button>
                  {hasIndexingConfigured && (
                    <Button
                      variant="outline"
                      className="cursor-pointer"
                      disabled={isPending}
                      onClick={() => onSave({ ...buildBasePayload(), chunking_strategy: null, parent_child_chunking: null })}
                    >
                      {tSettings("resetToInherited")}
                    </Button>
                  )}
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
                  <Label htmlFor={id("retrievalStrategy")}>{tSettings("contextRetrieval.searchTypeLabel")}</Label>
                  <select
                    id={id("retrievalStrategy")}
                    value={effectiveRetrievalStrategy}
                    onChange={(e) => setRetrievalStrategy(e.target.value as RetrievalStrategy)}
                    className="border-input bg-background w-full rounded-md border px-3 py-2 text-sm"
                  >
                    <option value="hybrid">{tSettings("contextRetrieval.hybrid")}</option>
                    <option value="vector">{tSettings("contextRetrieval.vector")}</option>
                    <option value="fulltext">{tSettings("contextRetrieval.fulltext")}</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor={id("retrievalTopK")}>{tSettings("contextRetrieval.topKLabel")}</Label>
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
                  <Label htmlFor={id("retrievalMinScore")}>{tSettings("contextRetrieval.minScoreLabel")}</Label>
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
                <div className="flex gap-2">
                  <Button
                    className="cursor-pointer"
                    disabled={!hasRetrievalChanges || isPending}
                    onClick={() => onSave({
                      ...buildBasePayload(),
                      retrieval_strategy: effectiveRetrievalStrategy,
                      retrieval_top_k: effectiveRetrievalTopK,
                      retrieval_min_score: effectiveRetrievalMinScore,
                    })}
                  >
                    {isPending ? tCommon("saving") : tSettings("saveChanges")}
                  </Button>
                  {hasRetrievalConfigured && (
                    <Button
                      variant="outline"
                      className="cursor-pointer"
                      disabled={isPending}
                      onClick={() => onSave({ ...buildBasePayload(), retrieval_strategy: null, retrieval_top_k: null, retrieval_min_score: null })}
                    >
                      {tSettings("resetToInherited")}
                    </Button>
                  )}
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
                  <Label htmlFor={id("rerankingEnabled")}>{tSettings("contextAugmentation.rerankingLabel")}</Label>
                </div>
                {effectiveRerankingEnabled && (
                  <>
                    <div className="space-y-2">
                      <Label htmlFor={id("rerankerBackend")}>{tSettings("contextAugmentation.rerankerBackendLabel")}</Label>
                      <select
                        id={id("rerankerBackend")}
                        value={effectiveRerankerBackend}
                        onChange={(e) => { setRerankerBackend(e.target.value as ProjectRerankerBackend); setRerankerModel(""); }}
                        className="border-input bg-background w-full rounded-md border px-3 py-2 text-sm"
                      >
                        <option value="none">{tSettings("contextAugmentation.rerankerNone")}</option>
                        <option value="cross_encoder">{tSettings("contextAugmentation.rerankerCrossEncoder")}</option>
                        <option value="inmemory">{tSettings("contextAugmentation.rerankerInMemory")}</option>
                        <option value="mmr">{tSettings("contextAugmentation.rerankerMmr")}</option>
                      </select>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor={id("rerankerModel")}>{tSettings("contextAugmentation.rerankerModelLabel")}</Label>
                      <select
                        id={id("rerankerModel")}
                        value={effectiveRerankerModel}
                        onChange={(e) => setRerankerModel(e.target.value)}
                        disabled={effectiveRerankerBackend === "none"}
                        className="border-input bg-background w-full rounded-md border px-3 py-2 text-sm disabled:opacity-60"
                      >
                        <option value="">{effectiveRerankerBackend === "none" ? tSettings("contextAugmentation.selectRerankerBackend") : tSettings("contextAugmentation.selectModel")}</option>
                        {rerankerModelOptions.map((m) => <option key={m.id} value={m.id}>{m.label}</option>)}
                      </select>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor={id("rerankerCandidateMultiplier")}>{tSettings("contextAugmentation.candidateMultiplierLabel")}</Label>
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
                <div className="flex gap-2">
                  <Button
                    className="cursor-pointer"
                    disabled={!hasRerankingChanges || isPending}
                    onClick={() => onSave({
                      ...buildBasePayload(),
                      reranking_enabled: effectiveRerankingEnabled,
                      reranker_backend: effectiveRerankerBackend,
                      reranker_model: effectiveRerankerModel || null,
                      reranker_candidate_multiplier: effectiveRerankerCandidateMultiplier,
                    })}
                  >
                    {isPending ? tCommon("saving") : tSettings("saveChanges")}
                  </Button>
                  {hasRerankingConfigured && (
                    <Button
                      variant="outline"
                      className="cursor-pointer"
                      disabled={isPending}
                      onClick={() => onSave({ ...buildBasePayload(), reranking_enabled: null, reranker_backend: null, reranker_model: null, reranker_candidate_multiplier: null })}
                    >
                      {tSettings("resetToInherited")}
                    </Button>
                  )}
                </div>
              </div>
            </AccordionContent>
          </AccordionItem>

          {/* Chat history */}
          <AccordionItem value="history">
            <AccordionTrigger className="text-base">{tSettings("tabs.answerGeneration")}</AccordionTrigger>
            <AccordionContent>
              <div className="space-y-4 pb-2">
                <div className="space-y-2">
                  <Label htmlFor={id("chatHistoryWindowSize")}>{tSettings("answerGeneration.chatHistoryWindowLabel")}</Label>
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
                  <Label htmlFor={id("chatHistoryMaxChars")}>{tSettings("answerGeneration.chatHistoryMaxCharsLabel")}</Label>
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
                <div className="flex gap-2">
                  <Button
                    className="cursor-pointer"
                    disabled={!hasHistoryChanges || isPending}
                    onClick={() => onSave({
                      ...buildBasePayload(),
                      chat_history_window_size: effectiveChatHistoryWindowSize,
                      chat_history_max_chars: effectiveChatHistoryMaxChars,
                    })}
                  >
                    {isPending ? tCommon("saving") : tSettings("saveChanges")}
                  </Button>
                  {hasHistoryConfigured && (
                    <Button
                      variant="outline"
                      className="cursor-pointer"
                      disabled={isPending}
                      onClick={() => onSave({ ...buildBasePayload(), chat_history_window_size: null, chat_history_max_chars: null })}
                    >
                      {tSettings("resetToInherited")}
                    </Button>
                  )}
                </div>
              </div>
            </AccordionContent>
          </AccordionItem>

        </Accordion>
      </Card>
    </div>
  );
}
