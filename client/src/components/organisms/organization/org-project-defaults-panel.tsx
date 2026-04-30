"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Skeleton } from "@/components/ui/skeleton";
import { useOrganizationProjectDefaults, useUpsertOrganizationProjectDefaults } from "@/lib/hooks/use-org-project-defaults";
import { useModelCatalog } from "@/lib/hooks/use-model-catalog";
import { useOrgModelCredentials } from "@/lib/hooks/use-org-model-credentials";
import { useSystemDefaults } from "@/lib/hooks/use-system-defaults";
import type {
  ChunkingStrategy,
  ProjectEmbeddingBackend,
  ProjectLLMBackend,
  ProjectRerankerBackend,
  RetrievalStrategy,
} from "@/lib/types/api";

type OrgProjectDefaultsPanelProps = {
  organizationId: string;
};

export function OrgProjectDefaultsPanel({ organizationId }: OrgProjectDefaultsPanelProps) {
  const t = useTranslations("organizations.projectDefaults");
  const tSettings = useTranslations("projects.settings");
  const tForm = useTranslations("projects.form");
  const tCommon = useTranslations("common");

  const { data: defaults, isLoading, isError } = useOrganizationProjectDefaults(organizationId);
  const { data: systemDefaults } = useSystemDefaults();
  const upsert = useUpsertOrganizationProjectDefaults(organizationId);
  const { data: modelCatalog } = useModelCatalog();
  const { data: orgCredentials } = useOrgModelCredentials(organizationId);

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

  if (isLoading) {
    return (
      <Card className="space-y-4 p-5">
        <Skeleton className="h-6 w-48" />
        <Skeleton className="h-40 w-full" />
      </Card>
    );
  }

  if (isError) {
    return <p className="text-sm text-destructive">{t("loadError")}</p>;
  }

  // Effective values = local state ?? persisted defaults ?? fallback
  const effectiveEmbeddingBackend = embeddingBackend === undefined ? (defaults?.embedding_backend ?? "") : embeddingBackend;
  const effectiveLlmBackend = llmBackend === undefined ? (defaults?.llm_backend ?? "") : llmBackend;
  const effectiveEmbeddingModel = embeddingModel ?? (defaults?.embedding_model ?? "");
  const effectiveLlmModel = llmModel ?? (defaults?.llm_model ?? "");
  const effectiveEmbeddingCredentialId = embeddingCredentialId ?? (defaults?.embedding_api_key_credential_id ?? "");
  const effectiveLlmCredentialId = llmCredentialId ?? (defaults?.llm_api_key_credential_id ?? "");

  const activeCredentials = (orgCredentials ?? []).filter((c) => c.is_active);
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

  const effectiveRetrievalStrategy = retrievalStrategy ?? (defaults?.retrieval_strategy as RetrievalStrategy | undefined) ?? "hybrid";
  const effectiveRetrievalTopK = retrievalTopK ?? defaults?.retrieval_top_k ?? 8;
  const effectiveRetrievalMinScore = retrievalMinScore ?? defaults?.retrieval_min_score ?? 0.3;

  const effectiveRerankingEnabled = rerankingEnabled ?? defaults?.reranking_enabled ?? false;
  const effectiveRerankerBackend = rerankerBackend ?? (defaults?.reranker_backend as ProjectRerankerBackend | undefined) ?? "none";
  const effectiveRerankerModel = rerankerModel ?? defaults?.reranker_model ?? "";
  const effectiveRerankerCandidateMultiplier = rerankerCandidateMultiplier ?? defaults?.reranker_candidate_multiplier ?? 3;
  const rerankerModelOptions = modelCatalog?.reranker[effectiveRerankerBackend as ProjectRerankerBackend] ?? [];
const effectiveChatHistoryWindowSize = chatHistoryWindowSize ?? defaults?.chat_history_window_size ?? 8;
const effectiveChatHistoryMaxChars = chatHistoryMaxChars ?? defaults?.chat_history_max_chars ?? 4000;

function handleReset() {
  if (!systemDefaults) return;
  setEmbeddingBackend(systemDefaults.embedding_backend as ProjectEmbeddingBackend);
  setEmbeddingModel(systemDefaults.embedding_model);
  setEmbeddingCredentialId("");
  setLlmBackend(systemDefaults.llm_backend as ProjectLLMBackend);
  setLlmModel(systemDefaults.llm_model);
  setLlmCredentialId("");
  setChunkingStrategy(systemDefaults.chunking_strategy as ChunkingStrategy);
  setParentChildChunking(systemDefaults.parent_child_chunking);
  setRetrievalStrategy(systemDefaults.retrieval_strategy as RetrievalStrategy);
  setRetrievalTopK(systemDefaults.retrieval_top_k);
  setRetrievalMinScore(systemDefaults.retrieval_min_score);
  setRerankingEnabled(systemDefaults.reranking_enabled);
  setRerankerBackend(systemDefaults.reranker_backend as ProjectRerankerBackend);
  setRerankerModel(systemDefaults.reranker_model);
  setRerankerCandidateMultiplier(systemDefaults.reranker_candidate_multiplier);
  setChatHistoryWindowSize(systemDefaults.chat_history_window_size);
  setChatHistoryMaxChars(systemDefaults.chat_history_max_chars);
}

const hasChanges =
    effectiveEmbeddingBackend !== (defaults?.embedding_backend ?? "") ||
    effectiveEmbeddingModel !== (defaults?.embedding_model ?? "") ||
    effectiveLlmBackend !== (defaults?.llm_backend ?? "") ||
    effectiveLlmModel !== (defaults?.llm_model ?? "") ||
    embeddingCredentialId !== undefined ||
    llmCredentialId !== undefined ||
    effectiveChunkingStrategy !== (defaults?.chunking_strategy ?? "auto") ||
    effectiveParentChildChunking !== (defaults?.parent_child_chunking ?? false) ||
    effectiveRetrievalStrategy !== (defaults?.retrieval_strategy ?? "hybrid") ||
    effectiveRetrievalTopK !== (defaults?.retrieval_top_k ?? 8) ||
    effectiveRetrievalMinScore !== (defaults?.retrieval_min_score ?? 0.3) ||
    effectiveRerankingEnabled !== (defaults?.reranking_enabled ?? false) ||
    effectiveRerankerBackend !== (defaults?.reranker_backend ?? "none") ||
    effectiveRerankerModel !== (defaults?.reranker_model ?? "") ||
    effectiveRerankerCandidateMultiplier !== (defaults?.reranker_candidate_multiplier ?? 3) ||
    effectiveChatHistoryWindowSize !== (defaults?.chat_history_window_size ?? 8) ||
    effectiveChatHistoryMaxChars !== (defaults?.chat_history_max_chars ?? 4000);

  function handleSave() {
    upsert.mutate(
      {
        embedding_backend: effectiveEmbeddingBackend || null,
        embedding_model: effectiveEmbeddingModel || null,
        embedding_api_key_credential_id: effectiveEmbeddingCredentialId || null,
        llm_backend: effectiveLlmBackend || null,
        llm_model: effectiveLlmModel || null,
        llm_api_key_credential_id: effectiveLlmCredentialId || null,
        chunking_strategy: effectiveChunkingStrategy,
        parent_child_chunking: effectiveParentChildChunking,
        retrieval_strategy: effectiveRetrievalStrategy,
        retrieval_top_k: effectiveRetrievalTopK,
        retrieval_min_score: effectiveRetrievalMinScore,
        reranking_enabled: effectiveRerankingEnabled,
        reranker_backend: effectiveRerankerBackend,
        reranker_model: effectiveRerankerModel || null,
        reranker_candidate_multiplier: effectiveRerankerCandidateMultiplier,
        chat_history_window_size: effectiveChatHistoryWindowSize,
        chat_history_max_chars: effectiveChatHistoryMaxChars,
      },
      {
        onSuccess: () => {
          toast.success(t("saveSuccess"));
          setEmbeddingCredentialId(undefined);
          setLlmCredentialId(undefined);
        },
        onError: () => toast.error(t("saveError")),
      },
    );
  }

  return (
    <Card className="space-y-8 p-5">
      <div className="space-y-1">
        <h2 className="text-lg font-medium">{t("title")}</h2>
        <p className="text-sm text-muted-foreground">{t("description")}</p>
      </div>

      {/* Models */}
      <div className="space-y-4">
        <h3 className="text-base font-semibold tracking-tight">{tSettings("models.embeddingTitle")}</h3>
        <p className="text-sm text-muted-foreground">{tSettings("models.embeddingDescription")}</p>
        <div className="space-y-2">
          <Label htmlFor="org-embeddingBackend">{tSettings("models.embeddingBackendLabel")}</Label>
          <select
            id="org-embeddingBackend"
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
              <Label htmlFor="org-embeddingCredentialId">{tSettings("models.embeddingApiKeyLabel")}</Label>
              <select
                id="org-embeddingCredentialId"
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
              <Label htmlFor="org-embeddingModel">{tSettings("models.embeddingModelLabel")}</Label>
              <select
                id="org-embeddingModel"
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
        <h3 className="text-base font-semibold tracking-tight">{tSettings("models.llmTitle")}</h3>
        <p className="text-sm text-muted-foreground">{tSettings("models.llmDescription")}</p>
        <div className="space-y-2">
          <Label htmlFor="org-llmBackend">{tSettings("models.llmBackendLabel")}</Label>
          <select
            id="org-llmBackend"
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
              <Label htmlFor="org-llmCredentialId">{tSettings("models.llmApiKeyLabel")}</Label>
              <select
                id="org-llmCredentialId"
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
              <Label htmlFor="org-llmModel">{tSettings("models.llmModelLabel")}</Label>
              <select
                id="org-llmModel"
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
      </div>

      <hr className="border-border" />

      {/* Indexation */}
      <div className="space-y-4">
        <h3 className="text-base font-semibold tracking-tight">{tSettings("knowledgeIndexing.title")}</h3>
        <div className="space-y-2">
          <Label htmlFor="org-chunkingStrategy">{tSettings("knowledgeIndexing.chunkingLabel")}</Label>
          <select
            id="org-chunkingStrategy"
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
            id="org-parentChildChunking"
            checked={effectiveParentChildChunking}
            onCheckedChange={setParentChildChunking}
          />
          <Label htmlFor="org-parentChildChunking">{tSettings("knowledgeIndexing.parentChildLabel")}</Label>
        </div>
      </div>

      <hr className="border-border" />

      {/* Retrieval */}
      <div className="space-y-4">
        <h3 className="text-base font-semibold tracking-tight">{tSettings("contextRetrieval.title")}</h3>
        <p className="text-sm text-muted-foreground">{tSettings("contextRetrieval.description")}</p>
        <div className="space-y-2">
          <Label htmlFor="org-retrievalStrategy">{tSettings("contextRetrieval.searchTypeLabel")}</Label>
          <select
            id="org-retrievalStrategy"
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
          <Label htmlFor="org-retrievalTopK">{tSettings("contextRetrieval.topKLabel")}</Label>
          <Input
            id="org-retrievalTopK"
            type="number"
            min={1}
            max={40}
            value={effectiveRetrievalTopK}
            onChange={(e) => { const v = Number.parseInt(e.target.value, 10); if (!Number.isNaN(v)) setRetrievalTopK(Math.max(1, Math.min(40, v))); }}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="org-retrievalMinScore">{tSettings("contextRetrieval.minScoreLabel")}</Label>
          <Input
            id="org-retrievalMinScore"
            type="number"
            min={0}
            max={1}
            step={0.05}
            value={effectiveRetrievalMinScore}
            onChange={(e) => { const v = Number.parseFloat(e.target.value); if (!Number.isNaN(v)) setRetrievalMinScore(Math.round(Math.max(0, Math.min(1, v)) * 100) / 100); }}
          />
        </div>
      </div>

      <hr className="border-border" />

      {/* Reranking */}
      <div className="space-y-4">
        <h3 className="text-base font-semibold tracking-tight">{tSettings("contextAugmentation.title")}</h3>
        <div className="flex items-center gap-2">
          <Switch
            id="org-rerankingEnabled"
            checked={effectiveRerankingEnabled}
            onCheckedChange={setRerankingEnabled}
          />
          <Label htmlFor="org-rerankingEnabled">{tSettings("contextAugmentation.rerankingLabel")}</Label>
        </div>
        {effectiveRerankingEnabled && (
          <>
            <div className="space-y-2">
              <Label htmlFor="org-rerankerBackend">{tSettings("contextAugmentation.rerankerBackendLabel")}</Label>
              <select
                id="org-rerankerBackend"
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
              <Label htmlFor="org-rerankerModel">{tSettings("contextAugmentation.rerankerModelLabel")}</Label>
              <select
                id="org-rerankerModel"
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
              <Label htmlFor="org-rerankerCandidateMultiplier">{tSettings("contextAugmentation.candidateMultiplierLabel")}</Label>
              <Input
                id="org-rerankerCandidateMultiplier"
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

      <hr className="border-border" />

      {/* Chat history */}
      <div className="space-y-4">
        <h3 className="text-base font-semibold tracking-tight">{tSettings("answerGeneration.historyTitle")}</h3>
        <div className="space-y-2">
          <Label htmlFor="org-chatHistoryWindowSize">{tSettings("answerGeneration.chatHistoryWindowLabel")}</Label>
          <Input
            id="org-chatHistoryWindowSize"
            type="number"
            min={1}
            max={40}
            value={effectiveChatHistoryWindowSize}
            onChange={(e) => { const v = Number.parseInt(e.target.value, 10); if (!Number.isNaN(v)) setChatHistoryWindowSize(Math.max(1, Math.min(40, v))); }}
          />
          <p className="text-xs text-muted-foreground">{tSettings("answerGeneration.chatHistoryWindowNote")}</p>
        </div>
        <div className="space-y-2">
          <Label htmlFor="org-chatHistoryMaxChars">{tSettings("answerGeneration.chatHistoryMaxCharsLabel")}</Label>
          <Input
            id="org-chatHistoryMaxChars"
            type="number"
            min={128}
            max={16000}
            value={effectiveChatHistoryMaxChars}
            onChange={(e) => { const v = Number.parseInt(e.target.value, 10); if (!Number.isNaN(v)) setChatHistoryMaxChars(Math.max(128, Math.min(16000, v))); }}
          />
          <p className="text-xs text-muted-foreground">{tSettings("answerGeneration.chatHistoryMaxCharsNote")}</p>
        </div>
      </div>

      <div className="pt-2 flex gap-3">
        <Button
          className="cursor-pointer"
          disabled={!hasChanges || upsert.isPending}
          onClick={handleSave}
        >
          {upsert.isPending ? tCommon("saving") : tSettings("saveChanges")}
        </Button>
        <Button
          variant="outline"
          className="cursor-pointer"
          onClick={handleReset}
          disabled={!systemDefaults || upsert.isPending}
        >
          {t("resetToSystem")}
        </Button>
      </div>
    </Card>
  );
}
