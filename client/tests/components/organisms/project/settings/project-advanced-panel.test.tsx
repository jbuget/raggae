import { http, HttpResponse } from "msw";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { ProjectAdvancedPanel } from "@/components/organisms/project/settings/project-advanced-panel";
import type { AgentConfigurationResponse } from "@/lib/types/api";
import { renderWithProviders } from "../../../../helpers/render";
import { server } from "../../../../helpers/msw-server";

vi.mock("@/lib/hooks/use-auth", () => ({
  useAuth: () => ({ token: "mock-token", user: { id: "user-1" } }),
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
}));

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------

const PROJECT_ID = "proj-1";
const ORG_ID = "org-1";

const userProject = {
  id: PROJECT_ID,
  user_id: "user-1",
  organization_id: null,
  name: "Test Project",
  description: "",
  system_prompt: "",
  is_published: false,
  created_at: "2026-01-01T00:00:00Z",
  reindex_status: "idle",
  reindex_progress: 0,
  reindex_total: 0,
};

const orgProject = { ...userProject, organization_id: ORG_ID };

const emptyConfig: AgentConfigurationResponse = {
  owner_id: PROJECT_ID,
  embedding_backend: null,
  embedding_model: null,
  embedding_api_key_credential_id: null,
  llm_backend: null,
  llm_model: null,
  llm_api_key_credential_id: null,
  chunking_strategy: null,
  parent_child_chunking: null,
  retrieval_strategy: null,
  retrieval_top_k: null,
  retrieval_min_score: null,
  reranking_enabled: null,
  reranker_backend: null,
  reranker_model: null,
  reranker_candidate_multiplier: null,
  chat_history_window_size: null,
  chat_history_max_chars: null,
};

const systemDefaults = {
  llm_backend: "gemini",
  llm_model: "gemini-1.5-flash",
  embedding_backend: "gemini",
  embedding_model: "text-embedding-004",
  chunking_strategy: "auto",
  parent_child_chunking: false,
  retrieval_strategy: "hybrid",
  retrieval_top_k: 8,
  retrieval_min_score: 0.3,
  reranker_backend: null,
  reranker_model: null,
  reranker_candidate_multiplier: 3,
  chat_history_window_size: 8,
  chat_history_max_chars: 4000,
};

