"use client";

import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { ChatPanel } from "@/components/organisms/chat/chat-panel";
import { renderWithProviders } from "../../../helpers/render";

class ResizeObserverMock {
  observe() {}
  unobserve() {}
  disconnect() {}
}
vi.stubGlobal("ResizeObserver", ResizeObserverMock);

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}));

const mockSendMessageResult = vi.hoisted(() => ({
  send: vi.fn(),
  cancel: vi.fn(),
  state: "idle" as "idle" | "sending" | "streaming",
  streamedContent: "",
  chunks: [] as never[],
  error: null as string | null,
}));

vi.mock("@/lib/hooks/use-chat", () => ({
  useMessages: () => ({
    data: [
      {
        id: "msg-user",
        conversation_id: "conv-1",
        role: "user",
        content: "Hello",
        created_at: "2026-01-01T00:00:00Z",
      },
      {
        id: "msg-assistant",
        conversation_id: "conv-1",
        role: "assistant",
        content: "Hi there",
        source_documents: [
          {
            document_id: "doc-1",
            document_file_name: "atelier-migration-24-11-2025.md",
            chunk_ids: ["chunk-aaa", "chunk-bbb"],
          },
          {
            document_id: "doc-1",
            document_file_name: "atelier-migration-24-11-2025.md",
            chunk_ids: ["chunk-aaa", "chunk-bbb"],
          },
        ],
        created_at: "2026-01-01T00:00:01Z",
      },
    ],
  }),
  useSendMessage: () => mockSendMessageResult,
}));

vi.mock("@/lib/hooks/use-auth", () => ({
  useAuth: () => ({ token: "token-1" }),
}));

const mockProjectData = vi.hoisted(() => ({
  reindex_status: "idle" as string,
  reindex_progress: 0,
  reindex_total: 0,
}));

vi.mock("@/lib/hooks/use-projects", () => ({
  useProject: () => ({ data: mockProjectData }),
}));

const getDocumentFileBlobMock = vi.fn();
vi.mock("@/lib/api/documents", () => ({
  getDocumentFileBlob: (...args: unknown[]) => getDocumentFileBlobMock(...args),
}));

describe("ChatPanel", () => {
  it("should display unique document source badge for assistant response", () => {
    renderWithProviders(<ChatPanel projectId="proj-1" conversationId="conv-1" />);
    expect(screen.getByText("atelier-migration-24-11-2025.md")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /show sources/i })).toBeNull();
  });

  it("should open document dialog when clicking a source badge", async () => {
    getDocumentFileBlobMock.mockResolvedValue(new Blob(["hello"], { type: "text/plain" }));
    const user = userEvent.setup();
    renderWithProviders(<ChatPanel projectId="proj-1" conversationId="conv-1" />);
    await user.click(screen.getByText("atelier-migration-24-11-2025.md"));
    expect(getDocumentFileBlobMock).toHaveBeenCalledWith("token-1", "proj-1", "doc-1");
    expect(screen.getByRole("heading", { name: "atelier-migration-24-11-2025.md" })).toBeInTheDocument();
  });

  it("should display chunk IDs in document dialog with copy buttons", async () => {
    getDocumentFileBlobMock.mockResolvedValue(new Blob(["hello"], { type: "text/plain" }));
    const user = userEvent.setup();
    renderWithProviders(<ChatPanel projectId="proj-1" conversationId="conv-1" />);
    await user.click(screen.getByText("atelier-migration-24-11-2025.md"));
    expect(screen.getByText("chunk-aaa")).toBeInTheDocument();
    expect(screen.getByText("chunk-bbb")).toBeInTheDocument();
    const chunkCopyButtons = screen
      .getAllByRole("button", { name: /copy/i })
      .filter((btn) => btn.getAttribute("title") === "Copy chunk ID");
    expect(chunkCopyButtons).toHaveLength(2);
  });

  it("should display stream error when state is idle", () => {
    mockSendMessageResult.error = "Stream connection failed";
    mockSendMessageResult.state = "idle";
    renderWithProviders(<ChatPanel projectId="proj-1" conversationId="conv-1" />);
    expect(screen.getByText("Stream connection failed")).toBeInTheDocument();
    mockSendMessageResult.error = null;
  });

  it("should show reindexing message when project is being reindexed", () => {
    mockProjectData.reindex_status = "in_progress";
    mockProjectData.reindex_progress = 3;
    mockProjectData.reindex_total = 10;
    renderWithProviders(<ChatPanel projectId="proj-1" conversationId="conv-1" />);
    expect(screen.getByText("Reindexing in progress (3/10). Chat is temporarily disabled.")).toBeInTheDocument();
    mockProjectData.reindex_status = "idle";
  });
});
