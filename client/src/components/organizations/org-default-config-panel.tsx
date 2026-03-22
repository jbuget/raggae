"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { Switch } from "@/components/ui/switch";
import { useOrgModelCredentials } from "@/lib/hooks/use-org-model-credentials";
import {
  useOrganizationDefaultConfig,
  useUpsertOrganizationDefaultConfig,
} from "@/lib/hooks/use-organization-default-config";
import type {
  ChunkingStrategy,
  OrganizationDefaultConfigResponse,
  RetrievalStrategy,
} from "@/lib/types/api";

const INPUT_CLASS =
  "flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus:outline-none focus:ring-1 focus:ring-ring";

type OrgDefaultConfigPanelProps = {
  organizationId: string;
};

export function OrgDefaultConfigPanel({ organizationId }: OrgDefaultConfigPanelProps) {
  const { data: config, isLoading } = useOrganizationDefaultConfig(organizationId);
  const { data: credentials } = useOrgModelCredentials(organizationId);

  if (isLoading) {
    return (
      <div className="space-y-3">
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-10 w-full" />
      </div>
    );
  }

  return (
    <OrgDefaultConfigForm
      key={config?.updated_at ?? "empty"}
      organizationId={organizationId}
      config={config ?? null}
      credentials={credentials ?? []}
    />
  );
}

type Credential = { id: string; provider: string; masked_key: string };

type OrgDefaultConfigFormProps = {
  organizationId: string;
  config: OrganizationDefaultConfigResponse | null;
  credentials: Credential[];
};

function SectionTitle({ title }: { title: string }) {
  return <h3 className="text-base font-semibold">{title}</h3>;
}

function SubSectionTitle({ title }: { title: string }) {
  return <h4 className="text-sm font-medium text-muted-foreground">{title}</h4>;
}