const emptyModelCatalog = {
  embedding: { gemini: [], openai: [], ollama: [], inmemory: [] },
  llm: { gemini: [], openai: [], anthropic: [], ollama: [], inmemory: [] },
  reranker: { none: [], cross_encoder: [], inmemory: [], mmr: [] },
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

interface SetupOptions {
  project?: typeof userProject | typeof orgProject;
  projectConfig?: AgentConfigurationResponse;
  userDefaults?: object | null;
  orgDefaults?: object | null;
}

function setup({
  project = userProject,
  projectConfig = emptyConfig,
  userDefaults = null,
  orgDefaults = null,
}: SetupOptions = {}) {
  server.use(
    http.get(`/api/v1/projects/${PROJECT_ID}`, () => HttpResponse.json(project)),
    http.get(`/api/v1/projects/${PROJECT_ID}/configuration`, () =>
      HttpResponse.json(projectConfig),
    ),
    http.get("/api/v1/system/defaults", () => HttpResponse.json(systemDefaults)),
    http.get("/api/v1/auth/me/project-defaults", () =>
      userDefaults
        ? HttpResponse.json(userDefaults)
        : new HttpResponse(null, { status: 404 }),
    ),
    http.get(`/api/v1/organizations/${ORG_ID}/project-defaults`, () =>
      orgDefaults
        ? HttpResponse.json(orgDefaults)
        : new HttpResponse(null, { status: 404 }),
    ),
    http.get("/api/v1/model-catalog", () => HttpResponse.json(emptyModelCatalog)),
    http.get("/api/v1/model-credentials", () => HttpResponse.json([])),
    http.get(`/api/v1/organizations/${ORG_ID}/model-credentials`, () =>
      HttpResponse.json([]),
    ),
    http.patch(`/api/v1/projects/${PROJECT_ID}/configuration`, () =>
      HttpResponse.json(projectConfig),
    ),
  );
  renderWithProviders(<ProjectAdvancedPanel projectId={PROJECT_ID} />);
}

async function openSection(name: RegExp) {
  const trigger = await screen.findByRole("button", { name });
  await userEvent.click(trigger);
}

// ---------------------------------------------------------------------------
// Field value inheritance tests
// ---------------------------------------------------------------------------

describe("ProjectAdvancedPanel – field values inheritance", () => {
  describe("Retrieval — Top-K input", () => {
    it("shows system default top-k when no parent defaults and no project config", async () => {
      setup({ project: userProject });
      await openSection(/context retrieval/i);
      expect(await screen.findByLabelText(/top-k/i)).toHaveValue(8);
    });

    it("shows user default top-k when user has it and project has none", async () => {
      setup({
        project: userProject,
        userDefaults: { user_id: "user-1", retrieval_top_k: 12 },
      });
      await openSection(/context retrieval/i);
      expect(await screen.findByLabelText(/top-k/i)).toHaveValue(12);
    });

    it("shows org default top-k in org project when project has none", async () => {
      setup({
        project: orgProject,
        orgDefaults: { organization_id: ORG_ID, retrieval_top_k: 15 },
      });
      await openSection(/context retrieval/i);
      expect(await screen.findByLabelText(/top-k/i)).toHaveValue(15);
    });

    it("shows project top-k and ignores user default", async () => {
      setup({
        project: userProject,
        projectConfig: { ...emptyConfig, retrieval_top_k: 20 },
        userDefaults: { user_id: "user-1", retrieval_top_k: 12 },
      });
      await openSection(/context retrieval/i);
      expect(await screen.findByLabelText(/top-k/i)).toHaveValue(20);
    });

    it("shows project top-k and ignores org default", async () => {
      setup({
        project: orgProject,
        projectConfig: { ...emptyConfig, retrieval_top_k: 5 },
        orgDefaults: { organization_id: ORG_ID, retrieval_top_k: 15 },
      });
      await openSection(/context retrieval/i);
      expect(await screen.findByLabelText(/top-k/i)).toHaveValue(5);
    });
  });

  describe("Retrieval — Min score input", () => {
    it("shows system default min score when no parent defaults", async () => {
      setup({ project: userProject });
      await openSection(/context retrieval/i);
      expect(await screen.findByLabelText(/min score/i)).toHaveValue(0.3);
    });

    it("shows user default min score when user has it and project has none", async () => {
      setup({
        project: userProject,
        userDefaults: { user_id: "user-1", retrieval_min_score: 0.7 },
      });
      await openSection(/context retrieval/i);
      expect(await screen.findByLabelText(/min score/i)).toHaveValue(0.7);
    });

    it("shows org default min score in org project when project has none", async () => {
      setup({
        project: orgProject,
        orgDefaults: { organization_id: ORG_ID, retrieval_min_score: 0.6 },
      });
      await openSection(/context retrieval/i);
      expect(await screen.findByLabelText(/min score/i)).toHaveValue(0.6);
    });

    it("shows project min score and ignores user default", async () => {
      setup({
        project: userProject,
        projectConfig: { ...emptyConfig, retrieval_min_score: 0.9 },
        userDefaults: { user_id: "user-1", retrieval_min_score: 0.7 },
      });
      await openSection(/context retrieval/i);
      expect(await screen.findByLabelText(/min score/i)).toHaveValue(0.9);
    });
  });

  describe("Knowledge indexing — Parent-child chunking switch", () => {
    it("shows system default (false) when no parent defaults", async () => {
      setup({ project: userProject });
      await openSection(/knowledge indexing/i);
      const sw = await screen.findByRole("switch", { name: /parent-child chunking/i });
      expect(sw).not.toBeChecked();
    });

    it("shows user default true when user has parent_child_chunking=true and project has none", async () => {
      setup({
        project: userProject,
        userDefaults: { user_id: "user-1", parent_child_chunking: true },
      });
      await openSection(/knowledge indexing/i);
      const sw = await screen.findByRole("switch", { name: /parent-child chunking/i });
      expect(sw).toBeChecked();
    });

    it("shows user default false when user has parent_child_chunking=false and project has none", async () => {
      setup({
        project: userProject,
        userDefaults: { user_id: "user-1", parent_child_chunking: false },
      });
      await openSection(/knowledge indexing/i);
      const sw = await screen.findByRole("switch", { name: /parent-child chunking/i });
      expect(sw).not.toBeChecked();
    });

    it("shows org default true in org project when project has none", async () => {
      setup({
        project: orgProject,
        orgDefaults: { organization_id: ORG_ID, parent_child_chunking: true },
      });
      await openSection(/knowledge indexing/i);
      const sw = await screen.findByRole("switch", { name: /parent-child chunking/i });
      expect(sw).toBeChecked();
    });

    it("shows project value true even if user has false", async () => {
      setup({
        project: userProject,
        projectConfig: { ...emptyConfig, parent_child_chunking: true },
        userDefaults: { user_id: "user-1", parent_child_chunking: false },
      });
      await openSection(/knowledge indexing/i);
      const sw = await screen.findByRole("switch", { name: /parent-child chunking/i });
      expect(sw).toBeChecked();
    });

    it("shows project value false even if org has true", async () => {
      setup({
        project: orgProject,
        projectConfig: { ...emptyConfig, parent_child_chunking: false },
        orgDefaults: { organization_id: ORG_ID, parent_child_chunking: true },
      });
      await openSection(/knowledge indexing/i);
      const sw = await screen.findByRole("switch", { name: /parent-child chunking/i });
      expect(sw).not.toBeChecked();
    });
  });

  describe("Answer generation — Chat history inputs", () => {
    it("shows system default window size when no parent defaults", async () => {
      setup({ project: userProject });
      await openSection(/answer generation/i);
      expect(await screen.findByLabelText(/window size/i)).toHaveValue(8);
    });

    it("shows user default window size when user has it and project has none", async () => {
      setup({
        project: userProject,
        userDefaults: { user_id: "user-1", chat_history_window_size: 16 },
      });
      await openSection(/answer generation/i);
      expect(await screen.findByLabelText(/window size/i)).toHaveValue(16);
    });

    it("shows org default window size in org project when project has none", async () => {
      setup({
        project: orgProject,
        orgDefaults: { organization_id: ORG_ID, chat_history_window_size: 20 },
      });
      await openSection(/answer generation/i);
      expect(await screen.findByLabelText(/window size/i)).toHaveValue(20);
    });

    it("shows project window size and ignores user default", async () => {
      setup({
        project: userProject,
        projectConfig: { ...emptyConfig, chat_history_window_size: 4 },
        userDefaults: { user_id: "user-1", chat_history_window_size: 16 },
      });
      await openSection(/answer generation/i);
      expect(await screen.findByLabelText(/window size/i)).toHaveValue(4);
    });
  });

  describe("Models — Embedding backend inherited label", () => {
    it("shows Default (Gemini) when no inherited config and system default is gemini", async () => {
      setup({ project: userProject });
      await openSection(/models/i);
      expect((await screen.findAllByText(/Default.*Gemini/i)).length).toBeGreaterThan(0);
    });

    it("shows Set by user (OpenAI) when user has embedding_backend=openai and project has none", async () => {
      setup({
        project: userProject,
        userDefaults: { user_id: "user-1", embedding_backend: "openai" },
      });
      await openSection(/models/i);
      expect(await screen.findByText(/Set by user.*OpenAI/i)).toBeInTheDocument();
    });

    it("shows Set by organization (OpenAI) when org has embedding_backend=openai and project has none", async () => {
      setup({
        project: orgProject,
        orgDefaults: { organization_id: ORG_ID, embedding_backend: "openai" },
      });
      await openSection(/models/i);
      expect(await screen.findByText(/Set by organization.*OpenAI/i)).toBeInTheDocument();
    });

    it("shows Default (Gemini) when user has embedding_backend=null (not set)", async () => {
      setup({
        project: userProject,
        userDefaults: { user_id: "user-1", embedding_backend: null },
      });
      await openSection(/models/i);
      expect((await screen.findAllByText(/Default.*Gemini/i)).length).toBeGreaterThan(0);
    });
  });

  describe("Models — LLM backend inherited label", () => {
    it("shows Default (Gemini) when no inherited config and system default is gemini", async () => {
      setup({ project: userProject });
      await openSection(/models/i);
      expect((await screen.findAllByText(/Default.*Gemini/i)).length).toBeGreaterThan(0);
    });

    it("shows Set by user (Gemini) when user has llm_backend=gemini and project has none", async () => {
      setup({
        project: userProject,
        userDefaults: { user_id: "user-1", llm_backend: "gemini" },
      });
      await openSection(/models/i);
      expect((await screen.findAllByText(/Set by user.*Gemini/i)).length).toBeGreaterThan(0);
    });

    it("shows Set by organization (OpenAI) when org has llm_backend=openai and project has none", async () => {
      setup({
        project: orgProject,
        orgDefaults: { organization_id: ORG_ID, llm_backend: "openai" },
      });
      await openSection(/models/i);
      expect(await screen.findByText(/Set by organization.*OpenAI/i)).toBeInTheDocument();
    });
  });

  describe("Knowledge indexing — Chunking strategy inherited label", () => {
    it("shows Default (Auto) when no inherited config and system default is auto", async () => {
      setup({ project: userProject });
      await openSection(/knowledge indexing/i);
      expect((await screen.findAllByText(/Default.*Auto/i)).length).toBeGreaterThan(0);
    });

    it("shows Set by user (Paragraph) when user has chunking_strategy=paragraph and project has none", async () => {
      setup({
        project: userProject,
        userDefaults: { user_id: "user-1", chunking_strategy: "paragraph" },
      });
      await openSection(/knowledge indexing/i);
      expect((await screen.findAllByText(/Set by user.*Paragraph/i)).length).toBeGreaterThan(0);
    });

    it("shows Set by organization (Fixed window) when org has chunking_strategy=fixed_window and project has none", async () => {
      setup({
        project: orgProject,
        orgDefaults: { organization_id: ORG_ID, chunking_strategy: "fixed_window" },
      });
      await openSection(/knowledge indexing/i);
      expect((await screen.findAllByText(/Set by organization.*Fixed window/i)).length).toBeGreaterThan(0);
    });
  });

  describe("Retrieval — Strategy inherited label", () => {
    it("shows Default (Hybrid) when no inherited config and system default is hybrid", async () => {
      setup({ project: userProject });
      await openSection(/context retrieval/i);
      expect((await screen.findAllByText(/Default.*Hybrid/i)).length).toBeGreaterThan(0);
    });

    it("shows Set by user (Vector) when user has retrieval_strategy=vector and project has none", async () => {
      setup({
        project: userProject,
        userDefaults: { user_id: "user-1", retrieval_strategy: "vector" },
      });
      await openSection(/context retrieval/i);
      expect((await screen.findAllByText(/Set by user.*Vector/i)).length).toBeGreaterThan(0);
    });

    it("shows Set by organization (Fulltext) when org has retrieval_strategy=fulltext and project has none", async () => {
      setup({
        project: orgProject,
        orgDefaults: { organization_id: ORG_ID, retrieval_strategy: "fulltext" },
      });
      await openSection(/context retrieval/i);
      expect((await screen.findAllByText(/Set by organization.*Fulltext/i)).length).toBeGreaterThan(0);
    });
  });

  describe("Answer generation — Chat history max chars", () => {
    it("shows system default max chars when no parent defaults", async () => {
      setup({ project: userProject });
      await openSection(/answer generation/i);
      expect(await screen.findByLabelText(/max chars/i)).toHaveValue(4000);
    });

    it("shows user default max chars when user has it and project has none", async () => {
      setup({
        project: userProject,
        userDefaults: { user_id: "user-1", chat_history_max_chars: 8000 },
      });
      await openSection(/answer generation/i);
      expect(await screen.findByLabelText(/max chars/i)).toHaveValue(8000);
    });

    it("shows org default max chars in org project when project has none", async () => {
      setup({
        project: orgProject,
        orgDefaults: { organization_id: ORG_ID, chat_history_max_chars: 6000 },
      });
      await openSection(/answer generation/i);
      expect(await screen.findByLabelText(/max chars/i)).toHaveValue(6000);
    });

    it("shows project max chars and ignores user default", async () => {
      setup({
        project: userProject,
        projectConfig: { ...emptyConfig, chat_history_max_chars: 2000 },
        userDefaults: { user_id: "user-1", chat_history_max_chars: 8000 },
      });
      await openSection(/answer generation/i);
      expect(await screen.findByLabelText(/max chars/i)).toHaveValue(2000);
    });
  });
});

// ---------------------------------------------------------------------------
// Smoke tests (existing behaviour)
// ---------------------------------------------------------------------------

describe("ProjectAdvancedPanel – smoke", () => {
  it("renders section triggers", async () => {
    setup();
    expect(await screen.findByRole("button", { name: /models/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /context retrieval/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /delete/i })).toBeInTheDocument();
  });
});

// ---------------------------------------------------------------------------
// FieldHint per-field inheritance indicators — user project
// ---------------------------------------------------------------------------

describe("ProjectAdvancedPanel – FieldHint (user project)", () => {
  describe("Models section", () => {
    it("shows no field hint for embedding_backend when user has no defaults", async () => {
      setup({ project: userProject });
      await openSection(/models/i);
      await screen.findByLabelText(/embedding backend/i);
      expect(screen.queryByText("Inherited from user")).not.toBeInTheDocument();
    });

    it("shows 'Inherited from user' for embedding_backend when user has it but project has none", async () => {
      setup({
        project: userProject,
        userDefaults: { user_id: "user-1", embedding_backend: "gemini" },
      });
      await openSection(/models/i);
      expect(await screen.findByText("Inherited from user")).toBeInTheDocument();
    });

    it("shows 'Inherited from user' when project has same embedding_backend as user (not customized)", async () => {
      setup({
        project: userProject,
        projectConfig: { ...emptyConfig, embedding_backend: "openai" },
        userDefaults: { user_id: "user-1", embedding_backend: "openai" },
      });
      await openSection(/models/i);
      expect(await screen.findByText("Inherited from user")).toBeInTheDocument();
      expect(screen.queryByText(/Customized/)).not.toBeInTheDocument();
    });

    it("shows 'Customized · user default: Gemini' when project overrides embedding_backend", async () => {
      setup({
        project: userProject,
        projectConfig: { ...emptyConfig, embedding_backend: "openai" },
        userDefaults: { user_id: "user-1", embedding_backend: "gemini" },
      });
      await openSection(/models/i);
      expect(await screen.findByText(/Customized · user default:/)).toBeInTheDocument();
      expect(await screen.findByText("Gemini")).toBeInTheDocument();
    });

    it("shows 'Customized · user default: Gemini' for llm_backend when project differs from user", async () => {
      setup({
        project: userProject,
        projectConfig: { ...emptyConfig, llm_backend: "openai" },
        userDefaults: { user_id: "user-1", llm_backend: "gemini" },
      });
      await openSection(/models/i);
      expect(await screen.findByText(/Customized · user default:/)).toBeInTheDocument();
      expect(await screen.findByText("Gemini")).toBeInTheDocument();
    });
  });

  describe("Retrieval section", () => {
    it("shows no field hint for retrieval fields when user has no defaults", async () => {
      setup({ project: userProject });
      await openSection(/context retrieval/i);
      await screen.findByLabelText(/top-k/i);
      expect(screen.queryByText("Inherited from user")).not.toBeInTheDocument();
    });

    it("shows 'Inherited from user' for retrieval_strategy when user has it and project has none", async () => {
      setup({
        project: userProject,
        userDefaults: { user_id: "user-1", retrieval_strategy: "hybrid" },
      });
      await openSection(/context retrieval/i);
      expect(await screen.findByText("Inherited from user")).toBeInTheDocument();
    });

    it("shows 'Customized · user default: 10' when project overrides retrieval_top_k", async () => {
      setup({
        project: userProject,
        projectConfig: { ...emptyConfig, retrieval_top_k: 20 },
        userDefaults: { user_id: "user-1", retrieval_top_k: 10 },
      });
      await openSection(/context retrieval/i);
      expect(await screen.findByText(/Customized · user default:/)).toBeInTheDocument();
      expect(await screen.findByText("10")).toBeInTheDocument();
    });

    it("shows 'Customized · user default: Hybrid' when project overrides retrieval_strategy", async () => {
      setup({
        project: userProject,
        projectConfig: { ...emptyConfig, retrieval_strategy: "vector" },
        userDefaults: { user_id: "user-1", retrieval_strategy: "hybrid" },
      });
      await openSection(/context retrieval/i);
      expect(await screen.findByText(/Customized · user default:/)).toBeInTheDocument();
      expect(await screen.findByText("Hybrid")).toBeInTheDocument();
    });
  });

  describe("Knowledge indexing section", () => {
    it("shows 'Inherited from user' for chunking_strategy when user has it and project has none", async () => {
      setup({
        project: userProject,
        userDefaults: { user_id: "user-1", chunking_strategy: "paragraph" },
      });
      await openSection(/knowledge indexing/i);
      expect(await screen.findByText("Inherited from user")).toBeInTheDocument();
    });

    it("shows 'Customized · user default: Paragraph' when project overrides chunking_strategy", async () => {
      setup({
        project: userProject,
        projectConfig: { ...emptyConfig, chunking_strategy: "fixed_window" },
        userDefaults: { user_id: "user-1", chunking_strategy: "paragraph" },
      });
      await openSection(/knowledge indexing/i);
      expect(await screen.findByText(/Customized · user default:/)).toBeInTheDocument();
      expect(await screen.findByText("Paragraph")).toBeInTheDocument();
    });
  });

  describe("Context augmentation section", () => {
    it("shows no field hint for reranking when user has no defaults", async () => {
      setup({ project: userProject });
      await openSection(/context augmentation/i);
      await screen.findByLabelText(/reranking/i);
      expect(screen.queryByText("Inherited from user")).not.toBeInTheDocument();
    });

    it("shows 'Inherited from user' for reranking_enabled when user has it and project has none", async () => {
      setup({
        project: userProject,
        userDefaults: { user_id: "user-1", reranking_enabled: true },
      });
      await openSection(/context augmentation/i);
      expect(await screen.findByText("Inherited from user")).toBeInTheDocument();
    });

    it("shows 'Customized · user default: false' when project overrides reranking_enabled", async () => {
      setup({
        project: userProject,
        projectConfig: { ...emptyConfig, reranking_enabled: true },
        userDefaults: { user_id: "user-1", reranking_enabled: false },
      });
      await openSection(/context augmentation/i);
      expect(await screen.findByText(/Customized · user default:/)).toBeInTheDocument();
    });
  });

  describe("Answer generation section", () => {
    it("shows no field hint for history fields when user has no defaults", async () => {
      setup({ project: userProject });
      await openSection(/answer generation/i);
      await screen.findByLabelText(/max chars/i);
      expect(screen.queryByText("Inherited from user")).not.toBeInTheDocument();
    });

    it("shows 'Inherited from user' for chat_history_max_chars when user has it and project has none", async () => {
      setup({
        project: userProject,
        userDefaults: { user_id: "user-1", chat_history_max_chars: 8000 },
      });
      await openSection(/answer generation/i);
      expect(await screen.findByText("Inherited from user")).toBeInTheDocument();
    });

    it("shows 'Customized · user default: 8000' when project overrides chat_history_max_chars", async () => {
      setup({
        project: userProject,
        projectConfig: { ...emptyConfig, chat_history_max_chars: 2000 },
        userDefaults: { user_id: "user-1", chat_history_max_chars: 8000 },
      });
      await openSection(/answer generation/i);
      expect(await screen.findByText(/Customized · user default:/)).toBeInTheDocument();
      expect(await screen.findByText("8000")).toBeInTheDocument();
    });
  });
});

// ---------------------------------------------------------------------------
// FieldHint per-field inheritance indicators — org project
// ---------------------------------------------------------------------------

describe("ProjectAdvancedPanel – FieldHint (org project)", () => {
  describe("Models section", () => {
    it("shows 'Inherited from organization' for embedding_backend when org has it and project has none", async () => {
      setup({
        project: orgProject,
        orgDefaults: { organization_id: ORG_ID, embedding_backend: "openai" },
      });
      await openSection(/models/i);
      expect(await screen.findByText("Inherited from organization")).toBeInTheDocument();
    });

    it("shows 'Inherited from organization' when project has same embedding_backend as org", async () => {
      setup({
        project: orgProject,
        projectConfig: { ...emptyConfig, embedding_backend: "openai" },
        orgDefaults: { organization_id: ORG_ID, embedding_backend: "openai" },
      });
      await openSection(/models/i);
      expect(await screen.findByText("Inherited from organization")).toBeInTheDocument();
      expect(screen.queryByText(/Customized/)).not.toBeInTheDocument();
    });

    it("shows 'Customized · org default: Gemini' when project overrides embedding_backend", async () => {
      setup({
        project: orgProject,
        projectConfig: { ...emptyConfig, embedding_backend: "openai" },
        orgDefaults: { organization_id: ORG_ID, embedding_backend: "gemini" },
      });
      await openSection(/models/i);
      expect(await screen.findByText(/Customized · org default:/)).toBeInTheDocument();
      expect(await screen.findByText("Gemini")).toBeInTheDocument();
    });

    it("shows 'Customized · org default: Gemini' for llm_backend when project differs from org", async () => {
      setup({
        project: orgProject,
        projectConfig: { ...emptyConfig, llm_backend: "anthropic" },
        orgDefaults: { organization_id: ORG_ID, llm_backend: "gemini" },
      });
      await openSection(/models/i);
      expect(await screen.findByText(/Customized · org default:/)).toBeInTheDocument();
      expect(await screen.findByText("Gemini")).toBeInTheDocument();
    });
  });

  describe("Retrieval section", () => {
    it("shows 'Inherited from organization' for retrieval_strategy when org has it and project has none", async () => {
      setup({
        project: orgProject,
        orgDefaults: { organization_id: ORG_ID, retrieval_strategy: "hybrid" },
      });
      await openSection(/context retrieval/i);
      expect(await screen.findByText("Inherited from organization")).toBeInTheDocument();
    });

    it("shows 'Customized · org default: Hybrid' when project overrides retrieval_strategy", async () => {
      setup({
        project: orgProject,
        projectConfig: { ...emptyConfig, retrieval_strategy: "vector" },
        orgDefaults: { organization_id: ORG_ID, retrieval_strategy: "hybrid" },
      });
      await openSection(/context retrieval/i);
      expect(await screen.findByText(/Customized · org default:/)).toBeInTheDocument();
      expect(await screen.findByText("Hybrid")).toBeInTheDocument();
    });

    it("shows 'Customized · org default: 15' when project overrides retrieval_top_k", async () => {
      setup({
        project: orgProject,
        projectConfig: { ...emptyConfig, retrieval_top_k: 5 },
        orgDefaults: { organization_id: ORG_ID, retrieval_top_k: 15 },
      });
      await openSection(/context retrieval/i);
      expect(await screen.findByText(/Customized · org default:/)).toBeInTheDocument();
      expect(await screen.findByText("15")).toBeInTheDocument();
    });
  });

  describe("Knowledge indexing section", () => {
    it("shows 'Inherited from organization' for chunking_strategy when org has it and project has none", async () => {
      setup({
        project: orgProject,
        orgDefaults: { organization_id: ORG_ID, chunking_strategy: "paragraph" },
      });
      await openSection(/knowledge indexing/i);
      expect(await screen.findByText("Inherited from organization")).toBeInTheDocument();
    });

    it("shows 'Customized · org default: Paragraph' when project overrides chunking_strategy", async () => {
      setup({
        project: orgProject,
        projectConfig: { ...emptyConfig, chunking_strategy: "fixed_window" },
        orgDefaults: { organization_id: ORG_ID, chunking_strategy: "paragraph" },
      });
      await openSection(/knowledge indexing/i);
      expect(await screen.findByText(/Customized · org default:/)).toBeInTheDocument();
      expect(await screen.findByText("Paragraph")).toBeInTheDocument();
    });
  });

  describe("Context augmentation section", () => {
    it("shows 'Inherited from organization' for reranking_enabled when org has it and project has none", async () => {
      setup({
        project: orgProject,
        orgDefaults: { organization_id: ORG_ID, reranking_enabled: false },
      });
      await openSection(/context augmentation/i);
      expect(await screen.findByText("Inherited from organization")).toBeInTheDocument();
    });

    it("shows 'Customized · org default: false' when project overrides reranking_enabled", async () => {
      setup({
        project: orgProject,
        projectConfig: { ...emptyConfig, reranking_enabled: true },
        orgDefaults: { organization_id: ORG_ID, reranking_enabled: false },
      });
      await openSection(/context augmentation/i);
      expect(await screen.findByText(/Customized · org default:/)).toBeInTheDocument();
    });
  });

  describe("Answer generation section", () => {
    it("shows 'Inherited from organization' for chat_history_window_size when org has it and project has none", async () => {
      setup({
        project: orgProject,
        orgDefaults: { organization_id: ORG_ID, chat_history_window_size: 20 },
      });
      await openSection(/answer generation/i);
      expect(await screen.findByText("Inherited from organization")).toBeInTheDocument();
    });

    it("shows 'Customized · org default: 20' when project overrides chat_history_window_size", async () => {
      setup({
        project: orgProject,
        projectConfig: { ...emptyConfig, chat_history_window_size: 4 },
        orgDefaults: { organization_id: ORG_ID, chat_history_window_size: 20 },
      });
      await openSection(/answer generation/i);
      expect(await screen.findByText(/Customized · org default:/)).toBeInTheDocument();
      expect(await screen.findByText("20")).toBeInTheDocument();
    });

    it("shows 'Customized · org default: 6000' when project overrides chat_history_max_chars", async () => {
      setup({
        project: orgProject,
        projectConfig: { ...emptyConfig, chat_history_max_chars: 2000 },
        orgDefaults: { organization_id: ORG_ID, chat_history_max_chars: 6000 },
      });
      await openSection(/answer generation/i);
      expect(await screen.findByText(/Customized · org default:/)).toBeInTheDocument();
      expect(await screen.findByText("6000")).toBeInTheDocument();
    });
  });
});
