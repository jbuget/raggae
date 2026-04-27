import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { SnapshotCard } from "@/components/molecules/project/snapshot-card";
import { renderWithProviders } from "../../../helpers/render";
import type { ProjectSnapshotResponse } from "@/lib/types/api";

const mockSnapshot: ProjectSnapshotResponse = {
  id: "snap-1",
  project_id: "proj-1",
  version_number: 3,
  label: "After big refactor",
  created_at: "2026-01-15T10:30:00Z",
  created_by_user_id: "user-1",
  name: "My project",
  description: "",
  system_prompt: "",
  is_published: false,
  chunking_strategy: "auto",
  parent_child_chunking: false,
  embedding_backend: null,
  embedding_model: "text-embedding-ada-002",
  embedding_api_key_credential_id: null,
  org_embedding_api_key_credential_id: null,
  llm_backend: null,
  llm_model: "gpt-4",
  llm_api_key_credential_id: null,
  org_llm_api_key_credential_id: null,
  retrieval_strategy: "hybrid",
  retrieval_top_k: 8,
  retrieval_min_score: 0.3,
  chat_history_window_size: 8,
  chat_history_max_chars: 4000,
  reranking_enabled: false,
  reranker_backend: null,
  reranker_model: null,
  reranker_candidate_multiplier: 3,
  restored_from_version: null,
  organization_id: null,
};

describe("SnapshotCard", () => {
  it("should display the version number", () => {
    renderWithProviders(
      <SnapshotCard snapshot={mockSnapshot} isCurrentVersion={false} onRestoreRequest={vi.fn()} />,
    );
    expect(screen.getByText("v3")).toBeInTheDocument();
  });

  it("should display the label", () => {
    renderWithProviders(
      <SnapshotCard snapshot={mockSnapshot} isCurrentVersion={false} onRestoreRequest={vi.fn()} />,
    );
    expect(screen.getByText("After big refactor")).toBeInTheDocument();
  });

  it("should show 'Current version' badge when isCurrentVersion is true", () => {
    renderWithProviders(
      <SnapshotCard snapshot={mockSnapshot} isCurrentVersion={true} onRestoreRequest={vi.fn()} />,
    );
    expect(screen.getByText("Current version")).toBeInTheDocument();
  });

  it("should disable restore button when isCurrentVersion is true", () => {
    renderWithProviders(
      <SnapshotCard snapshot={mockSnapshot} isCurrentVersion={true} onRestoreRequest={vi.fn()} />,
    );
    expect(screen.getByRole("button", { name: /restore/i })).toBeDisabled();
  });

  it("should call onRestoreRequest when restore button is clicked", async () => {
    const onRestoreRequest = vi.fn();
    const user = userEvent.setup();
    renderWithProviders(
      <SnapshotCard snapshot={mockSnapshot} isCurrentVersion={false} onRestoreRequest={onRestoreRequest} />,
    );
    await user.click(screen.getByRole("button", { name: /restore/i }));
    expect(onRestoreRequest).toHaveBeenCalledWith(mockSnapshot);
  });

  it("should display embedding model and llm model", () => {
    renderWithProviders(
      <SnapshotCard snapshot={mockSnapshot} isCurrentVersion={false} onRestoreRequest={vi.fn()} />,
    );
    expect(screen.getByText("text-embedding-ada-002")).toBeInTheDocument();
    expect(screen.getByText("gpt-4")).toBeInTheDocument();
  });

  it("should show restored_from badge when applicable", () => {
    const restoredSnapshot = { ...mockSnapshot, restored_from_version: 1 };
    renderWithProviders(
      <SnapshotCard snapshot={restoredSnapshot} isCurrentVersion={false} onRestoreRequest={vi.fn()} />,
    );
    expect(screen.getByText(/restored from v1/i)).toBeInTheDocument();
  });
});
