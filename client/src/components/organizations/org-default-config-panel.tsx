"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
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

const SELECT_CLASS =
  "flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus:outline-none focus:ring-1 focus:ring-ring";

type OrgDefaultConfigPanelProps = {
  organizationId: string;
};

export function OrgDefaultConfigPanel({ organizationId }: OrgDefaultConfigPanelProps) {
  const t = useTranslations("organizations.defaultConfig");
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

function OrgDefaultConfigForm({
  organizationId,
  config,
  credentials,
}: OrgDefaultConfigFormProps) {
  const t = useTranslations("organizations.defaultConfig");
  const tCommon = useTranslations("common");
  const upsert = useUpsertOrganizationDefaultConfig(organizationId);

  const [embeddingBackend, setEmbeddingBackend] = useState(config?.embedding_backend ?? "");
  const [llmBackend, setLlmBackend] = useState(config?.llm_backend ?? "");
  const [chunkingStrategy, setChunkingStrategy] = useState(
    config?.chunking_strategy ?? "",
  );
  const [retrievalStrategy, setRetrievalStrategy] = useState(
    config?.retrieval_strategy ?? "",
  );
  const [retrievalTopK, setRetrievalTopK] = useState(
    config?.retrieval_top_k?.toString() ?? "",
  );
  const [retrievalMinScore, setRetrievalMinScore] = useState(
    config?.retrieval_min_score?.toString() ?? "",
  );
  const [rerankingEnabled, setRerankingEnabled] = useState(
    config?.reranking_enabled ?? false,
  );
  const [rerankerBackend, setRerankerBackend] = useState(config?.reranker_backend ?? "");
  const [orgEmbeddingCredId, setOrgEmbeddingCredId] = useState(
    config?.org_embedding_api_key_credential_id ?? "",
  );
  const [orgLlmCredId, setOrgLlmCredId] = useState(
    config?.org_llm_api_key_credential_id ?? "",
  );

  useEffect(() => {
    if (!rerankingEnabled) setRerankerBackend("");
  }, [rerankingEnabled]);

  function handleSave() {
    upsert.mutate(
      {
        embedding_backend: embeddingBackend || null,
        llm_backend: llmBackend || null,
        chunking_strategy: (chunkingStrategy as ChunkingStrategy) || null,
        retrieval_strategy: (retrievalStrategy as RetrievalStrategy) || null,
        retrieval_top_k: retrievalTopK ? parseInt(retrievalTopK, 10) : null,
        retrieval_min_score: retrievalMinScore ? parseFloat(retrievalMinScore) : null,
        reranking_enabled: rerankingEnabled,
        reranker_backend: rerankerBackend || null,
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
  const llmCredentials = credentials;

  return (
    <Card className="space-y-6 p-5">
      <div className="space-y-1">
        <h2 className="text-lg font-medium">{t("title")}</h2>
        <p className="text-sm text-muted-foreground">{t("description")}</p>
      </div>

      <div className="grid gap-5 sm:grid-cols-2">
        {/* Embedding backend */}
        <div className="space-y-2">
          <Label htmlFor="cfg-embedding-backend">{t("embeddingBackendLabel")}</Label>
          <select
            id="cfg-embedding-backend"
            value={embeddingBackend}
            onChange={(e) => setEmbeddingBackend(e.target.value)}
            className={SELECT_CLASS}
          >
            <option value="">{t("noDefault")}</option>
            <option value="openai">OpenAI</option>
            <option value="gemini">Gemini</option>
            <option value="ollama">Ollama</option>
          </select>
        </div>

        {/* LLM backend */}
        <div className="space-y-2">
          <Label htmlFor="cfg-llm-backend">{t("llmBackendLabel")}</Label>
          <select
            id="cfg-llm-backend"
            value={llmBackend}
            onChange={(e) => setLlmBackend(e.target.value)}
            className={SELECT_CLASS}
          >
            <option value="">{t("noDefault")}</option>
            <option value="openai">OpenAI</option>
            <option value="gemini">Gemini</option>
            <option value="anthropic">Anthropic</option>
            <option value="ollama">Ollama</option>
          </select>
        </div>

        {/* Org embedding credential */}
        <div className="space-y-2">
          <Label htmlFor="cfg-emb-cred">{t("orgEmbeddingCredLabel")}</Label>
          <select
            id="cfg-emb-cred"
            value={orgEmbeddingCredId}
            onChange={(e) => setOrgEmbeddingCredId(e.target.value)}
            className={SELECT_CLASS}
          >
            <option value="">{t("noDefault")}</option>
            {embeddingCredentials.map((c) => (
              <option key={c.id} value={c.id}>
                {c.provider} — {c.masked_key}
              </option>
            ))}
          </select>
        </div>

        {/* Org LLM credential */}
        <div className="space-y-2">
          <Label htmlFor="cfg-llm-cred">{t("orgLlmCredLabel")}</Label>
          <select
            id="cfg-llm-cred"
            value={orgLlmCredId}
            onChange={(e) => setOrgLlmCredId(e.target.value)}
            className={SELECT_CLASS}
          >
            <option value="">{t("noDefault")}</option>
            {llmCredentials.map((c) => (
              <option key={c.id} value={c.id}>
                {c.provider} — {c.masked_key}
              </option>
            ))}
          </select>
        </div>

        {/* Chunking strategy */}
        <div className="space-y-2">
          <Label htmlFor="cfg-chunking">{t("chunkingStrategyLabel")}</Label>
          <select
            id="cfg-chunking"
            value={chunkingStrategy}
            onChange={(e) => setChunkingStrategy(e.target.value)}
            className={SELECT_CLASS}
          >
            <option value="">{t("noDefault")}</option>
            <option value="auto">Auto</option>
            <option value="fixed_window">Fixed window</option>
            <option value="paragraph">Paragraph</option>
            <option value="heading_section">Heading section</option>
            <option value="semantic">Semantic</option>
          </select>
        </div>

        {/* Retrieval strategy */}
        <div className="space-y-2">
          <Label htmlFor="cfg-retrieval">{t("retrievalStrategyLabel")}</Label>
          <select
            id="cfg-retrieval"
            value={retrievalStrategy}
            onChange={(e) => setRetrievalStrategy(e.target.value)}
            className={SELECT_CLASS}
          >
            <option value="">{t("noDefault")}</option>
            <option value="vector">Vector</option>
            <option value="fulltext">Full-text</option>
            <option value="hybrid">Hybrid</option>
          </select>
        </div>

        {/* Retrieval top-k */}
        <div className="space-y-2">
          <Label htmlFor="cfg-top-k">{t("retrievalTopKLabel")}</Label>
          <input
            id="cfg-top-k"
            type="number"
            min={1}
            max={50}
            value={retrievalTopK}
            onChange={(e) => setRetrievalTopK(e.target.value)}
            placeholder={t("noDefault")}
            className={SELECT_CLASS}
          />
        </div>

        {/* Retrieval min score */}
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
            placeholder={t("noDefault")}
            className={SELECT_CLASS}
          />
        </div>
      </div>

      {/* Reranking */}
      <div className="space-y-3 rounded-md border p-4">
        <div className="flex items-center justify-between">
          <div>
            <Label htmlFor="cfg-reranking">{t("rerankingLabel")}</Label>
            <p className="text-xs text-muted-foreground mt-0.5">{t("rerankingHint")}</p>
          </div>
          <Switch
            id="cfg-reranking"
            checked={rerankingEnabled}
            onCheckedChange={setRerankingEnabled}
          />
        </div>

        {rerankingEnabled && (
          <div className="space-y-2">
            <Label htmlFor="cfg-reranker-backend">{t("rerankerBackendLabel")}</Label>
            <select
              id="cfg-reranker-backend"
              value={rerankerBackend}
              onChange={(e) => setRerankerBackend(e.target.value)}
              className={SELECT_CLASS}
            >
              <option value="">{t("noDefault")}</option>
              <option value="cross_encoder">Cross-encoder</option>
              <option value="mmr">MMR</option>
            </select>
          </div>
        )}
      </div>

      <Button
        onClick={handleSave}
        disabled={upsert.isPending}
        className="cursor-pointer"
      >
        {upsert.isPending ? tCommon("saving") : tCommon("save")}
      </Button>
    </Card>
  );
}
