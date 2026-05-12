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
});
