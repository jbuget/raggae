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
  embedding_model: "text-embedding-ada-002",
  llm_model: "gpt-4",
  retrieval_strategy: "hybrid",
  restored_from_version: null,
  created_at: "2026-01-15T10:30:00Z",
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
