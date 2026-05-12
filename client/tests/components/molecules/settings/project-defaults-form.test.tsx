import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { ProjectDefaultsForm } from "@/components/molecules/settings/project-defaults-form";
import type { ProjectDefaultsConfig } from "@/lib/types/api";
import { renderWithProviders } from "../../../helpers/render";

const systemDefaults = {
  llm_backend: "gemini",
  llm_model: "gemini-1.5-flash",
  embedding_backend: "gemini",
  embedding_model: "text-embedding-004",
  chunking_strategy: "auto",
  parent_child_chunking: true,
  retrieval_strategy: "hybrid",
  retrieval_top_k: 8,
  retrieval_min_score: 0.3,
  reranker_backend: "none",
  reranker_model: "",
  reranker_candidate_multiplier: 3,
  chat_history_window_size: 8,
  chat_history_max_chars: 4000,
};

const modelCatalog = {
  embedding: {
    gemini: [{ id: "text-embedding-004", label: "text-embedding-004" }],
    openai: [], ollama: [], inmemory: [],
  },
  llm: {
    gemini: [{ id: "gemini-1.5-flash", label: "gemini-1.5-flash" }],
    openai: [], anthropic: [], ollama: [], inmemory: [],
  },
  reranker: { none: [], cross_encoder: [], inmemory: [], mmr: [] },
};

const baseProps = {
  defaults: null,
  systemDefaults,
  credentials: [],
  modelCatalog,
  onSave: vi.fn(),
  isPending: false,
  idPrefix: "test",
};

describe("ProjectDefaultsForm", () => {
  it("should render accordion sections", async () => {
    renderWithProviders(<ProjectDefaultsForm {...baseProps} />);
    expect(await screen.findByRole("button", { name: /models/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /indexing/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /retrieval/i })).toBeInTheDocument();
  });

  it("should not show model/credential selects when no backend configured at this level", async () => {
    // When embedding_backend is null in defaults (not explicitly set), backend select is "none"
    // → model and credential selects should be hidden
    renderWithProviders(<ProjectDefaultsForm {...baseProps} defaults={null} />);
    const modelsBtn = await screen.findByRole("button", { name: /models/i });
    await userEvent.click(modelsBtn);
    // Embedding model label should not appear when backend is none
    expect(screen.queryByLabelText(/embedding model/i)).not.toBeInTheDocument();
  });

  it("should show model select when embedding backend is explicitly set in defaults", async () => {
    const defaults: ProjectDefaultsConfig = {
      embedding_backend: "gemini", embedding_model: null, embedding_api_key_credential_id: null,
      llm_backend: null, llm_model: null, llm_api_key_credential_id: null,
      chunking_strategy: null, parent_child_chunking: null,
      retrieval_strategy: null, retrieval_top_k: null, retrieval_min_score: null,
      reranking_enabled: null, reranker_backend: null, reranker_model: null,
      reranker_candidate_multiplier: null, chat_history_window_size: null, chat_history_max_chars: null,
    };
    renderWithProviders(<ProjectDefaultsForm {...baseProps} defaults={defaults} />);
    const modelsBtn = await screen.findByRole("button", { name: /models/i });
    await userEvent.click(modelsBtn);
    // Embedding model label should appear once a backend is set
    expect(await screen.findByLabelText(/embedding model/i)).toBeInTheDocument();
  });

  it("should not show llm model select when no llm backend configured at this level", async () => {
    renderWithProviders(<ProjectDefaultsForm {...baseProps} defaults={null} />);
    const modelsBtn = await screen.findByRole("button", { name: /models/i });
    await userEvent.click(modelsBtn);
    expect(screen.queryByLabelText(/llm model/i)).not.toBeInTheDocument();
  });

  it("should show save button disabled when no changes", async () => {
    renderWithProviders(<ProjectDefaultsForm {...baseProps} />);
    const saveBtn = await screen.findByRole("button", { name: /save/i });
    expect(saveBtn).toBeDisabled();
  });

  it("should not show reset button when showReset is false", async () => {
    renderWithProviders(<ProjectDefaultsForm {...baseProps} showReset={false} />);
    await screen.findByRole("button", { name: /save/i });
    expect(screen.queryByRole("button", { name: /reset/i })).not.toBeInTheDocument();
  });

  it("should show reset button when showReset is true and defaults have a value configured", async () => {
    const defaults: ProjectDefaultsConfig = {
      embedding_backend: "gemini", embedding_model: null, embedding_api_key_credential_id: null,
      llm_backend: null, llm_model: null, llm_api_key_credential_id: null,
      chunking_strategy: null, parent_child_chunking: null,
      retrieval_strategy: null, retrieval_top_k: null, retrieval_min_score: null,
      reranking_enabled: null, reranker_backend: null, reranker_model: null,
      reranker_candidate_multiplier: null, chat_history_window_size: null, chat_history_max_chars: null,
    };
    renderWithProviders(<ProjectDefaultsForm {...baseProps} defaults={defaults} showReset />);
    expect(await screen.findByRole("button", { name: /reset/i })).toBeInTheDocument();
  });

  it("should show title and description when provided", async () => {
    renderWithProviders(
      <ProjectDefaultsForm {...baseProps} title="Mon titre" description="Ma description" />,
    );
    expect(await screen.findByText("Mon titre")).toBeInTheDocument();
    expect(screen.getByText("Ma description")).toBeInTheDocument();
  });

  it("should call onSave with all null values when reset button is clicked", async () => {
    const onSave = vi.fn();
    const defaults: ProjectDefaultsConfig = {
      embedding_backend: "gemini", embedding_model: "text-embedding-004",
      embedding_api_key_credential_id: null,
      llm_backend: "gemini", llm_model: "gemini-1.5-flash", llm_api_key_credential_id: null,
      chunking_strategy: "auto", parent_child_chunking: false,
      retrieval_strategy: "hybrid", retrieval_top_k: 8, retrieval_min_score: 0.3,
      reranking_enabled: false, reranker_backend: "none", reranker_model: null,
      reranker_candidate_multiplier: 3, chat_history_window_size: 8, chat_history_max_chars: 4000,
    };
    renderWithProviders(<ProjectDefaultsForm {...baseProps} defaults={defaults} showReset onSave={onSave} />);
    const resetBtn = await screen.findByRole("button", { name: /reset/i });
    await userEvent.click(resetBtn);
    expect(onSave).toHaveBeenCalledWith(
      expect.objectContaining({
        embedding_backend: null,
        llm_backend: null,
        embedding_model: null,
        llm_model: null,
      }),
    );
  });
});
