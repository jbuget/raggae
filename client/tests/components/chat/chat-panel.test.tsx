import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { ChatPanel } from "@/components/chat/chat-panel";
import { renderWithProviders } from "../../helpers/render";

class ResizeObserverMock {
  observe() {}
  unobserve() {}
  disconnect() {}
}
vi.stubGlobal("ResizeObserver", ResizeObserverMock);

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
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
          },
          {
            document_id: "doc-1",
            document_file_name: "atelier-migration-24-11-2025.md",
          },
        ],
        created_at: "2026-01-01T00:00:01Z",
      },
    ],
  }),
  useSendMessage: () => ({
    send: vi.fn(),
    state: "idle",
    streamedContent: "",
    chunks: [],
  }),
}));

vi.mock("@/lib/hooks/use-auth", () => ({
  useAuth: () => ({
    token: "token-1",
  }),
}));

const getDocumentFileBlobMock = vi.fn();
vi.mock("@/lib/api/documents", () => ({
  getDocumentFileBlob: (...args: unknown[]) => getDocumentFileBlobMock(...args),
}));

describe("ChatPanel", () => {
  it("should display unique document source badge for assistant response", () => {
    renderWithProviders(
      <ChatPanel projectId="proj-1" conversationId="conv-1" />,
    );

    expect(screen.getByText("atelier-migration-24-11-2025.md")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /show sources/i })).toBeNull();
  });

  it("opens document popup when clicking source badge", async () => {
    getDocumentFileBlobMock.mockResolvedValue(
      new Blob(["hello"], { type: "text/plain" }),
    );
    const user = userEvent.setup();
    renderWithProviders(
      <ChatPanel projectId="proj-1" conversationId="conv-1" />,
    );

    await user.click(screen.getByText("atelier-migration-24-11-2025.md"));

    expect(getDocumentFileBlobMock).toHaveBeenCalledWith(
      "token-1",
      "proj-1",
      "doc-1",
    );
    expect(
      screen.getByRole("heading", { name: "atelier-migration-24-11-2025.md" }),
    ).toBeInTheDocument();
  });
});
