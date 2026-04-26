"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
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

  // --- Indexation computed values ---
  const effectiveChunkingStrategy = chunkingStrategy ?? project.chunking_strategy;
  const effectiveParentChildChunking = parentChildChunking ?? project.parent_child_chunking;
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
  const effectiveEmbeddingBackend = embeddingBackend === undefined ? (project.embedding_backend ?? "") : embeddingBackend;
  const effectiveLlmBackend = llmBackend === undefined ? (project.llm_backend ?? "") : llmBackend;
  const effectiveEmbeddingModel = effectiveEmbeddingBackend === "" ? "" : (embeddingModel ?? (project.embedding_model ?? ""));
  const effectiveLlmModel = effectiveLlmBackend === "" ? "" : (llmModel ?? (project.llm_model ?? ""));
  const storedEmbeddingCredentialId = project.organization_id
    ? (project.org_embedding_api_key_credential_id ?? "")
    : (project.embedding_api_key_credential_id ?? "");
  const storedLlmCredentialId = project.organization_id
    ? (project.org_llm_api_key_credential_id ?? "")
    : (project.llm_api_key_credential_id ?? "");
  const effectiveEmbeddingCredentialId = effectiveEmbeddingBackend === "" ? "" : (embeddingCredentialId ?? storedEmbeddingCredentialId);
  const effectiveLlmCredentialId = effectiveLlmBackend === "" ? "" : (llmCredentialId ?? storedLlmCredentialId);

  const credentialsByProvider = (credentials ?? [])
    .filter((c) => c.is_active)
    .reduce<Record<ModelProvider, Array<{ id: string; masked_key: string }>>>(
      (acc, c) => { acc[c.provider].push({ id: c.id, masked_key: c.masked_key }); return acc; },
      { openai: [], gemini: [], anthropic: [] },
    );
  const embeddingProviderForHints = effectiveEmbeddingBackend === "openai" || effectiveEmbeddingBackend === "gemini" ? effectiveEmbeddingBackend : null;
  const llmProviderForHints = effectiveLlmBackend === "openai" || effectiveLlmBackend === "gemini" || effectiveLlmBackend === "anthropic" ? effectiveLlmBackend : null;
  const embeddingCredentialOptions = embeddingProviderForHints ? credentialsByProvider[embeddingProviderForHints] : [];
  const llmCredentialOptions = llmProviderForHints ? credentialsByProvider[llmProviderForHints] : [];
  const embeddingModelOptions = effectiveEmbeddingBackend ? (modelCatalog?.embedding[effectiveEmbeddingBackend as ProjectEmbeddingBackend] ?? []) : [];
  const llmModelOptions = effectiveLlmBackend ? (modelCatalog?.llm[effectiveLlmBackend as ProjectLLMBackend] ?? []) : [];

  const hasModelsChanges =
    effectiveEmbeddingBackend !== (project.embedding_backend ?? "") ||
    effectiveEmbeddingModel !== (project.embedding_model ?? "") ||
    effectiveLlmBackend !== (project.llm_backend ?? "") ||
    effectiveLlmModel !== (project.llm_model ?? "") ||
    effectiveEmbeddingCredentialId !== "" ||
    effectiveLlmCredentialId !== "";

  // --- Retrieval computed values ---
  const effectiveRetrievalStrategy = retrievalStrategy ?? (project.retrieval_strategy ?? "hybrid");
  const effectiveRetrievalTopK = retrievalTopK ?? project.retrieval_top_k ?? 8;
  const effectiveRetrievalMinScore = retrievalMinScore ?? project.retrieval_min_score ?? 0.3;

  const hasRetrievalChanges =
    effectiveRetrievalStrategy !== (project.retrieval_strategy ?? "hybrid") ||
    effectiveRetrievalTopK !== (project.retrieval_top_k ?? 8) ||
    effectiveRetrievalMinScore !== (project.retrieval_min_score ?? 0.3);

  // --- Augmentation computed values ---
  const effectiveRerankingEnabled = rerankingEnabled ?? project.reranking_enabled ?? false;
  const effectiveRerankerBackend = rerankerBackend ?? project.reranker_backend ?? "none";
  const effectiveRerankerModel = rerankerModel ?? project.reranker_model ?? "";
  const effectiveRerankerCandidateMultiplier = rerankerCandidateMultiplier ?? project.reranker_candidate_multiplier ?? 3;
  const rerankerModelOptions = modelCatalog?.reranker[effectiveRerankerBackend as ProjectRerankerBackend] ?? [];

  const hasAugmentationChanges =
    effectiveRerankingEnabled !== (project.reranking_enabled ?? false) ||
    effectiveRerankerBackend !== (project.reranker_backend ?? "none") ||
    effectiveRerankerModel !== (project.reranker_model ?? "") ||
    effectiveRerankerCandidateMultiplier !== (project.reranker_candidate_multiplier ?? 3);

  // --- History computed values ---
  const effectiveChatHistoryWindowSize = chatHistoryWindowSize ?? project.chat_history_window_size ?? 8;
  const effectiveChatHistoryMaxChars = chatHistoryMaxChars ?? project.chat_history_max_chars ?? 4000;

  const hasHistoryChanges =
    effectiveChatHistoryWindowSize !== (project.chat_history_window_size ?? 8) ||
    effectiveChatHistoryMaxChars !== (project.chat_history_max_chars ?? 4000);

  return (
    <div className="max-w-3xl space-y-10">

      {/* Models */}
      <div className="space-y-4">
        <h2 className="text-base font-semibold tracking-tight">{t("models.embeddingTitle")}</h2>
        <p className="text-sm text-muted-foreground">{t("models.embeddingDescription")}</p>
        <div className="space-y-2">
          <Label htmlFor="embeddingBackend">{t("models.embeddingBackendLabel")}</Label>
          <select id="embeddingBackend" value={effectiveEmbeddingBackend}
            onChange={(e) => { setEmbeddingBackend((e.target.value || "") as ProjectEmbeddingBackend | ""); setEmbeddingModel(""); setEmbeddingCredentialId(""); }}
            className="border-input bg-background w-full rounded-md border px-3 py-2 text-sm"
          >
            <option value="">Default</option>
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
        <h2 className="text-base font-semibold tracking-tight">{t("models.llmTitle")}</h2>
        <p className="text-sm text-muted-foreground">{t("models.llmDescription")}</p>
        <div className="space-y-2">
          <Label htmlFor="llmBackend">{t("models.llmBackendLabel")}</Label>
          <select id="llmBackend" value={effectiveLlmBackend}
            onChange={(e) => { setLlmBackend((e.target.value || "") as ProjectLLMBackend | ""); setLlmModel(""); setLlmCredentialId(""); }}
            className="border-input bg-background w-full rounded-md border px-3 py-2 text-sm"
          >
            <option value="">Default</option>
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
        <Button className="cursor-pointer" disabled={!hasModelsChanges || updateProject.isPending}
          onClick={() => updateProject.mutate(
            { embedding_backend: effectiveEmbeddingBackend || null, embedding_model: effectiveEmbeddingModel || null, embedding_api_key: null, embedding_api_key_credential_id: effectiveEmbeddingCredentialId || null, llm_backend: effectiveLlmBackend || null, llm_model: effectiveLlmModel || null, llm_api_key: null, llm_api_key_credential_id: effectiveLlmCredentialId || null },
            { onSuccess: () => toast.success(t("updateSuccess")), onError: () => toast.error(t("updateError")) },
          )}
        >
          {updateProject.isPending ? tCommon("saving") : t("saveChanges")}
        </Button>
      </div>

      <hr className="border-border" />

      {/* Indexation */}
      <div className="space-y-4">
        <h2 className="text-base font-semibold tracking-tight">{t("knowledgeIndexing.title")}</h2>

        {isProjectReindexing && (
          <div className="rounded-md border border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-900">
            {t("reindexingWarning", { progress: project.reindex_progress, total: project.reindex_total })}
          </div>
        )}

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
        <Button className="cursor-pointer" disabled={!hasIndexingChanges || updateProject.isPending} onClick={handleIndexingSave}>
          {updateProject.isPending ? tCommon("saving") : t("saveChanges")}
        </Button>
        <div className="space-y-3 rounded-md border p-4">
          <p className="text-base font-semibold tracking-tight">{t("knowledgeIndexing.reindexTitle")}</p>
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

      <hr className="border-border" />

      {/* Retrieval */}
      <div className="space-y-4">
        <h2 className="text-base font-semibold tracking-tight">{t("contextRetrieval.title")}</h2>
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
        <Button className="cursor-pointer" disabled={!hasRetrievalChanges || updateProject.isPending}
          onClick={() => updateProject.mutate(
            { retrieval_strategy: effectiveRetrievalStrategy, retrieval_top_k: effectiveRetrievalTopK, retrieval_min_score: effectiveRetrievalMinScore },
            { onSuccess: () => toast.success(t("updateSuccess")), onError: () => toast.error(t("updateError")) },
          )}
        >
          {updateProject.isPending ? tCommon("saving") : t("saveChanges")}
        </Button>
      </div>

      <hr className="border-border" />

      {/* Augmentation */}
      <div className="space-y-4">
        <h2 className="text-base font-semibold tracking-tight">{t("contextAugmentation.title")}</h2>
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
        <Button className="cursor-pointer" disabled={!hasAugmentationChanges || updateProject.isPending}
          onClick={() => updateProject.mutate(
            { reranking_enabled: effectiveRerankingEnabled, reranker_backend: effectiveRerankerBackend, reranker_model: effectiveRerankerModel || null, reranker_candidate_multiplier: effectiveRerankerCandidateMultiplier },
            { onSuccess: () => toast.success(t("updateSuccess")), onError: () => toast.error(t("updateError")) },
          )}
        >
          {updateProject.isPending ? tCommon("saving") : t("saveChanges")}
        </Button>
      </div>

      <hr className="border-border" />

      {/* Chat history */}
      <div className="space-y-4">
        <h2 className="text-base font-semibold tracking-tight">{t("answerGeneration.historyTitle")}</h2>
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
        <Button className="cursor-pointer" disabled={!hasHistoryChanges || updateProject.isPending}
          onClick={() => updateProject.mutate(
            { chat_history_window_size: effectiveChatHistoryWindowSize, chat_history_max_chars: effectiveChatHistoryMaxChars },
            { onSuccess: () => toast.success(t("updateSuccess")), onError: () => toast.error(t("updateError")) },
          )}
        >
          {updateProject.isPending ? tCommon("saving") : t("saveChanges")}
        </Button>
      </div>

      <hr className="border-border" />

      {/* Versions */}
      <div className="space-y-4">
        <h2 className="text-base font-semibold tracking-tight">{t("tabs.history")}</h2>
        <ProjectSnapshotsList projectId={projectId} />
      </div>

      <hr className="border-border" />

      {/* Danger zone */}
      <div className="space-y-3 rounded-md border border-destructive/30 p-4">
        <p className="text-base font-semibold tracking-tight">{t("general.deleteTitle")}</p>
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
