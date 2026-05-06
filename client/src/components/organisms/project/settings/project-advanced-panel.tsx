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
import {
  useDeleteProject,
  useProject,
  useProjectConfiguration,
  useReindexProject,
  useUpdateProjectConfiguration,
} from "@/lib/hooks/use-projects";
import { useModelCatalog } from "@/lib/hooks/use-model-catalog";
import { useModelCredentials } from "@/lib/hooks/use-model-credentials";
import { useOrgModelCredentials } from "@/lib/hooks/use-org-model-credentials";
import { useOrganizationProjectDefaults } from "@/lib/hooks/use-org-project-defaults";
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

  if (!project) return null;

  const isProjectReindexing = project.reindex_status === "in_progress";

  // --- Models computed values ---
  const effectiveEmbeddingBackend = embeddingBackend === undefined
    ? (projectConfig?.embedding_backend ?? "")
    : embeddingBackend;
  const effectiveLlmBackend = llmBackend === undefined
    ? (projectConfig?.llm_backend ?? "")
    : llmBackend;
  const effectiveEmbeddingModel = embeddingModel === undefined
    ? (projectConfig?.embedding_model ?? "")
    : (embeddingModel ?? "");
  const effectiveLlmModel = llmModel === undefined
    ? (projectConfig?.llm_model ?? "")
    : (llmModel ?? "");
  const effectiveEmbeddingCredentialId = embeddingCredentialId === undefined
    ? (projectConfig?.embedding_api_key_credential_id ?? "")
    : (embeddingCredentialId ?? "");
  const effectiveLlmCredentialId = llmCredentialId === undefined
    ? (projectConfig?.llm_api_key_credential_id ?? "")
    : (llmCredentialId ?? "");

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

  const storedEmbeddingBackend = projectConfig?.embedding_backend ?? "";
  const storedLlmBackend = projectConfig?.llm_backend ?? "";
  const storedEmbeddingModel = projectConfig?.embedding_model ?? "";
  const storedLlmModel = projectConfig?.llm_model ?? "";
  const storedEmbeddingCredentialId = projectConfig?.embedding_api_key_credential_id ?? "";
  const storedLlmCredentialId = projectConfig?.llm_api_key_credential_id ?? "";

  const hasModelsChanges =
    effectiveEmbeddingBackend !== storedEmbeddingBackend ||
    effectiveEmbeddingModel !== storedEmbeddingModel ||
    effectiveLlmBackend !== storedLlmBackend ||
    effectiveLlmModel !== storedLlmModel ||
    effectiveEmbeddingCredentialId !== storedEmbeddingCredentialId ||
    effectiveLlmCredentialId !== storedLlmCredentialId;

  const hasModelsConfigured =
    projectConfig?.embedding_backend != null ||
    projectConfig?.llm_backend != null;

  // --- Indexation computed values ---
  const effectiveChunkingStrategy = chunkingStrategy === undefined
    ? (projectConfig?.chunking_strategy as ChunkingStrategy | null ?? null)
    : chunkingStrategy;
  const effectiveParentChildChunking = parentChildChunking === undefined
    ? (projectConfig?.parent_child_chunking ?? false)
    : (parentChildChunking ?? false);

  const storedChunkingStrategy = projectConfig?.chunking_strategy as ChunkingStrategy | null ?? null;
  const storedParentChildChunking = projectConfig?.parent_child_chunking ?? false;

  const hasIndexingChanges =
    effectiveChunkingStrategy !== storedChunkingStrategy ||
    effectiveParentChildChunking !== storedParentChildChunking;
  const isSemanticRecommended = effectiveParentChildChunking && effectiveChunkingStrategy !== "semantic";

  const hasIndexingConfigured =
    projectConfig?.chunking_strategy != null ||
    projectConfig?.parent_child_chunking != null;

  const indexingPayload: UpdateAgentConfigurationRequest = {
    chunking_strategy: effectiveChunkingStrategy,
    parent_child_chunking: effectiveParentChildChunking,
  };

  function handleIndexingSave() {
    const parentChildChanged = effectiveParentChildChunking !== storedParentChildChunking;
    if (parentChildChanged) {
      setPendingIndexingData(indexingPayload);
      setReindexWarningOpen(true);
      return;
    }
    updateProjectConfig.mutate(indexingPayload, {
      onSuccess: () => toast.success(t("updateSuccess")),
      onError: () => toast.error(t("updateError")),
    });
  }

  // --- Retrieval computed values ---
  const effectiveRetrievalStrategy = retrievalStrategy === undefined
    ? (projectConfig?.retrieval_strategy as RetrievalStrategy | null ?? null)
    : retrievalStrategy;
  const effectiveRetrievalTopK = retrievalTopK === undefined
    ? projectConfig?.retrieval_top_k ?? null
    : retrievalTopK;
  const effectiveRetrievalMinScore = retrievalMinScore === undefined
    ? projectConfig?.retrieval_min_score ?? null
    : retrievalMinScore;

  const storedRetrievalStrategy = projectConfig?.retrieval_strategy as RetrievalStrategy | null ?? null;
  const storedRetrievalTopK = projectConfig?.retrieval_top_k ?? null;
  const storedRetrievalMinScore = projectConfig?.retrieval_min_score ?? null;

  const hasRetrievalChanges =
    effectiveRetrievalStrategy !== storedRetrievalStrategy ||
    effectiveRetrievalTopK !== storedRetrievalTopK ||
    effectiveRetrievalMinScore !== storedRetrievalMinScore;

  const hasRetrievalConfigured =
    projectConfig?.retrieval_strategy != null ||
    projectConfig?.retrieval_top_k != null ||
    projectConfig?.retrieval_min_score != null;

  // --- Augmentation computed values ---
  const effectiveRerankingEnabled = rerankingEnabled === undefined
    ? (projectConfig?.reranking_enabled ?? false)
    : (rerankingEnabled ?? false);
  const effectiveRerankerBackend = rerankerBackend === undefined
    ? (projectConfig?.reranker_backend as ProjectRerankerBackend | null ?? null)
    : rerankerBackend;
  const effectiveRerankerModel = rerankerModel === undefined
    ? (projectConfig?.reranker_model ?? "")
    : (rerankerModel ?? "");
  const effectiveRerankerCandidateMultiplier = rerankerCandidateMultiplier === undefined
    ? projectConfig?.reranker_candidate_multiplier ?? null
    : rerankerCandidateMultiplier;

  const storedRerankingEnabled = projectConfig?.reranking_enabled ?? false;
  const storedRerankerBackend = projectConfig?.reranker_backend as ProjectRerankerBackend | null ?? null;
  const storedRerankerModel = projectConfig?.reranker_model ?? "";
  const storedRerankerCandidateMultiplier = projectConfig?.reranker_candidate_multiplier ?? null;

  const rerankerModelOptions = modelCatalog?.reranker[effectiveRerankerBackend as ProjectRerankerBackend] ?? [];

  const hasAugmentationChanges =
    effectiveRerankingEnabled !== storedRerankingEnabled ||
    effectiveRerankerBackend !== storedRerankerBackend ||
    effectiveRerankerModel !== storedRerankerModel ||
    effectiveRerankerCandidateMultiplier !== storedRerankerCandidateMultiplier;

  const hasRerankingConfigured =
    projectConfig?.reranking_enabled != null ||
    projectConfig?.reranker_backend != null;

  // --- History computed values ---
  const effectiveChatHistoryWindowSize = chatHistoryWindowSize === undefined
    ? projectConfig?.chat_history_window_size ?? null
    : chatHistoryWindowSize;
  const effectiveChatHistoryMaxChars = chatHistoryMaxChars === undefined
    ? projectConfig?.chat_history_max_chars ?? null
    : chatHistoryMaxChars;

  const storedChatHistoryWindowSize = projectConfig?.chat_history_window_size ?? null;
  const storedChatHistoryMaxChars = projectConfig?.chat_history_max_chars ?? null;

  const hasHistoryChanges =
    effectiveChatHistoryWindowSize !== storedChatHistoryWindowSize ||
    effectiveChatHistoryMaxChars !== storedChatHistoryMaxChars;

  const hasHistoryConfigured =
    projectConfig?.chat_history_window_size != null ||
    projectConfig?.chat_history_max_chars != null;

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
                {(!hasModelsConfigured && systemDefaults) && (
                  <p className="text-xs text-foreground">{t("systemDefaultsApplied")}</p>
                )}
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
                    <option value="">{inheritedDefaults?.embedding_backend ? `— (${inheritedDefaults.embedding_backend})` : "—"}</option>
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
                    <option value="">{inheritedDefaults?.llm_backend ? `— (${inheritedDefaults.llm_backend})` : "—"}</option>
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
                <div className="flex gap-2">
                  <Button className="cursor-pointer" disabled={!hasModelsChanges || updateProjectConfig.isPending}
                    onClick={() => updateProjectConfig.mutate(
                      {
                        embedding_backend: (effectiveEmbeddingBackend || null),
                        embedding_model: effectiveEmbeddingModel || null,
                        embedding_api_key_credential_id: effectiveEmbeddingCredentialId || null,
                        llm_backend: (effectiveLlmBackend || null),
                        llm_model: effectiveLlmModel || null,
                        llm_api_key_credential_id: effectiveLlmCredentialId || null,
                      },
                      { onSuccess: () => toast.success(t("updateSuccess")), onError: () => toast.error(t("updateError")) },
                    )}
                  >
                    {updateProjectConfig.isPending ? tCommon("saving") : t("saveChanges")}
                  </Button>
                  {hasModelsConfigured && (
                    <Button variant="outline" className="cursor-pointer" disabled={updateProjectConfig.isPending}
                      onClick={() => updateProjectConfig.mutate(
                        { embedding_backend: null, embedding_model: null, embedding_api_key_credential_id: null, llm_backend: null, llm_model: null, llm_api_key_credential_id: null },
                        { onSuccess: () => toast.success(t("updateSuccess")), onError: () => toast.error(t("updateError")) },
                      )}
                    >
                      {t("resetToInherited")}
                    </Button>
                  )}
                </div>
              </div>
            </AccordionContent>
          </AccordionItem>

          {/* Indexation */}
          <AccordionItem value="indexing">
            <AccordionTrigger className="text-base">{t("tabs.knowledgeIndexing")}</AccordionTrigger>
            <AccordionContent>
              <div className="space-y-4">
                {isProjectReindexing && (
                  <div className="rounded-md border border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-900">
                    {t("reindexingWarning", { progress: project.reindex_progress, total: project.reindex_total })}
                  </div>
                )}
                <div className="space-y-2">
                  <Label htmlFor="chunkingStrategy">{t("knowledgeIndexing.chunkingLabel")}</Label>
                  <select id="chunkingStrategy" value={effectiveChunkingStrategy ?? ""}
                    onChange={(e) => setChunkingStrategy((e.target.value as ChunkingStrategy) || null)}
                    className="border-input bg-background w-full rounded-md border px-3 py-2 text-sm"
                  >
                    <option value="">{inheritedDefaults?.chunking_strategy ? `— (${inheritedDefaults.chunking_strategy})` : "—"}</option>
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
                <div className="flex gap-2">
                  <Button className="cursor-pointer" disabled={!hasIndexingChanges || updateProjectConfig.isPending} onClick={handleIndexingSave}>
                    {updateProjectConfig.isPending ? tCommon("saving") : t("saveChanges")}
                  </Button>
                  {hasIndexingConfigured && (
                    <Button variant="outline" className="cursor-pointer" disabled={updateProjectConfig.isPending}
                      onClick={() => updateProjectConfig.mutate(
                        { chunking_strategy: null, parent_child_chunking: null },
                        { onSuccess: () => toast.success(t("updateSuccess")), onError: () => toast.error(t("updateError")) },
                      )}
                    >
                      {t("resetToInherited")}
                    </Button>
                  )}
                </div>
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
                {(!hasRetrievalConfigured && systemDefaults) && (
                  <p className="text-xs text-foreground">{t("systemDefaultsApplied")}</p>
                )}
                <p className="text-sm text-muted-foreground">{t("contextRetrieval.description")}</p>
                <div className="space-y-2">
                  <Label htmlFor="retrievalStrategy">{t("contextRetrieval.searchTypeLabel")}</Label>
                  <select id="retrievalStrategy" value={effectiveRetrievalStrategy ?? ""}
                    onChange={(e) => setRetrievalStrategy((e.target.value as RetrievalStrategy) || null)}
                    className="border-input bg-background w-full rounded-md border px-3 py-2 text-sm"
                  >
                    <option value="">{inheritedDefaults?.retrieval_strategy ? `— (${inheritedDefaults.retrieval_strategy})` : `— (${systemDefaults?.retrieval_strategy ?? "hybrid"})`}</option>
                    <option value="hybrid">{t("contextRetrieval.hybrid")}</option>
                    <option value="vector">{t("contextRetrieval.vector")}</option>
                    <option value="fulltext">{t("contextRetrieval.fulltext")}</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="retrievalTopK">{t("contextRetrieval.topKLabel")}</Label>
                  <Input id="retrievalTopK" type="number" min={1} max={40}
                    value={effectiveRetrievalTopK ?? ""}
                    placeholder={String(inheritedDefaults?.retrieval_top_k ?? systemDefaults?.retrieval_top_k ?? 8)}
                    onChange={(e) => { const v = Number.parseInt(e.target.value, 10); setRetrievalTopK(Number.isNaN(v) ? null : Math.max(1, Math.min(40, v))); }}
                  />
                  <p className="text-xs text-muted-foreground">{t("contextRetrieval.topKNote")}</p>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="retrievalMinScore">{t("contextRetrieval.minScoreLabel")}</Label>
                  <Input id="retrievalMinScore" type="number" min={0} max={1} step={0.05}
                    value={effectiveRetrievalMinScore ?? ""}
                    placeholder={String(inheritedDefaults?.retrieval_min_score ?? systemDefaults?.retrieval_min_score ?? 0.3)}
                    onChange={(e) => { const v = Number.parseFloat(e.target.value); setRetrievalMinScore(Number.isNaN(v) ? null : Math.round(Math.max(0, Math.min(1, v)) * 100) / 100); }}
                  />
                  <p className="text-xs text-muted-foreground">{t("contextRetrieval.minScoreNote")}</p>
                </div>
                <div className="flex gap-2">
                  <Button className="cursor-pointer" disabled={!hasRetrievalChanges || updateProjectConfig.isPending}
                    onClick={() => updateProjectConfig.mutate(
                      { retrieval_strategy: effectiveRetrievalStrategy, retrieval_top_k: effectiveRetrievalTopK, retrieval_min_score: effectiveRetrievalMinScore },
                      { onSuccess: () => toast.success(t("updateSuccess")), onError: () => toast.error(t("updateError")) },
                    )}
                  >
                    {updateProjectConfig.isPending ? tCommon("saving") : t("saveChanges")}
                  </Button>
                  {hasRetrievalConfigured && (
                    <Button variant="outline" className="cursor-pointer" disabled={updateProjectConfig.isPending}
                      onClick={() => updateProjectConfig.mutate(
                        { retrieval_strategy: null, retrieval_top_k: null, retrieval_min_score: null },
                        { onSuccess: () => toast.success(t("updateSuccess")), onError: () => toast.error(t("updateError")) },
                      )}
                    >
                      {t("resetToInherited")}
                    </Button>
                  )}
                </div>
              </div>
            </AccordionContent>
          </AccordionItem>

          {/* Augmentation */}
          <AccordionItem value="augmentation">
            <AccordionTrigger className="text-base">{t("tabs.contextAugmentation")}</AccordionTrigger>
            <AccordionContent>
              <div className="space-y-4">
                {(!hasRerankingConfigured && systemDefaults) && (
                  <p className="text-xs text-foreground">{t("systemDefaultsApplied")}</p>
                )}
                <div className="flex items-center gap-2">
                  <Switch id="rerankingEnabled" checked={effectiveRerankingEnabled} onCheckedChange={setRerankingEnabled} />
                  <Label htmlFor="rerankingEnabled">{t("contextAugmentation.rerankingLabel")}</Label>
                </div>
                {effectiveRerankingEnabled && (
                  <>
                    <div className="space-y-2">
                      <Label htmlFor="rerankerBackend">{t("contextAugmentation.rerankerBackendLabel")}</Label>
                      <select id="rerankerBackend" value={effectiveRerankerBackend ?? ""}
                        onChange={(e) => { setRerankerBackend((e.target.value as ProjectRerankerBackend) || null); setRerankerModel(""); }}
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
                        disabled={effectiveRerankerBackend === "none" || effectiveRerankerBackend === null}
                        className="border-input bg-background w-full rounded-md border px-3 py-2 text-sm disabled:opacity-60"
                      >
                        <option value="">{effectiveRerankerBackend === "none" || effectiveRerankerBackend === null ? t("contextAugmentation.selectRerankerBackend") : t("contextAugmentation.selectModel")}</option>
                        {rerankerModelOptions.map((m) => <option key={m.id} value={m.id}>{m.label}</option>)}
                      </select>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="rerankerCandidateMultiplier">{t("contextAugmentation.candidateMultiplierLabel")}</Label>
                      <Input id="rerankerCandidateMultiplier" type="number" min={1} max={10}
                        value={effectiveRerankerCandidateMultiplier ?? ""}
                        placeholder={String(inheritedDefaults?.reranker_candidate_multiplier ?? systemDefaults?.reranker_candidate_multiplier ?? 3)}
                        onChange={(e) => { const v = Number.parseInt(e.target.value, 10); setRerankerCandidateMultiplier(Number.isNaN(v) ? null : Math.max(1, Math.min(10, v))); }}
                      />
                      <p className="text-xs text-muted-foreground">{t("contextAugmentation.candidateMultiplierNote")}</p>
                    </div>
                  </>
                )}
                <div className="flex gap-2">
                  <Button className="cursor-pointer" disabled={!hasAugmentationChanges || updateProjectConfig.isPending}
                    onClick={() => updateProjectConfig.mutate(
                      { reranking_enabled: effectiveRerankingEnabled, reranker_backend: effectiveRerankerBackend, reranker_model: effectiveRerankerModel || null, reranker_candidate_multiplier: effectiveRerankerCandidateMultiplier },
                      { onSuccess: () => toast.success(t("updateSuccess")), onError: () => toast.error(t("updateError")) },
                    )}
                  >
                    {updateProjectConfig.isPending ? tCommon("saving") : t("saveChanges")}
                  </Button>
                  {hasRerankingConfigured && (
                    <Button variant="outline" className="cursor-pointer" disabled={updateProjectConfig.isPending}
                      onClick={() => updateProjectConfig.mutate(
                        { reranking_enabled: null, reranker_backend: null, reranker_model: null, reranker_candidate_multiplier: null },
                        { onSuccess: () => toast.success(t("updateSuccess")), onError: () => toast.error(t("updateError")) },
                      )}
                    >
                      {t("resetToInherited")}
                    </Button>
                  )}
                </div>
              </div>
            </AccordionContent>
          </AccordionItem>

          {/* Chat history */}
          <AccordionItem value="history">
            <AccordionTrigger className="text-base">{t("tabs.answerGeneration")}</AccordionTrigger>
            <AccordionContent>
              <div className="space-y-4">
                {(!hasHistoryConfigured && systemDefaults) && (
                  <p className="text-xs text-foreground">{t("systemDefaultsApplied")}</p>
                )}
                <div className="space-y-2">
                  <Label htmlFor="chatHistoryWindowSize">{t("answerGeneration.chatHistoryWindowLabel")}</Label>
                  <Input id="chatHistoryWindowSize" type="number" min={1} max={40}
                    value={effectiveChatHistoryWindowSize ?? ""}
                    placeholder={String(inheritedDefaults?.chat_history_window_size ?? systemDefaults?.chat_history_window_size ?? 8)}
                    onChange={(e) => { const v = Number.parseInt(e.target.value, 10); setChatHistoryWindowSize(Number.isNaN(v) ? null : Math.max(1, Math.min(40, v))); }}
                  />
                  <p className="text-xs text-muted-foreground">{t("answerGeneration.chatHistoryWindowNote")}</p>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="chatHistoryMaxChars">{t("answerGeneration.chatHistoryMaxCharsLabel")}</Label>
                  <Input id="chatHistoryMaxChars" type="number" min={128} max={16000}
                    value={effectiveChatHistoryMaxChars ?? ""}
                    placeholder={String(inheritedDefaults?.chat_history_max_chars ?? systemDefaults?.chat_history_max_chars ?? 4000)}
                    onChange={(e) => { const v = Number.parseInt(e.target.value, 10); setChatHistoryMaxChars(Number.isNaN(v) ? null : Math.max(128, Math.min(16000, v))); }}
                  />
                  <p className="text-xs text-muted-foreground">{t("answerGeneration.chatHistoryMaxCharsNote")}</p>
                </div>
                <div className="flex gap-2">
                  <Button className="cursor-pointer" disabled={!hasHistoryChanges || updateProjectConfig.isPending}
                    onClick={() => updateProjectConfig.mutate(
                      { chat_history_window_size: effectiveChatHistoryWindowSize, chat_history_max_chars: effectiveChatHistoryMaxChars },
                      { onSuccess: () => toast.success(t("updateSuccess")), onError: () => toast.error(t("updateError")) },
                    )}
                  >
                    {updateProjectConfig.isPending ? tCommon("saving") : t("saveChanges")}
                  </Button>
                  {hasHistoryConfigured && (
                    <Button variant="outline" className="cursor-pointer" disabled={updateProjectConfig.isPending}
                      onClick={() => updateProjectConfig.mutate(
                        { chat_history_window_size: null, chat_history_max_chars: null },
                        { onSuccess: () => toast.success(t("updateSuccess")), onError: () => toast.error(t("updateError")) },
                      )}
                    >
                      {t("resetToInherited")}
                    </Button>
                  )}
                </div>
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
              updateProjectConfig.mutate(pendingIndexingData, {
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