function OrgDefaultConfigForm({
  organizationId,
  config,
  credentials,
}: OrgDefaultConfigFormProps) {
  const t = useTranslations("organizations.defaultConfig");
  const tCommon = useTranslations("common");
  const upsert = useUpsertOrganizationDefaultConfig(organizationId);

  // Models — Embedding
  const [embeddingBackend, setEmbeddingBackend] = useState(config?.embedding_backend ?? "");
  const [embeddingModel, setEmbeddingModel] = useState(config?.embedding_model ?? "");
  const [orgEmbeddingCredId, setOrgEmbeddingCredId] = useState(
    config?.org_embedding_api_key_credential_id ?? "",
  );

  // Models — LLM
  const [llmBackend, setLlmBackend] = useState(config?.llm_backend ?? "");
  const [llmModel, setLlmModel] = useState(config?.llm_model ?? "");
  const [orgLlmCredId, setOrgLlmCredId] = useState(
    config?.org_llm_api_key_credential_id ?? "",
  );

  // Indexation
  const [chunkingStrategy, setChunkingStrategy] = useState(config?.chunking_strategy ?? "");
  const [parentChildChunking, setParentChildChunking] = useState(
    config?.parent_child_chunking ?? true,
  );

  // Retrieval
  const [retrievalStrategy, setRetrievalStrategy] = useState(
    config?.retrieval_strategy ?? "",
  );
  const [retrievalTopK, setRetrievalTopK] = useState(
    config?.retrieval_top_k?.toString() ?? "",
  );
  const [retrievalMinScore, setRetrievalMinScore] = useState(
    config?.retrieval_min_score?.toString() ?? "",
  );

  // Augmentation
  const [rerankingEnabled, setRerankingEnabled] = useState(
    config?.reranking_enabled ?? true,
  );
  const [rerankerBackend, setRerankerBackend] = useState(config?.reranker_backend ?? "");
  const [rerankerModel, setRerankerModel] = useState(config?.reranker_model ?? "");
  const [rerankerCandidateMultiplier, setRerankerCandidateMultiplier] = useState(
    config?.reranker_candidate_multiplier?.toString() ?? "",
  );

  function handleSave() {
    upsert.mutate(
      {
        embedding_backend: embeddingBackend || null,
        embedding_model: embeddingModel || null,
        llm_backend: llmBackend || null,
        llm_model: llmModel || null,
        chunking_strategy: (chunkingStrategy as ChunkingStrategy) || null,
        parent_child_chunking: parentChildChunking,
        retrieval_strategy: (retrievalStrategy as RetrievalStrategy) || null,
        retrieval_top_k: retrievalTopK ? parseInt(retrievalTopK, 10) : null,
        retrieval_min_score: retrievalMinScore ? parseFloat(retrievalMinScore) : null,
        reranking_enabled: rerankingEnabled,
        reranker_backend: rerankerBackend || null,
        reranker_model: rerankerModel || null,
        reranker_candidate_multiplier: rerankerCandidateMultiplier
          ? parseInt(rerankerCandidateMultiplier, 10)
          : null,
        org_embedding_api_key_credential_id: orgEmbeddingCredId || null,
        org_llm_api_key_credential_id: orgLlmCredId || null,
      },
      {
        onSuccess: () => toast.success(t("saveSuccess")),
        onError: () => toast.error(t("saveError")),
      },
    );
  }

  const embeddingCredentials = credentials.filter(
    (c) => c.provider === "openai" || c.provider === "gemini",
  );

  return (
    <Card className="space-y-6 p-5">
      <div className="space-y-1">
        <h2 className="text-lg font-medium">{t("title")}</h2>
        <p className="text-sm text-muted-foreground">{t("description")}</p>
      </div>

      {/* ── Modèles ─────────────────────────────────────────── */}
      <div className="space-y-5">
        <SectionTitle title={t("sectionModels")} />

        {/* Embedding */}
        <div className="space-y-3 rounded-md border p-4">
          <SubSectionTitle title={t("sectionEmbedding")} />
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="cfg-embedding-backend">{t("embeddingBackendLabel")}</Label>
              <select
                id="cfg-embedding-backend"
                value={embeddingBackend}
                onChange={(e) => setEmbeddingBackend(e.target.value)}
                className={INPUT_CLASS}
              >
                <option value="">{t("noDefault")}</option>
                <option value="openai">OpenAI</option>
                <option value="gemini">Gemini</option>
                <option value="ollama">Ollama</option>
              </select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="cfg-embedding-model">{t("embeddingModelLabel")}</Label>
              <input
                id="cfg-embedding-model"
                type="text"
                value={embeddingModel}
                onChange={(e) => setEmbeddingModel(e.target.value)}
                placeholder={t("embeddingModelPlaceholder")}
                className={INPUT_CLASS}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="cfg-emb-cred">{t("orgEmbeddingCredLabel")}</Label>
              <select
                id="cfg-emb-cred"
                value={orgEmbeddingCredId}
                onChange={(e) => setOrgEmbeddingCredId(e.target.value)}
                className={INPUT_CLASS}
              >
                <option value="">{t("noDefault")}</option>
                {embeddingCredentials.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.provider} — {c.masked_key}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* RAG / LLM */}
        <div className="space-y-3 rounded-md border p-4">
          <SubSectionTitle title={t("sectionLlm")} />
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="cfg-llm-backend">{t("llmBackendLabel")}</Label>
              <select
                id="cfg-llm-backend"
                value={llmBackend}
                onChange={(e) => setLlmBackend(e.target.value)}
                className={INPUT_CLASS}
              >
                <option value="">{t("noDefault")}</option>
                <option value="openai">OpenAI</option>
                <option value="gemini">Gemini</option>
                <option value="anthropic">Anthropic</option>
                <option value="ollama">Ollama</option>
              </select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="cfg-llm-model">{t("llmModelLabel")}</Label>
              <input
                id="cfg-llm-model"
                type="text"
                value={llmModel}
                onChange={(e) => setLlmModel(e.target.value)}
                placeholder={t("llmModelPlaceholder")}
                className={INPUT_CLASS}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="cfg-llm-cred">{t("orgLlmCredLabel")}</Label>
              <select
                id="cfg-llm-cred"
                value={orgLlmCredId}
                onChange={(e) => setOrgLlmCredId(e.target.value)}
                className={INPUT_CLASS}
              >
                <option value="">{t("noDefault")}</option>
                {credentials.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.provider} — {c.masked_key}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </div>

      <Separator />

      {/* ── Indexation ──────────────────────────────────────── */}
      <div className="space-y-4">
        <SectionTitle title={t("sectionIndexation")} />

        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="cfg-chunking">{t("chunkingStrategyLabel")}</Label>
            <select
              id="cfg-chunking"
              value={chunkingStrategy}
              onChange={(e) => setChunkingStrategy(e.target.value)}
              className={INPUT_CLASS}
            >
              <option value="">{t("chunkingStrategyDefault")}</option>
              <option value="fixed_window">Fixed window</option>
              <option value="paragraph">Paragraph</option>
              <option value="heading_section">Heading section</option>
              <option value="semantic">Semantic</option>
            </select>
          </div>

          <div className="space-y-2">
            <Label>{t("parentChildChunkingLabel")}</Label>
            <div className="flex items-center gap-3 rounded-md border px-3 h-9">
              <Switch
                id="cfg-parent-child"
                checked={parentChildChunking}
                onCheckedChange={setParentChildChunking}
              />
              <span className="text-xs text-muted-foreground">
                {t("parentChildChunkingDefault")}
              </span>
            </div>
          </div>
        </div>
      </div>

      <Separator />

      {/* ── Retrieval ───────────────────────────────────────── */}
      <div className="space-y-4">
        <SectionTitle title={t("sectionRetrieval")} />

        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="cfg-retrieval">{t("retrievalStrategyLabel")}</Label>
            <select
              id="cfg-retrieval"
              value={retrievalStrategy}
              onChange={(e) => setRetrievalStrategy(e.target.value)}
              className={INPUT_CLASS}
            >
              <option value="">{t("retrievalStrategyDefault")}</option>
              <option value="vector">Vector</option>
              <option value="fulltext">Full-text</option>
              <option value="hybrid">Hybrid</option>
            </select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="cfg-top-k">{t("retrievalTopKLabel")}</Label>
            <input
              id="cfg-top-k"
              type="number"
              min={1}
              max={50}
              value={retrievalTopK}
              onChange={(e) => setRetrievalTopK(e.target.value)}
              placeholder={t("retrievalTopKPlaceholder")}
              className={INPUT_CLASS}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="cfg-min-score">{t("retrievalMinScoreLabel")}</Label>
            <input
              id="cfg-min-score"
              type="number"
              min={0}
              max={1}
              step={0.05}
              value={retrievalMinScore}
              onChange={(e) => setRetrievalMinScore(e.target.value)}
              placeholder={t("retrievalMinScorePlaceholder")}
              className={INPUT_CLASS}
            />
          </div>
        </div>
      </div>

      <Separator />

      {/* ── Augmentation ────────────────────────────────────── */}
      <div className="space-y-4">
        <SectionTitle title={t("sectionAugmentation")} />

        <div className="space-y-2">
          <Label>{t("rerankingLabel")}</Label>
          <div className="flex items-center gap-3 rounded-md border px-3 h-9">
            <Switch
              id="cfg-reranking"
              checked={rerankingEnabled}
              onCheckedChange={setRerankingEnabled}
            />
            <span className="text-xs text-muted-foreground">{t("rerankingDefault")}</span>
          </div>
          <p className="text-xs text-muted-foreground">{t("rerankingHint")}</p>
        </div>

        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="cfg-reranker-backend">{t("rerankerBackendLabel")}</Label>
            <select
              id="cfg-reranker-backend"
              value={rerankerBackend}
              onChange={(e) => setRerankerBackend(e.target.value)}
              className={INPUT_CLASS}
            >
              <option value="">{t("rerankerBackendDefault")}</option>
              <option value="cross_encoder">Cross-encoder</option>
              <option value="mmr">MMR Diversity</option>
            </select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="cfg-reranker-model">{t("rerankerModelLabel")}</Label>
            <input
              id="cfg-reranker-model"
              type="text"
              value={rerankerModel}
              onChange={(e) => setRerankerModel(e.target.value)}
              placeholder={t("rerankerModelPlaceholder")}
              className={INPUT_CLASS}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="cfg-reranker-multiplier">{t("rerankerCandidateMultiplierLabel")}</Label>
            <input
              id="cfg-reranker-multiplier"
              type="number"
              min={1}
              max={20}
              value={rerankerCandidateMultiplier}
              onChange={(e) => setRerankerCandidateMultiplier(e.target.value)}
              placeholder={t("rerankerCandidateMultiplierPlaceholder")}
              className={INPUT_CLASS}
            />
          </div>
        </div>
      </div>

      <Separator />

      <Button onClick={handleSave} disabled={upsert.isPending} className="cursor-pointer">
        {upsert.isPending ? tCommon("saving") : tCommon("save")}
      </Button>
    </Card>
  );
}
