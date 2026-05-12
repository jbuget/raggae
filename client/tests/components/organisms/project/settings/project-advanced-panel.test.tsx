import { http, HttpResponse } from "msw";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { ProjectAdvancedPanel } from "@/components/organisms/project/settings/project-advanced-panel";
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

const emptyConfig = {
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
  projectConfig?: typeof emptyConfig;
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
// Inheritance messages — user project
// ---------------------------------------------------------------------------

describe("ProjectAdvancedPanel – inheritance messages (user project)", () => {
  describe("Models section", () => {
    it("shows system defaults message when no user defaults and no project config", async () => {
      setup({ project: userProject });
      await openSection(/models/i);
      expect(
        await screen.findByText("No settings configured — system defaults are used."),
      ).toBeInTheDocument();
    });

    it("shows userDefaultsActive when user has models but project has none", async () => {
      setup({
        project: userProject,
        userDefaults: { user_id: "user-1", embedding_backend: "openai", llm_backend: null },
      });
      await openSection(/models/i);
      expect(
        await screen.findByText("No parameters modified, user settings apply."),
      ).toBeInTheDocument();
    });

    it("does NOT show override message when project has the same value as user (same value ≠ override)", async () => {
      setup({
        project: userProject,
        projectConfig: { ...emptyConfig, embedding_backend: "openai" },
        userDefaults: { user_id: "user-1", embedding_backend: "openai", llm_backend: null },
      });
      await openSection(/models/i);
      expect(
        await screen.findByText("No parameters modified, user settings apply."),
      ).toBeInTheDocument();
      expect(
        screen.queryByText(/user settings are/i),
      ).not.toBeInTheDocument();
    });

    it("shows userOverrideSome when project overrides only one model field", async () => {
      setup({
        project: userProject,
        projectConfig: { ...emptyConfig, embedding_backend: "openai" },
        userDefaults: { user_id: "user-1", embedding_backend: "gemini", llm_backend: "gemini" },
      });
      await openSection(/models/i);
      expect(
        await screen.findByText("Some user settings are modified."),
      ).toBeInTheDocument();
    });

    it("shows userOverrideAll when project overrides all model fields", async () => {
      setup({
        project: userProject,
        projectConfig: { ...emptyConfig, embedding_backend: "openai", llm_backend: "openai" },
        userDefaults: { user_id: "user-1", embedding_backend: "gemini", llm_backend: "gemini" },
      });
      await openSection(/models/i);
      expect(
        await screen.findByText("All user settings are overridden."),
      ).toBeInTheDocument();
    });
  });

  describe("Retrieval section", () => {
    it("shows system defaults message when no user defaults and no project config", async () => {
      setup({ project: userProject });
      await openSection(/context retrieval/i);
      expect(
        await screen.findByText("No settings configured — system defaults are used."),
      ).toBeInTheDocument();
    });

    it("shows userDefaultsActive when user has retrieval params but project has none", async () => {
      setup({
        project: userProject,
        userDefaults: { user_id: "user-1", retrieval_top_k: 10, retrieval_min_score: 0.5 },
      });
      await openSection(/context retrieval/i);
      expect(
        await screen.findByText("No parameters modified, user settings apply."),
      ).toBeInTheDocument();
    });

    it("does NOT show override message when project has the same retrieval values as user", async () => {
      setup({
        project: userProject,
        projectConfig: { ...emptyConfig, retrieval_top_k: 10, retrieval_min_score: 0.5 },
        userDefaults: { user_id: "user-1", retrieval_top_k: 10, retrieval_min_score: 0.5 },
      });
      await openSection(/context retrieval/i);
      expect(
        await screen.findByText("No parameters modified, user settings apply."),
      ).toBeInTheDocument();
    });

    it("shows userOverrideSome when project overrides only retrieval_top_k", async () => {
      setup({
        project: userProject,
        projectConfig: { ...emptyConfig, retrieval_top_k: 20 },
        userDefaults: {
          user_id: "user-1",
          retrieval_strategy: "hybrid",
          retrieval_top_k: 10,
          retrieval_min_score: 0.5,
        },
      });
      await openSection(/context retrieval/i);
      expect(
        await screen.findByText("Some user settings are modified."),
      ).toBeInTheDocument();
    });

    it("shows userOverrideAll when project overrides all retrieval params", async () => {
      setup({
        project: userProject,
        projectConfig: {
          ...emptyConfig,
          retrieval_strategy: "vector",
          retrieval_top_k: 20,
          retrieval_min_score: 0.8,
        },
        userDefaults: {
          user_id: "user-1",
          retrieval_strategy: "hybrid",
          retrieval_top_k: 10,
          retrieval_min_score: 0.5,
        },
      });
      await openSection(/context retrieval/i);
      expect(
        await screen.findByText("All user settings are overridden."),
      ).toBeInTheDocument();
    });
  });

  describe("Knowledge indexing section", () => {
    it("shows userDefaultsActive when user has chunking strategy but project has none", async () => {
      setup({
        project: userProject,
        userDefaults: { user_id: "user-1", chunking_strategy: "paragraph", parent_child_chunking: true },
      });
      await openSection(/knowledge indexing/i);
      expect(
        await screen.findByText("No parameters modified, user settings apply."),
      ).toBeInTheDocument();
    });

    it("shows userOverrideSome when project overrides only chunking_strategy", async () => {
      setup({
        project: userProject,
        projectConfig: { ...emptyConfig, chunking_strategy: "fixed_window" },
        userDefaults: {
          user_id: "user-1",
          chunking_strategy: "paragraph",
          parent_child_chunking: true,
        },
      });
      await openSection(/knowledge indexing/i);
      expect(
        await screen.findByText("Some user settings are modified."),
      ).toBeInTheDocument();
    });

    it("shows userOverrideAll when project overrides all indexing params", async () => {
      setup({
        project: userProject,
        projectConfig: { ...emptyConfig, chunking_strategy: "fixed_window", parent_child_chunking: false },
        userDefaults: {
          user_id: "user-1",
          chunking_strategy: "paragraph",
          parent_child_chunking: true,
        },
      });
      await openSection(/knowledge indexing/i);
      expect(
        await screen.findByText("All user settings are overridden."),
      ).toBeInTheDocument();
    });
  });

  describe("Context augmentation section", () => {
    it("shows system defaults message when no user defaults and no project config", async () => {
      setup({ project: userProject });
      await openSection(/context augmentation/i);
      expect(
        await screen.findByText("No settings configured — system defaults are used."),
      ).toBeInTheDocument();
    });

    it("shows userDefaultsActive when user has reranking params but project has none", async () => {
      setup({
        project: userProject,
        userDefaults: { user_id: "user-1", reranking_enabled: true, reranker_backend: "cross_encoder" },
      });
      await openSection(/context augmentation/i);
      expect(
        await screen.findByText("No parameters modified, user settings apply."),
      ).toBeInTheDocument();
    });

    it("shows userOverrideSome when project overrides only reranking_enabled", async () => {
      setup({
        project: userProject,
        projectConfig: { ...emptyConfig, reranking_enabled: false },
        userDefaults: { user_id: "user-1", reranking_enabled: true, reranker_backend: "cross_encoder" },
      });
      await openSection(/context augmentation/i);
      expect(
        await screen.findByText("Some user settings are modified."),
      ).toBeInTheDocument();
    });

    it("shows userOverrideAll when project overrides all reranking params", async () => {
      setup({
        project: userProject,
        projectConfig: { ...emptyConfig, reranking_enabled: false, reranker_backend: "inmemory" },
        userDefaults: { user_id: "user-1", reranking_enabled: true, reranker_backend: "cross_encoder" },
      });
      await openSection(/context augmentation/i);
      expect(
        await screen.findByText("All user settings are overridden."),
      ).toBeInTheDocument();
    });
  });

  describe("Answer generation section", () => {
    it("shows system defaults message when no user defaults and no project config", async () => {
      setup({ project: userProject });
      await openSection(/answer generation/i);
      expect(
        await screen.findByText("No settings configured — system defaults are used."),
      ).toBeInTheDocument();
    });

    it("shows userDefaultsActive when user has history params but project has none", async () => {
      setup({
        project: userProject,
        userDefaults: { user_id: "user-1", chat_history_window_size: 16, chat_history_max_chars: 8000 },
      });
      await openSection(/answer generation/i);
      expect(
        await screen.findByText("No parameters modified, user settings apply."),
      ).toBeInTheDocument();
    });

    it("shows userOverrideSome when project overrides only window size", async () => {
      setup({
        project: userProject,
        projectConfig: { ...emptyConfig, chat_history_window_size: 4 },
        userDefaults: { user_id: "user-1", chat_history_window_size: 16, chat_history_max_chars: 8000 },
      });
      await openSection(/answer generation/i);
      expect(
        await screen.findByText("Some user settings are modified."),
      ).toBeInTheDocument();
    });

    it("shows userOverrideAll when project overrides all history params", async () => {
      setup({
        project: userProject,
        projectConfig: { ...emptyConfig, chat_history_window_size: 4, chat_history_max_chars: 2000 },
        userDefaults: { user_id: "user-1", chat_history_window_size: 16, chat_history_max_chars: 8000 },
      });
      await openSection(/answer generation/i);
      expect(
        await screen.findByText("All user settings are overridden."),
      ).toBeInTheDocument();
    });
  });
});

// ---------------------------------------------------------------------------
// Inheritance messages — org project
// ---------------------------------------------------------------------------

describe("ProjectAdvancedPanel – inheritance messages (org project)", () => {
  describe("Models section", () => {
    it("does NOT show system defaults message for org projects even with no org config", async () => {
      setup({ project: orgProject });
      await openSection(/models/i);
      await screen.findByRole("button", { name: /models/i });
      expect(
        screen.queryByText("No settings configured — system defaults are used."),
      ).not.toBeInTheDocument();
    });

    it("shows orgDefaultsActive when org has models but project has none", async () => {
      setup({
        project: orgProject,
        orgDefaults: {
          organization_id: ORG_ID,
          embedding_backend: "openai",
          llm_backend: null,
        },
      });
      await openSection(/models/i);
      expect(
        await screen.findByText("No parameters modified, organization settings apply."),
      ).toBeInTheDocument();
    });

    it("does NOT show override message when project has the same value as org", async () => {
      setup({
        project: orgProject,
        projectConfig: { ...emptyConfig, embedding_backend: "openai" },
        orgDefaults: {
          organization_id: ORG_ID,
          embedding_backend: "openai",
          llm_backend: null,
        },
      });
      await openSection(/models/i);
      expect(
        await screen.findByText("No parameters modified, organization settings apply."),
      ).toBeInTheDocument();
    });

    it("shows orgOverrideSome when project overrides only embedding_backend", async () => {
      setup({
        project: orgProject,
        projectConfig: { ...emptyConfig, embedding_backend: "openai" },
        orgDefaults: {
          organization_id: ORG_ID,
          embedding_backend: "gemini",
          llm_backend: "gemini",
        },
      });
      await openSection(/models/i);
      expect(
        await screen.findByText("Some organization settings are modified."),
      ).toBeInTheDocument();
    });

    it("shows orgOverrideAll when project overrides both model fields", async () => {
      setup({
        project: orgProject,
        projectConfig: { ...emptyConfig, embedding_backend: "openai", llm_backend: "openai" },
        orgDefaults: {
          organization_id: ORG_ID,
          embedding_backend: "gemini",
          llm_backend: "gemini",
        },
      });
      await openSection(/models/i);
      expect(
        await screen.findByText("All organization settings are overridden."),
      ).toBeInTheDocument();
    });
  });

  describe("Retrieval section", () => {
    it("shows orgDefaultsActive when org has retrieval params but project has none", async () => {
      setup({
        project: orgProject,
        orgDefaults: {
          organization_id: ORG_ID,
          retrieval_top_k: 15,
          retrieval_min_score: 0.4,
        },
      });
      await openSection(/context retrieval/i);
      expect(
        await screen.findByText("No parameters modified, organization settings apply."),
      ).toBeInTheDocument();
    });

    it("does NOT show override message when project has the same retrieval values as org", async () => {
      setup({
        project: orgProject,
        projectConfig: { ...emptyConfig, retrieval_top_k: 15 },
        orgDefaults: { organization_id: ORG_ID, retrieval_top_k: 15 },
      });
      await openSection(/context retrieval/i);
      expect(
        await screen.findByText("No parameters modified, organization settings apply."),
      ).toBeInTheDocument();
    });

    it("shows orgOverrideSome when project overrides only retrieval_top_k", async () => {
      setup({
        project: orgProject,
        projectConfig: { ...emptyConfig, retrieval_top_k: 20 },
        orgDefaults: {
          organization_id: ORG_ID,
          retrieval_strategy: "hybrid",
          retrieval_top_k: 10,
          retrieval_min_score: 0.5,
        },
      });
      await openSection(/context retrieval/i);
      expect(
        await screen.findByText("Some organization settings are modified."),
      ).toBeInTheDocument();
    });

    it("shows orgOverrideAll when project overrides all retrieval params", async () => {
      setup({
        project: orgProject,
        projectConfig: {
          ...emptyConfig,
          retrieval_strategy: "fulltext",
          retrieval_top_k: 20,
          retrieval_min_score: 0.9,
        },
        orgDefaults: {
          organization_id: ORG_ID,
          retrieval_strategy: "hybrid",
          retrieval_top_k: 10,
          retrieval_min_score: 0.5,
        },
      });
      await openSection(/context retrieval/i);
      expect(
        await screen.findByText("All organization settings are overridden."),
      ).toBeInTheDocument();
    });
  });

  describe("Knowledge indexing section", () => {
    it("shows orgDefaultsActive when org has chunking params but project has none", async () => {
      setup({
        project: orgProject,
        orgDefaults: { organization_id: ORG_ID, chunking_strategy: "paragraph", parent_child_chunking: true },
      });
      await openSection(/knowledge indexing/i);
      expect(
        await screen.findByText("No parameters modified, organization settings apply."),
      ).toBeInTheDocument();
    });

    it("shows orgOverrideSome when project overrides only chunking_strategy", async () => {
      setup({
        project: orgProject,
        projectConfig: { ...emptyConfig, chunking_strategy: "fixed_window" },
        orgDefaults: { organization_id: ORG_ID, chunking_strategy: "paragraph", parent_child_chunking: true },
      });
      await openSection(/knowledge indexing/i);
      expect(
        await screen.findByText("Some organization settings are modified."),
      ).toBeInTheDocument();
    });

    it("shows orgOverrideAll when project overrides all indexing params", async () => {
      setup({
        project: orgProject,
        projectConfig: { ...emptyConfig, chunking_strategy: "fixed_window", parent_child_chunking: false },
        orgDefaults: { organization_id: ORG_ID, chunking_strategy: "paragraph", parent_child_chunking: true },
      });
      await openSection(/knowledge indexing/i);
      expect(
        await screen.findByText("All organization settings are overridden."),
      ).toBeInTheDocument();
    });
  });

  describe("Context augmentation section", () => {
    it("shows orgDefaultsActive when org has reranking params but project has none", async () => {
      setup({
        project: orgProject,
        orgDefaults: { organization_id: ORG_ID, reranking_enabled: true, reranker_backend: "cross_encoder" },
      });
      await openSection(/context augmentation/i);
      expect(
        await screen.findByText("No parameters modified, organization settings apply."),
      ).toBeInTheDocument();
    });

    it("shows orgOverrideSome when project overrides only reranking_enabled", async () => {
      setup({
        project: orgProject,
        projectConfig: { ...emptyConfig, reranking_enabled: false },
        orgDefaults: { organization_id: ORG_ID, reranking_enabled: true, reranker_backend: "cross_encoder" },
      });
      await openSection(/context augmentation/i);
      expect(
        await screen.findByText("Some organization settings are modified."),
      ).toBeInTheDocument();
    });

    it("shows orgOverrideAll when project overrides all reranking params", async () => {
      setup({
        project: orgProject,
        projectConfig: { ...emptyConfig, reranking_enabled: false, reranker_backend: "inmemory" },
        orgDefaults: { organization_id: ORG_ID, reranking_enabled: true, reranker_backend: "cross_encoder" },
      });
      await openSection(/context augmentation/i);
      expect(
        await screen.findByText("All organization settings are overridden."),
      ).toBeInTheDocument();
    });
  });

  describe("Answer generation section", () => {
    it("shows orgDefaultsActive when org has history params but project has none", async () => {
      setup({
        project: orgProject,
        orgDefaults: { organization_id: ORG_ID, chat_history_window_size: 20, chat_history_max_chars: 6000 },
      });
      await openSection(/answer generation/i);
      expect(
        await screen.findByText("No parameters modified, organization settings apply."),
      ).toBeInTheDocument();
    });

    it("shows orgOverrideSome when project overrides only window size", async () => {
      setup({
        project: orgProject,
        projectConfig: { ...emptyConfig, chat_history_window_size: 4 },
        orgDefaults: { organization_id: ORG_ID, chat_history_window_size: 20, chat_history_max_chars: 6000 },
      });
      await openSection(/answer generation/i);
      expect(
        await screen.findByText("Some organization settings are modified."),
      ).toBeInTheDocument();
    });

    it("shows orgOverrideAll when project overrides all history params", async () => {
      setup({
        project: orgProject,
        projectConfig: { ...emptyConfig, chat_history_window_size: 4, chat_history_max_chars: 2000 },
        orgDefaults: { organization_id: ORG_ID, chat_history_window_size: 20, chat_history_max_chars: 6000 },
      });
      await openSection(/answer generation/i);
      expect(
        await screen.findByText("All organization settings are overridden."),
      ).toBeInTheDocument();
    });
  });
});
